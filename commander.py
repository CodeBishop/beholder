from subprocess import PIPE, Popen
import sys
import time

ON_POSIX = 'posix' in sys.builtin_module_names # TODO: Does this actually make it run on Windows? or is it just garbage you can remove?

command = 'adb shell dumpsys activity services'
# command = 'echo hi'

p = Popen(command.split(' '), stdout=PIPE)
# p = subprocess.Popen(["sleep",  "4"], shell=True)

# Wait until process terminates
while p.poll() is None:
    time.sleep(0.5)

# Fetch out the command results
(stdout, stderr) = p.communicate()

# It's done
print(stdout)
print("\nProcess ended, ret code:", p.returncode)




# from queue import Queue, Empty

# ON_POSIX = 'posix' in sys.builtin_module_names

# def enqueue_output(out, queue):
#     for line in iter(out.readline, b''):
#         queue.put(line)
#     print("EOF")
#     out.close()

# command = 'adb shell dumpsys activity services'
# p = Popen(command.split(' '), stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
# q = Queue()
# cmdThread = Thread(target=enqueue_output, args=(p.stdout, q))
# cmdThread.daemon = True # thread dies with the program
# cmdThread.start()

# print("doing other things")

# for i in range(20):
#     # read line without blocking
#     try:  line = q.get_nowait() # or q.get(timeout=.1)
#     except Empty:
#         print('no output yet')
#     else: # got line
#         print(line)
#     print('.')

#     time.sleep(0.1)