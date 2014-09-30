from sys import stdout, argv
import random
import math
from constants import *
from legal import actionIsLegal, resolveMoves
from do import performAction
from tools import padHex, padBin, listHex, write, writeAll, setWriteIndent

import ai_v1
import ai_v2
import ai_crazy

class Tile:
    def __init__(self, isWall=False):
        self.isWall = isWall
        self.resources = 0
        self.person = None
        self.broadcast = None
    
    def hasResources(self): return self.resources != 0
    def hasPerson(self): return self.person is not None
    def hasBroadcast(self): return self.broadcast not in [None, ""]
        
class Level:
    def __init__(self, persons, width=119, height=50, seed=False):
        self.persons = persons
        self.generateEnvironment(width, height, seed)
        
    def generateEnvironment(self, width=119, height=50, seed=False):
        #Todo: midpoint displacement algorithm
        
        if seed: random.seed(seed)
        
        xs = [random.uniform(0,2*math.pi)]
        for i in range(width-1):
            xs.append(xs[i] + 0.8*random.random())
            
        ys = [random.uniform(0,2*math.pi)]
        for i in range(height-1):
            ys.append(ys[i] + 0.8*random.random())
        
        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                tile = Tile(math.sin(xs[x])*math.sin(ys[y]) > random.uniform(0.1, 1.0))
                if not tile.isWall and random.random() > 0.99:
                    tile.resources = 1 + int(4*math.pow(random.random(), 5))
                row.append(tile)
            tiles.append(row)
        self.tiles = tiles
        
    def spawnTeam(self, ai, size=TEAM_SIZE):
        (teamX, teamY) = (random.choice(range(len(self.tiles[0]))), random.choice(range(len(self.tiles))))
        leader = self.spawnPerson(ai, teamX, teamY)
        if leader:
            write("Leader "+str((teamX, teamY))+": "+leader.name)
            dist = 1
            visited = [(teamX, teamY)]
            for i in range(1, size):
                personSpawned = False
                for d in range(dist, 100):
                    #write(d)
                    for x in range(teamX-d, teamX+d+1):
                        relX = x - teamX
                        for y in range(teamY-d, teamY+d+1):
                            relY = y - teamY
                            if (x, y) in visited: continue
                            if math.sqrt(relX*relX + relY*relY) <= d:
                                visited.append((x, y))
                                tile = self.getTile(x, y)
                                #write(math.sqrt(relX*relX + relY*relY))
                                if tile and not tile.isWall:
                                    member = self.spawnPerson(ai, x, y)
                                    if member:
                                        personSpawned = True
                                        write("- member "+str((x, y))+": "+member.name)
                                        dist = d
                                        break
                        if personSpawned: break
                    if personSpawned: break
        else:
            self.spawnTeam(ai, size)
                
                
        
    def spawnPerson(self, ai, x, y):
        tile = self.getTile(x, y)
        if not tile or tile.isWall or tile.hasPerson(): return None;
        person = Person(ai, x, y)
        tile.person = person
        person.onTile = tile
        self.persons.append(person)
        #write("position: "+str((x, y)))
        return person
    
    
    
    def getTile(self, x, y):
        if not y in range(len(self.tiles)): return None
        if not x in range(len(self.tiles[0])): return None
        return self.tiles[y][x]
    
    def hasNeighbour(self, x, y, direction):
        (x1, y1) = (x, y)
        if direction is RIGHT: x1 += 1
        if direction is DOWN: y1 += 1
        if direction is LEFT: x1 -= 1
        if direction is UP: y1 -= 1
        
        if not y1 in range(len(self.tiles)): return False
        if not x1 in range(len(self.tiles[0])): return False
        return not self.tiles[y1][x1].isWall
    
    def getNeighbour(self, x, y, direction):
        (x1, y1) = (x, y)
        if direction is RIGHT: x1 += 1
        if direction is DOWN: y1 += 1
        if direction is LEFT: x1 -= 1
        if direction is UP: y1 -= 1
        
        return ((x1, y1), self.getTile(x1, y1))
        
    
    
        
    def write(self):
        write()
        write('+' + ''.join(['-']*len(self.tiles[0])) + '+')
        for row in self.tiles:
            write('|', False)
            for tile in row:
                c = ' '
                if tile.isWall: c = '#'
                else:
                    if tile.hasPerson():
                        c = tile.person.ai.ai_name[0]
                        if tile.person.isCarrying: c = c.upper()
                        else: c = c.lower()
                    elif tile.hasResources(): c = str(hex(tile.resources))[2]
                    
                write(c, False)
            write('|')
        write('+' + ''.join(['-']*len(self.tiles[0])) + '+')
    
    def writeBig(self):
        write()
        write('+' + ''.join(['-']*(len(self.tiles[0]))*3) + '+')
        for i in range(len(self.tiles)*2):
            row = self.tiles[i//2]
            write('|', False)
            for j in range(len(row)*3):
                tile = row[j//3]
                c = ' '
                if tile.isWall: c = '#'
                else:
                    if tile.hasPerson():
                        c = tile.person.ai.ai_name[0]
                        if tile.person.isCarrying: c = c.upper()
                        else: c = c.lower()
                    elif tile.hasResources(): c = str(hex(tile.resources))[2]
                    
                write(c, False)
            write('|')
        write('+' + ''.join(['-']*(len(self.tiles[0]))*3) + '+')
            
class Person:
    def __init__(self, ai, x, y):
        self.ai = ai
        self.x = x
        self.y = y
        self.isAlive = True
        self.onTile = None
        self.isCarrying = False
        self.intention = WAIT
        self.lastAction = WAIT
        self.victim = None
        self.broadcast = None
        self.memory = {}
        self.name = random.choice(NAMES)+"-"+str(hash((x % 256) << 8 + (y % 256))).zfill(3)[-3:]
    
    def isBroadcasting(self): return self.intention is BROADCAST and self.broadcast not in [None, ""]
    
    
    def __str__(self): return str(self.name)
    def __repr__(self): return self.__str__()
    
    
    
    

    
def plan():
    global level, persons
    
    def tileData(personX, personY, relTileX, relTileY): #returns data about a tile as an integer
        tile = level.getTile(personX + relTileX, personY + relTileY)
        if not tile: tile = Tile(True)
        tileBytes = [
            ((relTileX % 16) << 4) + (relTileY % 16),
            (tile.isWall << 5) + (tile.hasPerson() << 4) + tile.resources
        ]
        return tileBytes
    
    def broadcastData(personX, personY, relTileX, relTileY): #returns data about a broadcast as an int
        tile = level.getTile(personX + relTileX, personY + relTileY)
        if not tile or not tile.hasBroadcast(): return False
        #write(level.getTile(personX, personY).person.name + " should hear some at " + str((personX + relTileX, personY + relTileY)) + " shout '" + tile.broadcast + "'")
        bcBytes = [((relTileX % 16) << 4) | (relTileY % 16)] #0-3 x-pos, 4-7 y-pos
        for c in tile.broadcast:
            bcBytes.append(ord(c) % 256)
        return bcBytes + [0x80]
    
    for person in persons:
        
        inputData = "0x"
        
        inputData += padHex(person.lastAction << 1 + person.isCarrying)[2:4] #0-6 lastAction, 7 isCarrying
        #write(inputData)
        inputData += "88" #indicates end of personData
        
        broadcasts = [] #list of positions from which this person can hear broadcasts
        xs = list(range(-7, 8))
        random.shuffle(xs)
        ys = list(range(-7, 8))
        random.shuffle(ys)
        for x in xs:
            for y in ys:
                if math.sqrt(x*x + y*y) <= VIEW_DISTANCE:
                    nextTileData = tileData(person.x, person.y, x, y)
                    inputData += listHex(nextTileData)[2:]
                    broadcasts.append((x, y)) #broadcasts from (x, y) can be heard by this person
        #write(inputData)
        inputData += "88" #indicates end of tiles
        
        random.shuffle(broadcasts)
        for pos in broadcasts:
            nextBroadcastData = broadcastData(person.x, person.y, pos[0], pos[1])
            if nextBroadcastData:
                inputData += listHex(nextBroadcastData)[2:]
        #write(inputData)
        inputData += "88" #indicates end of broadcasts
            
        write(person.name + ":", indent=2)
        setWriteIndent(3)
        person.broadcast = None
        (person.intention, variable, person.memory) = person.ai.think(inputData, person.memory)
        if person.intention is BROADCAST: person.broadcast = str(variable)
        setWriteIndent(1)
        write()

def resolve():
    global level, persons
    
    plannedMovement = {}
    isLegal = actionIsLegal(level, plannedMovement)
    
    for person in persons:
        plannedMovement[person.x, person.y] = (person, [])
        write(str(person.x).zfill(2) + ", " + str(person.y).zfill(2)+ ": " + person.name + " intends to " + INTENTION_DESCRIPTION[person.intention] + ".", indent=2)
    
    for intentions in ACTION_ORDER:
        for person in persons:
            if person.intention in intentions and not isLegal[person.intention](person):
                person.intention = WAIT
        if intentions is MOVE:
            plannedMovement = resolveMoves(plannedMovement)
    
    

def execute():
    global level, persons
    
    perform = performAction(level)
    
    for person in persons:
        person.onTile.person = None
        person.onTile.broadcast = None
    
    for intentions in ACTION_ORDER:
        for person in persons:
            if person.intention in intentions:
                #write(person.name + " does " + INTENTION_DESCRIPTION[person.intention] + ".")
                person.lastAction = person.intention
                perform[person.intention](person)
                person.onTile.person = person
    
    deaths = []
    for person in persons:
        #write("%s is%s alive" % (person.name, " not"[4*person.isAlive:]))
        if not person.isAlive:
            write(person.name + " has died.")
            deaths.append(person)
            person.onTile.person = None
            person.onTile.resources += 1 + person.isCarrying
    for person in deaths: persons.remove(person)

def initialize():
    global level, persons
    persons = []
    seed = None
    if len(argv) > 1: seed="".join(argv)
    level = Level(persons, 20, 20, seed=seed)
    level.spawnTeam(ai_crazy, 1)
    level.spawnTeam(ai_v1, 1)
    level.spawnTeam(ai_v2, 3)
    level.write()
    writeAll()
    
def tick():
    global level
    
    plan() #Each person plans their action
    resolve() #Illegal and conflicting actions are resolved
    execute() #Remaining actions are executed
    
    level.writeBig()
    writeAll()

def run(ticks=10):
    initialize()
    t = 0
    setWriteIndent(1)
    while not ticks or t < ticks:
        if input("\nPress enter for tick " + str(t+1) + "\n"): break
        write("\nTICK " + str(t+1) + ":\n\n", indent = 0)
        tick()
        t += 1
    write()

run(0)
