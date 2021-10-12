import io
import time
import subprocess

# command = "ls"
command = 'adb shell dumpsys activity services'

p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

# Wait until process terminates
while p.poll() is None:
    time.sleep(0.5)

for line in io.TextIOWrapper(p.stdout, encoding="utf-8"):  # or another encoding
    print(line.rstrip())

# It's done
print("Process ended, ret code:", p.returncode)