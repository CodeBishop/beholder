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

# TODO: Fix the printAt() function. It skips printing if the line is longer than the window.

import json
import subprocess
import sys
import time
from interpret_adb import *
from curses_utils import *
from async_command import AsyncCommand

PROGRAM_TITLE = "Beholder"

############################################################################################
#   Helper Functions   #####################################################################
############################################################################################

# Get the output from a terminal command and block any error messages from appearing.
def terminalCommand(command):
    output, _ = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=DEVNULL).communicate()
    return output


############################################################################################
#   Main   #################################################################################
############################################################################################

def cursesMain(screen):
    screen.nodelay(True)  # Make getch() non-blocking
    initCursesUtils(screen)  # Connect curses to the utility function library

    curses.curs_set(0) # Hide the cursor

    processExec = AsyncCommand('adb shell ps -wel')
    activityExec = AsyncCommand('adb shell dumpsys activity ' + appId)
    servicesExec = AsyncCommand('adb shell dumpsys activity services')

    processInfo = ""
    activityInfo = ""
    serviceList = ""
    exitFlag = False
    while not exitFlag:
        # Update info
        if processExec.isStopped():
            processExec.run()
            # Don't overwrite processInfo until it's confirmed that it was found  TODO: Find out why it's sometimes not found. Is `ps -wel` failing half the time?
            newProcessInfo = interpretProcessInfo(processExec.getResult(), appId)
            if newProcessInfo != None:
                processInfo = newProcessInfo
        if activityExec.isStopped():
            activityExec.run()
            activityInfo = interpretActivityInfo(activityExec.getResult(), appId)
        if servicesExec.isStopped():
            servicesExec.run()
            serviceList = interpretRunningServiceList(servicesExec.getResult(), appId)

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

if (len(sys.argv) < 2):
    print("Usage: behold <package-name>")
else:
    appId = sys.argv[1]

# TODO: Make this conditional on valid CLI args
curses.wrapper(cursesMain)
