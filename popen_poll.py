import time
import subprocess

# command = "sleep 4"
command = 'adb shell dumpsys activity services'

p = subprocess.Popen(command.split(), shell=True)

# Wait until process terminates
while p.poll() is None:
    time.sleep(0.5)

# It's done
print("Process ended, ret code:", p.returncode)