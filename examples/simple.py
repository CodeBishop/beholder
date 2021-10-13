import io
import time
import subprocess

command = 'adb shell dumpsys activity services'
proc = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE)

# Wait until process terminates
buffer = ""
while proc.poll() is None:
    time.sleep(0.1)
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):#proc.stdout.readlines():
        buffer += line
    print( ".")

for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
    print(line.rstrip())
