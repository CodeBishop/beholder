import sys
import time
from subprocess import PIPE, Popen
from threading  import Thread

from queue import Queue, Empty

ON_POSIX = 'posix' in sys.builtin_module_names

[PENDING, RUNNING, STOPPED] = range(3) # Command state enum

class AsyncCommand:
    def __init__(self, command, executeNow=True):
        self.command = command.split()
        self.state = PENDING
        self.proc = Popen(self.command, stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
        self.queue = Queue()
        self.result = ""
        self.cmdThread = Thread(target=self.enqueue_output, args=(self.proc.stdout, self.queue))
        self.cmdThread.daemon = True # thread dies with the program
        self.cmdThread.start()

        while self.state != STOPPED:
            # read line without blocking
            try:
                line = self.queue.get_nowait() # or q.get(timeout=.1)
            except Empty:
                if self.state == RUNNING:
                    self.state = STOPPED
                    print("Command has stopped")
                else:
                    time.sleep(0.1)
            else: # got line
                if self.state == PENDING:
                    self.state = RUNNING
                    print("Command has started returning results")
                self.result += line.decode('utf-8')

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def isFinished(self):
        return self.state == STOPPED

    def getResult(self):
        return self.result

servicesExec = AsyncCommand('adb shell dumpsys activity services')

while(servicesExec.isFinished == False):
    time.sleep(0.2)

# print(servicesExec.getResult())
