import math
from sys import stdout

def pad(numString, length):
    prefix = numString[:2]
    cleanNumString = numString[2:]
    origLength = len(cleanNumString)
    paddedNumString = cleanNumString.zfill(origLength + (-origLength % length))
    return prefix + paddedNumString

def padHex(integer, length=2):
    return pad(hex(integer), length)
    
def padBin(integer, length=8):
    return pad(bin(integer), length)

def removePrefix(numString, length=2):
    return numString[length:]

def listHex(integers):
    return "0x" + "".join(map(removePrefix, map(padHex, integers)))

def listBin(integers):
    return "0b" + "".join(map(removePrefix, map(padBin, integers)))

def write(writeObject = "", newLine = True, indent = -1):
    global writeList, writeIndent
    if 'writeList' not in globals(): writeList = []
    if 'writeIndent' not in globals(): setWriteIndent(0)
    
    if not (0 <= indent <= 8): indent = writeIndent
    
    writeList.append((str(writeObject), newLine, indent))
    
def writeAll():
    global writeList
    if 'writeList' not in globals() or len(writeList) == 0: return
    lines = [('', 0)]
    result = ''
    i = 0
    for (writeString, newLine, indent) in writeList:
        linesInString = writeString.split('\n')
        lines[i] = (lines[i][0] + linesInString[0], indent)
        for j in range(1, len(linesInString)):
            i += 1
            lines.append((linesInString[j], indent))
        if newLine:
            i += 1
            lines.append(('', indent))
    for (line, indent) in lines:
        line = ' ' + line
        for j in range(indent):
            line = '>' + line
        result += line + '\n'
    stdout.write(result)
    writeList = []
    
def setWriteIndent(indent):
    global writeIndent
    writeIndent = indent