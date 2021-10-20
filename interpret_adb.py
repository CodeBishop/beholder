import re

def interpretProcessInfo(commandOutput, appId):
    '''Takes in the output of a `ps -wel` and a process name, returns a string describing that process or None if the process was not found'''
    processDict = interpretProcessInfoIntoDict(commandOutput, appId)
    if processDict != None:
        return processDict['cmd'] + " (pid " + processDict['pid'] + ")   " + processDict['runTime'] + "   Nice: " + processDict['nice']
    return None

def interpretProcessInfoIntoDict(commandOutput, appId):
    '''Takes in the output of a `ps -wel` and a process name, returns a dictionary of info about that process or None if the process was not found'''
    processDict = {}
    for line in commandOutput.split('\n'):
        if line.find(appId) != -1:
            values = [s for s in line.split()]
            processDict['pid'] = values[3]
            processDict['nice'] = values[7]
            processDict['runTime'] = values[12]
            processDict['cmd'] = values[13]
            return processDict
    return None

def interpretActivityInfo(commandOutput, appId):
    '''Takes in the output of a `dumpsys activity <appId>` and an application ID, returns a string describing that app's Activity'''
    activityDict = {}
    for line in commandOutput.split('\n'):
        if 'ACTIVITY' in line:
            activityDict['activityName'] = line.split()[1]
            activityDict['pidInfo'] = line.split()[3]
        if 'mResumed' in line:
            flagEntries = line.split()
            activityDict['resumedFlag'] = 'true' in flagEntries[0]
            activityDict['stoppedFlag'] = 'true' in flagEntries[1]
            activityDict['finishedFlag'] = 'true' in flagEntries[2]
        if 'mLastFrameTime' in line:
            activityDict['timeSinceLastRender'] = re.search(r"\b.*(\b\d+) ms ago\)", line).group(1)
    if activityDict != {}:
        activityString = ""
        activityString += activityDict['activityName'] + " (" + activityDict['pidInfo'] + ")"
        if 'timeSinceLastRender' in activityDict.keys() and activityDict['timeSinceLastRender'] != None:
            activityString += "   updated " + activityDict['timeSinceLastRender'] + " ms ago"
        activityString += "   state: "
        if 'resumedFlag' in activityDict.keys() and activityDict['resumedFlag']:
            activityString += "foreground  "
        if 'stoppedFlag' in activityDict.keys() and activityDict['stoppedFlag']:
            activityString += "stopped  "
        if 'finishedFlag' in activityDict.keys() and activityDict['finishedFlag']:
            activityString += "finished  "
        return activityString
    return ""

    '''Replaces this command:
            hero deaths % watch -n 0.3 'adb shell dumpsys activity <appId> | grep -E "mResumed|astFrameT|hasService|ebView|CTIVITY"'
    '''
    return "hello"

def interpretRunningServiceList(commandOutput, appId):
    '''Takes in the output of a `dumpsys activity services <appId>` and an application ID, returns a list of strings naming all the Android services that app is running'''
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
