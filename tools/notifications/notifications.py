#!/usr/bin/python3

'''
Things you should pull from NotificationRecord
    numEnqueuedByApp  <-- one of these is the grand total

Things you should pull from the `AppSettings <package-name>` object
    NotificationChannel names

'''

from subprocess import check_output, CalledProcessError

from tempfile import TemporaryFile

def __getout(*args):
    with TemporaryFile() as t:
        try:
            out = check_output(args, stderr=t)
            return  0, out
        except CalledProcessError as e:
            t.seek(0)
            return e.returncode, t.read()

# cmd is string, split with blank
def getout(cmd):
    cmd = str(cmd)
    args = cmd.split(' ')
    return __getout(*args)

(returnCode, out) = getout('adb shell dumpsys notification --noredact')
lines = str(out, encoding='utf-8').split('\n')

# Add logic in here to parse NotificationRecord entries
for line in lines:
    print(line)
print ('Return code: ' + str(returnCode))
