'''
EXAMPLE USAGE:
    slowCommand = AsyncCommand("ping -c 2 python.org")
    while not slowCommand.isFinished():
        print(".", end = "", flush = True)
        sleep(0.1)
    print("\nstdout\n" + slowCommand.out + "\n")
    print("stderr\n" + slowCommand.err + "\n")
    print("returnCode: " + str(slowCommand.returnCode) + "\n")
'''

import subprocess
from time import sleep

# A class running a CLI command in the background
class AsyncCommand:
    # Create the command and, optionally, start it
    def __init__(self, command, executeNow=True):
        self.command = command.split()
        self._isFinished = False
        self._isStarted = False
        self.out = ""
        self.err = ""
        self.returnCode = None
        if executeNow:
            self.run()

    # Start or restart the command
    def run(self, command = None):
        self._isStarted = True
        self._isFinished = False
        if command is not None:
            self.command = command.split()
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the command has finished and save the result if it has
    def isFinished(self):
        if not self._isStarted:
            raise Exception("AsyncCommand.isFinished() called before AsyncCommand.run()")
        if not self._isFinished:
            self.returnCode = self.process.poll()
            if self.returnCode is not None:
                self._isFinished = True
                tempOut, tempErr = self.process.communicate()
                self.out = tempOut.decode("utf-8")
                self.err = tempErr.decode("utf-8")
        return self._isFinished
