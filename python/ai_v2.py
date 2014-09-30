from constants import *
from tools import padHex, padBin, write
import random

DO_NOTHING = 0
INTRODUCTIONS = 1
DISTRIBUTE_ROLES = 2
RECEIVE_ROLE = 3
MOVE_AROUND = 4

NONE = 0
CHIEF = 1000
GATHERER = 1001
SCOUT = 1002

ROLES = [NONE, CHIEF, GATHERER, SCOUT]

ROLE_NAMES = {
    NONE: "No role",
    CHIEF: "Chief",
    GATHERER: "Gatherer",
    SCOUT: "Scout"
}

ai_name = "teamwork"
        
class Tile:
    def __init__(self, wall = False, person = False, resources = 0):
        self.wall = wall
        self.person = person
        self.resources = resources

class Chart:
    def __init__(self):
        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0
        self.tiles = {}
    
    def hasTile(self, x, y):
        return (x, y) in self.tiles
    
    def update(self, tiles, offX, offY):
        for ((relX, relY), tile) in tiles.items():
            x = relX + offX
            y = relY + offY
            self.tiles[x, y] = tile
            self.minX = min(self.minX, x)
            self.minY = min(self.minY, y)
            self.maxX = max(self.maxX, x)
            self.maxY = max(self.maxY, y)
    
    def __str__(self):
        global m
        string = ""
        for y in range(self.minY-1, self.maxY+2):
            for x in range(self.minX-1, self.maxX+2):
                if (x, y) == (m.x, m.y):
                    c = '!'
                elif (x, y) in self.tiles:
                    tile = self.tiles[x, y]
                    if tile.wall: c = 'W'
                    elif tile.person: c = 'O'
                    elif tile.resources: c = '#'
                    else: c = '_'
                else:
                    c = '?'
                string += c
            string += '\n'
        return string
    

class Memory:
    def __init__(self):
        self.me = Person(padHex(hash(random.randint(0, 256**8)%0xFFFFFF)))
        self.x = 0
        self.y = 0
        self.lastIntention = WAIT
        self.chart = Chart()
        self.team = {}
        self.state = INTRODUCTIONS
        self.stateData = {}
    
    @staticmethod
    def load(memory):
        if not memory: m = Memory()
        else: m = memory
        return m

class Input:
    @staticmethod
    def split(inputData):
        data = [""]
        inputBytes = [(inputData[i:i+2]) for i in range(2, len(inputData), 2)]
        for byte in inputBytes:
            if byte == "88":
                data.append("")
            else:
                data[len(data)-1] += byte
        return data
    
    @staticmethod
    def hexToBytes(hexData, prefix = False):
        return [int(hexData[i:i+2], 16) for i in range(2*prefix, len(hexData), 2)]
        
    @staticmethod
    def parseMe(meBytes):
        lastAction = meBytes[0] >> 1
        isCarrying = meBytes[0] % 2
        return lastAction, isCarrying
        #return meBytes[0] >> 1, meBytes[0] % 2
        
    @staticmethod
    def parseTiles(tileBytes):
        level = {}
        tiles = [(tileBytes[i:i+2]) for i in range(0, len(tileBytes), 2)]
        for tile in tiles:
            print(*map(padHex, tile))
            x = ((tile[0] >> 4) + 8) % 16 - 8
            y = ((tile[0] % 16) + 8) % 16 - 8
            level[x, y] = Tile(tile[1] >> 5, (tile[1] >> 4) % 2, tile[1] % 16)
        return level
        #return {(((tileBytes[i]>>4)+8)%16-8,((tileBytes[i]%16)+8)%16-8):Tile(tileBytes[i+1]>>5,(tileBytes[i+1]>>4)%2,tileBytes[i+1]%16) for i in range(0, len(tileBytes), 2)}
        
    @staticmethod
    def parseBC(bcBytes):
        messages = {}
        pos = (0, 0)
        newMessage = True
        for byte in bcBytes:
            if byte == 0x80:
                newMessage = True
            elif newMessage:
                x = ((byte >> 4) + 8) % 16 - 8
                y = ((byte % 16) + 8) % 16 - 8
                pos = (x, y)
                messages[pos] = ""
                newMessage = False
            else:
                messages[pos] += chr(byte)
        return messages
    
