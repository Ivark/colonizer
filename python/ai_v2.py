from constants import *
from tools import padHex, padBin, write
import random
from math import sqrt

DO_NOTHING = 0000
INTRODUCTIONS = 1001
DISTRIBUTE_ROLES = 1002
RECEIVE_ROLE = 1003
MOVE_AROUND = 1004
CREATE_PLAN = 1005
FOLLOW_THE_PLAN = 1006

PLAN_CHIEFING = 1100
PLAN_GATHERING = 1200
PLAN_SCOUTING = 1300

NONE = 0000
CHIEF = 2000
GATHERER = 2001
SCOUT = 2002

ROLES = [NONE, CHIEF, GATHERER, SCOUT]

ROLE_NAMES = {
    NONE: "No role",
    CHIEF: "Chief",
    GATHERER: "Gatherer",
    SCOUT: "Scout"
}

ai_name = "teamwork"
        
class Tile:
    def __init__(self, wall = False, person = False, resources = 0, unknown = False):
        self.wall = wall
        self.person = person
        self.resources = resources
        self.unknown = unknown
    
    @staticmethod
    def neighbours(x, y):
        return {
            (x+1, y): RIGHT,
            (x, y+1): DOWN,
            (x-1, y): LEFT,
            (x, y-1): UP
        }
    
    @staticmethod
    def unknown():
        return Tile(unknown = True)
    

