WAIT = 0
RIGHT = 1
DOWN = 2
LEFT = 3
UP = 4
PICKUP = 5
PUTDOWN = 6
#CRAFT = 7
ATTACK = 8
BROADCAST = 9
REPRODUCE = 10


DIRECTIONS = MOVE = [RIGHT, DOWN, LEFT, UP]

ACTION_ORDER = [
    MOVE,
    [WAIT, PICKUP, PUTDOWN, BROADCAST],
    [REPRODUCE],
    [ATTACK]
]



VIEW_DISTANCE = 3.5
REPRODUCTION_PRICE_PER_PARTICIPANT = 3
TEAM_SIZE = 3

INTENTION_DESCRIPTION = {
    WAIT: "wait",
    RIGHT: "move right",
    DOWN: "move down",
    LEFT: "move left",
    UP: "move up",
    PICKUP: "pick up a resource",
    PUTDOWN: "put down a resource",
    #CRAFT: "craft something",
    ATTACK: "attack someone",
    BROADCAST: "shout something",
    REPRODUCE: "make a baby"
}

NAMES = ["Alex", "Charlie", "Corin", "Drew", "Emerson", "Finley", "Harley", "Hayden", "Jass", "Jess", "Morgan", "Quinn", "Reese", "River", "Sam", "Sky"]