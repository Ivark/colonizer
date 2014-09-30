from constants import *
from tools import write
import random

def wait():
    return True

def move(level, person, direction, plannedMovement):
    if level.hasNeighbour(person.x, person.y, direction):
        (pos, neighbour) = level.getNeighbour(person.x, person.y, direction)
        if pos not in plannedMovement.keys():
            plannedMovement[pos] = (None, [person])
        else:
            plannedMovement[pos][1].append(person)
        return True
    return False

def resolveMoves(plannedMovement):
    def illegalMove(persons):
        while len(persons) > 0:
            person = persons.pop()
            person.intention = WAIT
            illegalMove(plannedMovement[person.x, person.y][1])
            plannedMovement[person.x, person.y][1].append(person)
    
    for (beforePerson, plannedPersons) in plannedMovement.values():
        if len(plannedPersons) > 1 or (beforePerson and beforePerson.intention not in MOVE):
            illegalMove(plannedPersons)
            plannedPersons.append(beforePerson)
    return {(x, y): (pPs[0], None) for ((x, y), (bP, pPs)) in plannedMovement.items() if len(pPs) == 1}

def pickUp(person):
    return person.onTile.hasResources() and not person.isCarrying

def putDown(person):
    return person.isCarrying and person.onTile.resources < 15

#def craft(person, plannedMovement):
#    return person.onTile.hasResources()

def attack(level, person, plannedMovement):
    random.shuffle(DIRECTIONS)
    for direction in DIRECTIONS:
        if level.hasNeighbour(person.x, person.y, direction):
            pos = level.getNeighbour(person.x, person.y, direction)[0]
            if pos in plannedMovement:
                person.victim = plannedMovement[pos][0]
                return True
    return False

def broadcast(person):
    return 0 < len(person.broadcast) < 256

def reproduce(level, person, plannedMovement):
    if person.onTile.resources < REPRODUCTION_PRICE_PER_PARTICIPANT: return False
    
    for direction1 in DIRECTIONS:
        if level.hasNeighbour(person.x, person.y, direction1):
            (pos1, neighbour1) = level.getNeighbour(person.x, person.y, direction1)
            if not neighbour1: continue
            if neighbour1.hasPerson() and neighbour1.person.intention is REPRODUCE and\
            neighbour1.resources >= REPRODUCTION_PRICE_PER_PARTICIPANT:
                
                for direction2 in DIRECTIONS:
                    if level.hasNeighbour(person.x, person.y, direction2):
                        if level.getNeighbour(person.x, person.y, direction2)[0] not in plannedMovement.keys(): return True
                break
            
    return False



def actionIsLegal(level, plannedMovement):
    canDo = {
        WAIT: lambda person: wait(),
        RIGHT: lambda person: move(level, person, RIGHT, plannedMovement),
        DOWN: lambda person: move(level, person, DOWN, plannedMovement),
        LEFT: lambda person: move(level, person, LEFT, plannedMovement),
        UP: lambda person: move(level, person, UP, plannedMovement),
        PICKUP: lambda person: pickUp(person),
        PUTDOWN: lambda person: putDown(person),
        #CRAFT: lambda person: craft(person, plannedMovement),
        ATTACK: lambda person: attack(level, person, plannedMovement),
        BROADCAST: lambda person: broadcast(person),
        REPRODUCE: lambda person: reproduce(level, person, plannedMovement)
    }
    
    return canDo