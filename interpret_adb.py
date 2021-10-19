def interpretProcessInfo(commandOutput, appId):
    processDict = interpretProcessInfoIntoDict(commandOutput, appId)
    if processDict != None:
        return "PID: " + processDict['pid'] + "   runTime: " + processDict['runTime'] + "   Command: " + processDict['cmd']
    return None

def interpretProcessInfoIntoDict(commandOutput, appId):
    processDict = {}
    for line in commandOutput.split('\n'):
        if line.find(appId) != -1:
            values = [s for s in line.split()]
            processDict['pid'] = values[3]
            processDict['runTime'] = values[12]
            processDict['cmd'] = values[13]
            return processDict
    return None
    return "Process not found for " + appId

def interpretActivityInfo(commandOutput, appId):
    return "hello"

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