class Person:
    def __init__(self, name, role=NONE):
        self.name = name
        self.role = role
    
def think(inputData, memory):
    global m
    
    #Load memory
    m = Memory.load(memory)
    
    #Enterpret input
    #print(m.me.name + ": " + inputData)
    
    (meBytes, tileBytes, bcBytes) = [Input.hexToBytes(hexData) for hexData in Input.split(inputData)][:3]
    (lastAction, isCarrying) = Input.parseMe(meBytes)
    tiles = Input.parseTiles(tileBytes)
    broadcasts = Input.parseBC(bcBytes)
    
    m.x += (lastAction is RIGHT) - (lastAction is LEFT)
    m.y += (lastAction is DOWN) - (lastAction is UP)
    m.chart.update(tiles, m.x, m.y)
    

    
    
    #Figure out what to do
    def whatToDo():
        def lookupBCs(broadcasts, topic=""):
            return {bc[0]: bc[1] for bc in [bc2.split("|%s" % topic) for bc2 in broadcasts.values() if bc2.find("|%s" % topic) >= 0]}
        def formatBC(message, topic=""):
            return "%s%s" % (topic, message)
        
        def doIntroductions():
            m.state = DISTRIBUTE_ROLES
            rank = random.randint(0, 999)
            m.stateData["rank"] = rank
            return BROADCAST, formatBC(str(rank), "RANK")
        doIntroductions.val = INTRODUCTIONS
        
        def doDistributeRoles():
            ranks = list(map(int, lookupBCs(broadcasts, "RANK").values()))
            if(max(ranks) != m.stateData["rank"]):
                m.state = RECEIVE_ROLE
                return whatToDo()
            if(ranks.count(max(ranks)) > 1):
                m.state = INTRODUCTIONS
                return whatToDo()
            
            names = list(lookupBCs(broadcasts).keys())
            for name in names:
                member = Person(name)
                if(names.index(name) < len(names)/2): member.role = SCOUT
                else: member.role = GATHERER
                m.team[name] = member
            m.me.role = CHIEF
            m.team[m.me.name] = m.me
            broadcast = "&".join(["%s=%d" % (p.name, p.role) for p in m.team.values() if p is not m.me])
            
            m.state = MOVE_AROUND
            return BROADCAST, formatBC(broadcast, "ROLES")
        doDistributeRoles.val = DISTRIBUTE_ROLES
        
        def doReceiveRole():
            membersList = list(lookupBCs(broadcasts, "ROLES").values())
            if len(membersList) == 1:
                members = membersList[0].split('&')
                for member in members:
                    (name, roleStr) = member.split('=')
                    m.team[name] = Person(name, int(roleStr))
                
                if(m.me.name in m.team):
                    m.me = m.team[m.me.name]
                    m.state = MOVE_AROUND
                    return whatToDo()
            
            return BROADCAST, "Hey!"
        doReceiveRole.val = RECEIVE_ROLE
        
        def doMoveAround():
            return random.choice(MOVE), ""
        doMoveAround.val = MOVE_AROUND
        
        doState = {func.val: func for func in [
                doIntroductions,
                doDistributeRoles,
                doReceiveRole,
                doMoveAround
            ]}
        
        if m.state in doState: return doState[m.state]()
        else: return WAIT, ""
    
    
    (intention, broadcast) = whatToDo()
    write("NAME: " + m.me.name)
    write("ROLE: " + ROLE_NAMES[m.me.role])
    write(m.chart)
    return intention, "%s|%s" % (m.me.name, broadcast), m
    
