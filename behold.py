#!/usr/bin/python3

# MIT License

# Copyright (c) 2021 Scott Bishop

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
INSTALLATION
cd beholder
sudo ln -s ~+/behold.py /usr/local/bin/behold

USAGE
behold <package-name>

'''

import sys
import time
from interpret_adb import *
from curses_utils import *
from async_command import AsyncCommand

PROGRAM_TITLE = "Beholder"

############################################################################################
#   Main   #################################################################################
############################################################################################

def cursesMain(screen):
    screen.nodelay(True)  # Make getch() non-blocking
    initCursesUtils(screen)  # Connect curses to the utility function library

    curses.curs_set(0) # Hide the cursor

    processCmd = AsyncCommand('adb shell ps -wel')
    activityCmd = AsyncCommand('adb shell dumpsys activity ' + appId)
    servicesCmd = AsyncCommand('adb shell dumpsys activity services')

    processInfo = ""
    activityInfo = ""
    serviceList = ""
    exitFlag = False
    while not exitFlag:
        # Update info
        if processCmd.isFinished():
            newProcessInfo = processCmd.out
            processInfo = newProcessInfo
            processCmd.run() # Start the next run
        if activityCmd.isFinished():
            activityInfo = activityCmd.out
            processCmd.run() # Start the next run
        if servicesCmd.isFinished():
            serviceList = servicesCmd.out
            processCmd.run() # Start the next run

        # Clear the screen
        screen.erase()
        screen.border(0)

        # Draw the view
        printAt(3, 0, ' ' + BLUE + PROGRAM_TITLE + ' - ' + appId + ' ')
        printAt(2, 2, 'Process: ' + processInfo)
        printAt(2, 3, 'Services: [ ' + ', '.join(serviceList) + ' ]')
        printAt(2, 4, 'Activity: ' + activityInfo)

        screen.refresh() # Update the view

        # Check for and handle keypresses
        keypress = screen.getch()
        if keypress in [ord('q'), ord('Q')]:
            exitFlag = True

        time.sleep(0.5)  # Sleep for this many seconds to reduce CPU load

############################################################################################
#   Start of Program    ####################################################################
############################################################################################
appId = ""
appIdSearchString = ""

if (len(sys.argv) < 2):
    print("Usage: behold <package-name-pattern>")
else:
    appIdSearchString = sys.argv[1]

# Get full package name and confirm that only one package name matches
packageListCmd = AsyncCommand('adb shell pm list packages')
timeoutAfterTries = 5
tries = 0
exitFlag = False
while not exitFlag:
    # When the package list has loaded, get the package name
    if packageListCmd.isFinished():
        packageList = packageListCmd.out.split()
        matchingPackages = [packageEntry for packageEntry in packageList if appIdSearchString in packageEntry]

        # Ensure that exactly one package name matches the pattern given by the user
        if len(matchingPackages) == 1:
            # Extract the package name from the package entry. The package entry is of the form: package:com.example.app
            appId = re.findall(r'([a-zA-Z.]*\.+[a-zA-Z]*)', matchingPackages[0])[0]
        elif len(matchingPackages) > 1:
            print("More than one package matches the pattern: " + appIdSearchString)
            for matchingPackage in matchingPackages:
                print(re.findall(r'([a-zA-Z.]*\.+[a-zA-Z]*)', matchingPackage))
            sys.exit(1)
        else:
            print("No packages match the given pattern.")
            sys.exit(1)
        exitFlag = True
    else:
        tries += 1
        if tries >= timeoutAfterTries:
            print("Timed out while waiting for package manager response")
            sys.exit(1)
        else:
            time.sleep(0.1)  # Sleep for this many seconds before checking again

curses.wrapper(cursesMain)
