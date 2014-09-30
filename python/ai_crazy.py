from constants import *
import random

PERSON_DATA = 0
TILE_POS = 1
TILE_DATA = 2

ai_name = "crazy"

def think(inputData, memory):
    
    #Enterpret input
    
    byteState = PERSON_DATA
    intention = random.randrange(5)
    for i in range(2, len(inputData), 2):
        byte = int(inputData[i] + inputData[i+1], 16)
        if byte == 0x88:
            if byteState is PERSON_DATA:
                byteState = TILE_POS
                continue
            else: break
        if byteState is TILE_POS:
            tilePos = byte
            byteState = TILE_DATA
        elif byteState is TILE_DATA:
            person = (byte >> 4) % 2
            byteState = TILE_POS
            
            if tilePos in [0x01, 0x10, 0x0F, 0xF0] and person: intention = ATTACK
    
    return intention, "", {}