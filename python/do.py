from constants import *
from tools import write
import random

def move(level, person, direction):
    ((person.x, person.y), person.onTile) = level.getNeighbour(person.x, person.y, direction)

def pickUp(person):
    person.onTile.resources -= 1
    person.isCarrying = True

def putDown(person):
    person.onTile.resources += 1
    person.isCarrying = False

#def craft(person):
#    return

def attack(level, person):
    #write("%s is totally killing %s right now" % (person.name, person.victim.name))
    person.victim.isAlive = False
    person.victim = None
    
    #random.shuffle(MOVE)
    #for direction in MOVE:
    #    if level.hasNeighbour(person.x, person.y, direction):
    #        neighbour = level.getNeighbour(person.x, person.y, direction)[1]
    #        if neighbour.hasPerson():
    #            neighbour.person.isAlive = False
    #            break

def broadcast(person):
    write("%s says: %s" % (person.name, person.broadcast))
    person.onTile.broadcast = person.broadcast

def reproduce(level, person):
    person.onTile.resources -= REPRODUCTION_PRICE_PER_PARTICIPANT
    person.intention = WAIT
    
    random.shuffle(MOVE)
    for direction1 in MOVE:
        if not level.hasNeighbour(person.x, person.y, direction1): continue
        (pos1, neighbour1) = level.getNeighbour(person.x, person.y, direction1)
        if neighbour1.hasPerson() and neighbour1.person.intention is REPRODUCE:
            neighbour1.resources -= REPRODUCTION_PRICE_PER_PARTICIPANT
            neighbour1.person.intention = WAIT
            for direction2 in MOVE:
                if not level.hasNeighbour(person.x, person.y, direction2): continue
                (pos2, neighbour2) = getNeighbour(person.x, person.y, direction2)
                if not neighbour2.hasPerson(): level.spawnPerson(person.thinkF, pos2[0], pos2[1])
            return




def performAction(level):
    resolveDo = {
        WAIT: lambda person: True,
        RIGHT: lambda person: move(level, person, RIGHT),
        DOWN: lambda person: move(level, person, DOWN),
        LEFT: lambda person: move(level, person, LEFT),
        UP: lambda person: move(level, person, UP),
        PICKUP: lambda person: pickUp(person),
        PUTDOWN: lambda person: putDown(person),
        #CRAFT: lambda person: craft(person),
        ATTACK: lambda person: attack(level, person),
        BROADCAST: lambda person: broadcast(person),
        REPRODUCE: lambda person: reproduce(level, person)
    }
    
    return resolveDo