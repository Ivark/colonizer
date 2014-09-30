from constants import *
import random

PERSON_DATA = 0
TILE_POS = 1
TILE_DATA = 2
TILE_SECTION = [TILE_POS, TILE_DATA]

LOOK_FOR_RESOURCE = 0
GO_TO_RESOURCE = 1
PICK_UP_RESOURCE = 2
PUT_DOWN_RESOURCE = 3
DO_NOTHING = 4

ai_name = "boring"

class Bounds:
    def __init__(self, minX = 0, minY = 0, maxX = 0, maxY = 0):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY
        
class Tile:
    def __init__(self):
        self.isWall = False
        self.hasPerson = False
        self.hasResources = 0
    
    def update(self, x, y, levelBounds, tileData):
        if x < levelBounds.minX: levelBounds.minX = x
        elif x > levelBounds.maxX: levelBounds.maxX = x
        if y < levelBounds.minY: levelBounds.minY = y
        elif y > levelBounds.maxY: levelBounds.maxY = y
        
        self.isWall = tileData >> 5
        self.hasPerson = (tileData >> 4) % 2
        self.hasResources = tileData % 16


def think(inputData, memory):
    
    #Initiate memory
    
    if not memory or "initiated" not in memory:
        memory = {
            "initiated": True,
            
            "pos": (0, 0),
            "lastIntention": WAIT,
            "level": {},
            "levelBounds": Bounds(),
            "state": LOOK_FOR_RESOURCE,
            "stateData": {}
        }
    
    #Import memory
    
    pos = memory["pos"]
    lastIntention = memory["lastIntention"]
    level = memory["level"]
    levelBounds = memory["levelBounds"]
    state = memory["state"]
    stateData = memory["stateData"]
    
    #Enterpret input
    
    lastAction = WAIT
    isCarrying = False
    tileResources = 0
    
    byteState = PERSON_DATA
    for i in range(2, len(inputData), 2):
        byte = int(inputData[i] + inputData[i+1], 16)
        if byte == 0x88:
            if byteState is PERSON_DATA:
                byteState = TILE_POS
                continue
            else: break
        if byteState is PERSON_DATA:
            personData = byte
            lastAction = personData >> 1
            isCarrying = personData % 0b10
            
            pos = (pos[0] + (lastAction is RIGHT) - (lastAction is LEFT), pos[1] + (lastAction is DOWN) - (lastAction is UP))
        elif byteState is TILE_POS:
            tilePos = byte
            byteState = TILE_DATA
        elif byteState is TILE_DATA:
            tileData = byte
            byteState = TILE_POS
            
            x = ((tilePos >> 4) + 8) % 16 - 8 + pos[0]
            y = ((tilePos % 0b10000) + 8) % 16 - 8 + pos[1]
            if (x, y) not in level: level[x, y] = Tile()
            level[x, y].update(x, y, levelBounds, tileData)
            
            if tilePos == 0x00:
                tileResources = tileData % 0b10000
    
    
    #Print map from memory and visual input
    
    memoryLevel = ""
    for y in range(levelBounds.minY-1, levelBounds.maxY+2):
        for x in range(levelBounds.minX-1, levelBounds.maxX+2):
            if (x, y) == pos:
                if isCarrying: c = '+'
                else: c = '!'
            elif (x, y) in level:
                tile = level[x, y]
                if tile.isWall: c = 'W'
                elif tile.hasPerson: c = 'O'
                elif tile.hasResources: c = '#'
                else: c = '_'
            else:
                c = '?'
            memoryLevel += c
        memoryLevel += '\n'
    print(memoryLevel)

    
    
    
    
    #Figure out what to do
    
    (intention, state, stateData) = decideWhatToDo(pos, level, state, stateData, isCarrying)
    
    
    #Put memories back
    
    memory["pos"] = pos
    memory["lastIntention"] = intention
    memory["level"] = level
    memory["levelBounds"] = levelBounds
    memory["state"] = state
    memory["stateData"] = stateData
    return intention, "", memory

def decideWhatToDo(pos, level, state, stateData, isCarrying):
    intention = WAIT
    
    if state is LOOK_FOR_RESOURCE:
        maxResources = 0
        resourcePos = pos
        resourceDist = 0
        
        for (tilePos, tile) in level.items():
            if tile.hasResources > maxResources:
                maxResources = tile.hasResources
                resourcePos = tilePos
                resourceDist = abs(tilePos[0]-pos[0]) + abs(tilePos[1]-pos[1])
            elif tile.hasResources == maxResources and abs(tilePos[0]-pos[0]) + abs(tilePos[1]-pos[1]) < resourceDist:
                resourcePos = tilePos
                resourceDist = abs(tilePos[0]-pos[0]) + abs(tilePos[1]-pos[1])
        
        if maxResources > 0:
            state = GO_TO_RESOURCE
            stateData["resourcePos"] = resourcePos
            return decideWhatToDo(pos, level, state, stateData, isCarrying)
        else:
            intention = random.choice(MOVE)
        
    elif state is GO_TO_RESOURCE:
        if "resourcePos" not in stateData:
            state = LOOK_FOR_RESOURCE
            return decideWhatToDo(pos, level, state, stateData, isCarrying)
        resourcePos = stateData["resourcePos"]
        
        moveX = resourcePos[0] - pos[0]
        moveY = resourcePos[1] - pos[1]
        
        if moveX == 0 and moveY == 0:
            state = PICK_UP_RESOURCE*(not isCarrying) + PUT_DOWN_RESOURCE*isCarrying
            return decideWhatToDo(pos, level, state, stateData, isCarrying)
        elif abs(moveX) > abs(moveY) or (abs(moveX) == abs(moveY) and random.choice([0, 1])):
            intention = RIGHT*(moveX > 0) + LEFT*(moveX < 0)
        else:
            intention = DOWN*(moveY > 0) + UP*(moveY < 0)
    elif state is PICK_UP_RESOURCE:
        state = LOOK_FOR_RESOURCE
        intention = PICKUP
    elif state is PUT_DOWN_RESOURCE:
        state = DO_NOTHING
        intention = PUTDOWN
        
        
    return intention, state, stateData