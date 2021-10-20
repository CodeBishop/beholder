import curses

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