class Chart:
    def __init__(self):
        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0
        self.tiles = {}
    
    def update(self, tiles, offX, offY):
        for ((relX, relY), tile) in tiles.items():
            x = relX + offX
            y = relY + offY
            self.tiles[x, y] = tile
            self.minX = min(self.minX, x)
            self.minY = min(self.minY, y)
            self.maxX = max(self.maxX, x)
            self.maxY = max(self.maxY, y)

    def getTile(self, x, y):
        if (x, y) in self.tiles:
            write(bool(self.tiles[x, y].unknown))
            return self.tiles[x, y]
        else: return Tile.unknown()

    def tilesBorder(self):
        tilesSet = set(self.tiles.keys())
        for tile in tilesSet: write((tile, bool(self.getTile(*tile))))
        tilesBorderSet = set()
        for pos in tilesSet:
            tilesBorderSet = tilesBorderSet.union(set(Tile.neighbours(*pos).keys()))
            #print(set(Tile.neighbours(*pos).keys()))
        write()
        for tile in tilesBorderSet: write((tile, bool(self.getTile(*tile))))
        return {pos: self.getTile(*pos) for pos in tilesBorderSet}
    
    def __str__(self):
        global m
        string = ""
        for y in range(self.minY-1, self.maxY+2):
            for x in range(self.minX-1, self.maxX+2):
                if (x, y) == (m.x, m.y):
                    c = '!'
                elif (x, y) in self.tiles:
                    tile = self.tiles[x, y]
                    if tile.unknown: c = 'U'
                    elif tile.wall: c = 'W'
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
        self.plan = []
    
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
            #print(*map(padHex, tile))
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
    def do(setState = None):
        if setState is not None: m.state = setState
        
        
        
        
        
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
                return do(RECEIVE_ROLE)
            if(ranks.count(max(ranks)) > 1):
                return do(INTRODUCTIONS)
            
            names = list(lookupBCs(broadcasts).keys())
            for name in names:
                member = Person(name)
                if(names.index(name) < len(names)/2): member.role = SCOUT
                else: member.role = GATHERER
                m.team[name] = member
            m.me.role = CHIEF
            m.team[m.me.name] = m.me
            broadcast = "&".join(["%s=%d" % (p.name, p.role) for p in m.team.values() if p is not m.me])
            
            m.state = CREATE_PLAN
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
                    return do(CREATE_PLAN)
            
            return BROADCAST, "Hey!"
        doReceiveRole.val = RECEIVE_ROLE
        
        
        
        def doMoveAround():
            return random.choice(MOVE), ""
        doMoveAround.val = MOVE_AROUND
        
        def doCreatePlan():
            return do({
                NONE: DO_NOTHING,
                CHIEF: PLAN_CHIEFING,
                GATHERER: PLAN_GATHERING,
                SCOUT: PLAN_SCOUTING
                }[m.me.role])
        doCreatePlan.val = CREATE_PLAN
        
        
        
        
        def doFollowPlan():
            if len(m.plan) == 0: return do(MOVE_AROUND)
            return m.plan.pop(), ""
        doFollowPlan.val = FOLLOW_THE_PLAN
        
        
        
        def doPlanChiefing():
            m.plan = [PICKUP, LEFT, PUTDOWN, RIGHT]*10 + [WAIT]
            return do(FOLLOW_THE_PLAN)
        doPlanChiefing.val = PLAN_CHIEFING
        
        
        
        def doPlanGathering():
            m.plan = [PICKUP, DOWN, PUTDOWN, UP]*8 + [WAIT]*3
            return do(FOLLOW_THE_PLAN)
        doPlanGathering.val = PLAN_GATHERING
        
        
        
        def doPlanScouting():
            chartTiles = [pos for (pos, tile) in m.chart.tilesBorder().items() if tile.unknown]
            write(list(map(str,[(pos, bool(m.chart.getTile(*pos).unknown)) for pos in chartTiles])))
            targetTile = min(chartTiles, key = lambda pos: sqrt(pos[0]**2 + pos[1]**2))
            write(targetTile)
            m.plan = planMoveTo(*targetTile)
            return do(FOLLOW_THE_PLAN)
        doPlanScouting.val = PLAN_SCOUTING
        
        
        
        def planMoveTo(x, y):
            
            start = (m.x, m.y)
            goal = (x, y)
            closedSet = []
            openSet = [start]
            cameFrom = {}
            
            def heuristicCostEstimate(node):
                return sqrt((goal[0]-node[0])**2 + (goal[1]-node[1])**2)
            
            def reconstructPath(node):
                if node in cameFrom: return reconstructPath(cameFrom[node][0]) + [cameFrom[node][1]]
                else: return []
                
            def neighbourNodes(node):
                availableNodes = {n: d for (n, d) in Tile.neighbours(*node).items() \
                                  if (n in m.chart.tiles and \
                                  not m.chart.tiles[n].wall and \
                                  not m.chart.tiles[n].person) or \
                                  n == goal}
                return {}
            
            gScore = {start: 0}
            fScore = {start: heuristicCostEstimate(start)}
            
            while len(openSet) > 0:
                current = min(openSet, key = lambda node: fScore[node])
                if current == goal:
                    return reconstructPath(goal)
                
                openSet.remove(current)
                closedSet.append(current)
                for (neighbour, direction) in neighbourNodes(current):
                    if neighbour in closedSet: continue
                    tentativeGScore = gScore[current] + 1
                    
                    if neighbour not in openSet or tentativeGScore < gScore[neighbour]:
                        cameFrom[neighbour] = (current, direction)
                        gScore[neighbour] = tentativeGScore
                        fScore[neighbour] = gScore[neighbour] + heuristicCostEstimate(neighbour)
                        if neighbour not in openSet:
                            openSet.append(neighbour)
            return []
        
        
        
        
        
        
        doState = {func.val: func for func in [
                doIntroductions,
                doDistributeRoles,
                doReceiveRole,
                doMoveAround,
                doCreatePlan,
                doFollowPlan,
                doPlanChiefing,
                doPlanGathering,
                doPlanScouting
            ]}
        
        if m.state in doState: return doState[m.state]()
        else: return WAIT, ""
    
    
    (intention, broadcast) = do()
    write("NAME: " + m.me.name)
    write("ROLE: " + ROLE_NAMES[m.me.role])
    write("STATE: " + str(m.state))
    write("PLAN: " + str(list(map(lambda x: INTENTION_DESCRIPTION[x], m.plan))))
    write(m.chart)
    return intention, "%s|%s" % (m.me.name, broadcast), m
    
