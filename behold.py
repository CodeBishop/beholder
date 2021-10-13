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
behold <package name>

'''

import curses
import subprocess
import sys
import time
from async_command import AsyncCommand

############################################################################################
#   read_adb.py   ##########################################################################
############################################################################################
# TODO: Delete this function?
def getRunningServiceList(appId):
    # Execute command and get results into array of strings
    command = 'adb shell dumpsys activity services'
    process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output = process.stdout.readlines()

    # Strip out newlines
    for i in range(len(output)):
        output[i] = output[i].strip()

    # Filter out everything but the active ServiceRecords for the specified app
    filteredOutput = []
    for line in output:
        if '* ServiceRecord' in line and appId in line:
            filteredOutput.append(line)

    # Strip the ServiceRecord lines down to just the last part of the Service identifier
    serviceNames = []
    for line in filteredOutput:
        # Take last part of Service identifier and truncate final char (should be a close brace)
        # TODO: Rewrite this as a regex
        serviceNames.append(line.split('.')[-1][:-1])

    return serviceNames

def interpretRunningServiceList(commandOutput, appId):
    output = commandOutput.split('\n')
    # Strip out newlines
    for i in range(len(output)):
        output[i] = output[i].strip()

    # Filter out everything but the active ServiceRecords for the specified app
    filteredOutput = []
    for line in output:
        if '* ServiceRecord' in line and appId in line:
            filteredOutput.append(line)

    # Strip the ServiceRecord lines down to just the last part of the Service identifier
    serviceNames = []
    for line in filteredOutput:
        # Take last part of Service identifier and truncate final char (should be a close brace)
        # TODO: Rewrite this as a regex
        serviceNames.append(line.split('.')[-1][:-1])

    return serviceNames

# Get the output from a terminal command and block any error messages from appearing.
def terminalCommand(command):
    output, _ = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=DEVNULL).communicate()
    return output


############################################################################################
#   curses_utils.py   ######################################################################
############################################################################################
CEC = "%%%"  # Escape code for colored or special text
CECLEN = 1  # Number of chars after a color escape code

RED = CEC + "1"
GREEN = CEC + "2"
YELLOW = CEC + "3"
BLUE = CEC + "4"
MAGENTA = CEC + "5"
CYAN = CEC + "6"
REVERSE = CEC + "r"

# Subset of screen in which utils functions will print
utilsWindow = None

# Determine string length after removing embedded color codes
def CECStringLength(text):
    return len(text) - text.count(CEC) * (len(CEC) + CECLEN)

# Set area in which utils functions will print
def setPrintWindow(activeWindow):
    global utilsWindow
    utilsWindow = activeWindow

# Initialize curses utils library
def initCursesUtils(activeWindow):
    setPrintWindow(activeWindow)

    # Prepare color pairs.
    for i in range(1, 8):
        curses.init_pair(i, i, 0)

# If a CECString is longer than maxLength then cut it back and append ellipsis
def cutToEllipsis(text, maxLength):
    if CECStringLength(text) > maxLength:
        ellipsis = ".."
        newText = ""
        newLength = 0
        i = 0
        while newLength < maxLength - len(ellipsis):
            # If next part of string is a CEC code then append it but don't count it
            if text[i:i+len(CEC)] == CEC:
                newText += text[i:i+len(CEC) + CECLEN]
                i += len(CEC) + CECLEN
            # Else it's a normal character and just append it
            else:
                newText += text[i]
                i += 1
                newLength += 1
        # Return excess string with an ellipsis tacked on at the end
        return newText + ellipsis
    # If the given string didn't exceed the max length then return it as-is
    else:
        return text

# Print
def printAt(x, y, text, length=-1):
    # Get current window dimensions and clip them for border
    windowHeight, windowWidth = utilsWindow.getmaxyx()

    # Clip the supposed window dimensions on the assumption that the window has a border
    windowHeight, windowWidth = windowHeight - 1, windowWidth - 1

    # If text position is outside of window then don't draw it
    if x < 0 or y < 0 or x >= windowWidth or y >= windowHeight:
        return

    # If the string won't fit on screen then don't draw it
    if x + CECStringLength(text) >= windowWidth:
        return

    # If string needs to fit a given length then cut it
    if length > -1:
        text = cutToEllipsis(text, length)

    # Split the string by color-escape codes into a list of string portions
    strings = text.split(CEC)

    # Draw first portion of string in plain color
    utilsWindow.addstr(y, x, strings[0], curses.A_BOLD)
    x += len(strings[0])

    # Reverse color flag
    reverseFlag = 0
    colorCode = 0

    # Draw all subsequent string portions based on their first character (which should be their CEC value)
    for i in range(1, len(strings)):
        if len(strings[i]) >= CECLEN:
            colorCodeChar = strings[i][0:CECLEN]
            if colorCodeChar in "01234567":
                colorCode = curses.color_pair(int(colorCodeChar))
            elif colorCodeChar == 'r':
                if reverseFlag == 0:
                    reverseFlag = curses.A_REVERSE
                else:
                    reverseFlag = 0

            cursesCode = colorCode | curses.A_BOLD | reverseFlag
            utilsWindow.addstr(y, x, strings[i][1:], cursesCode)
        x += len(strings[i]) - CECLEN


############################################################################################
#   Main   #################################################################################
############################################################################################
PROGRAM_TITLE = "Beholder"
def cursesMain(screen):
    screen.nodelay(True)  # Make getch() non-blocking
    initCursesUtils(screen)  # Connect curses to the utility function library

    curses.curs_set(0) # Hide the cursor

    servicesExec = AsyncCommand('adb shell dumpsys activity services')

    exitFlag = False
    while not exitFlag:
        # Clear the screen
        screen.erase()
        screen.border(0)

        # Draw the view
        printAt(3, 0, ' ' + BLUE + PROGRAM_TITLE + ' - ' + appId + ' ')
        serviceList = interpretRunningServiceList(servicesExec.getResult(), appId)
        printAt(2, 2, 'Services: [' + ', '.join(serviceList) + ']')
        # if servicesExec.isStopped():
        #     servicesExec.run()

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
