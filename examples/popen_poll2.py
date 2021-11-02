import subprocess

process = subprocess.Popen(['ping', '-c 4', 'python.org'],
                           stdout=subprocess.PIPE,
                           universal_newlines=True)

while True:
    output = process.stdout.readline()
    print(output.strip())
    # Do something else
    return_code = process.poll()
    if return_code is not None:
        # Process has finished, read rest of the output
        print('RETURN CODE', return_code)
        for output in process.stdout.readlines():
            print(output.strip())
        break