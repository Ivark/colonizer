from math import ceil, log
import random

def generateEnvironmentMDA(width=10, height=10, k=5, seed=False):

    # def t(n, x, y):
    #     for i in range(n):
    #         z = (y%2**(i+1) == 2**i) + (x%2**(i+1) == 2**i)
    #         if z != 0:
    #             return z*4**(n-i-1) + (y//2^(i+1))*2**(n-i-1) + (x//2**(i+1))
    #     return -1

    # if seed: random.seed(seed)

    # minSize = max([width, height])
    # nodes = [random.random() * 10 for i in range(4)]
    # n = 1
    # while 2**(n-1) + 1 < minSize:
    #     m = n-1
    #     nodes.extend([None]*(3*4**n))
    #     for y in range(2**m+1):
    #         for x in range(2**m):
    #             node = 0.5 * (nodes[t(n, x, y)] + nodes[t(n, x+1, y)])
    #             nodes[4**n + y*(2**m+1) + x] = node
    #     for y in range(2**m):
    #         for x in range(2**m+1):
    #             node = 0.5 * (nodes[t(n, x, y)] + nodes[t(n, x, y+1)])
    #             nodes[2*4**n + y*(2**m+1) + x] = node
    #     for y in range(2**m):
    #         for x in range(2**m):
    #             node = 0.25 * (nodes[4**n + y*(2**m+1) + x] + nodes[4**n + (y+1)*(2**m+1) + x])
    #             node += 0.25 * (nodes[2*4**n + y*(2**m+1) + x] + nodes[4**n + y*(2**m+1) + (x+1)])
    #             nodes[3*4**n + y*(2**m+1) + x] = k*(random.random() - 0.5)/2**(2*n) + node
    #     n += 1

    # env = [[0] * width] * height

    # env[0][0] = nodes[0]
    # for t in range(1, len(nodes)):
    #     node = nodes[t]
    #     if not node: continue
    #     m = math.floor(math.log(t)/math.log(4))
    #     z = t // 4**m
    #     y = (z>1)*2**(n-m-1) + ((t % 4**m) // (2**(m-1)+1))*2**(n-m)
    #     x = (z%2)*2**(n-m-1) + ((t % 4**m) % (2**(m-1)+1))*2**(n-m)
    #     if y < height and x < width:
    #         env[y][x] = node

    def generateMDA(depth, upperleft, upperright, lowerleft, lowerright):
        if depth:
            uppermiddle = 0.5*(upperleft + upperright)
            lowermiddle = 0.5*(lowerleft + lowerright)
            middleleft  = 0.5*(upperleft + lowerleft)
            middleright = 0.5*(upperright + lowerright)
            middlemiddle = 0.5*(uppermiddle + lowermiddle) + k*(random.random() - 0.5)*2**depth
            upperleftResult  = generateMDA(depth-1, upperleft, uppermiddle, middleleft, middlemiddle)
            upperrightResult = generateMDA(depth-1, uppermiddle, upperright, middlemiddle, middleright)
            lowerleftResult  = generateMDA(depth-1, middleleft, middlemiddle, lowerleft, lowermiddle)
            lowerrightResult = generateMDA(depth-1, middlemiddle, middleright, lowermiddle, lowerright)
            upperResult = [upperleftResult[i] + upperrightResult[i][1:] for i in range(2**(depth-1)+1)]
            lowerResult = [lowerleftResult[i] + lowerrightResult[i][1:] for i in range(2**(depth-1)+1)]
            result = upperResult + lowerResult[1:]
        else:
            result = [[upperleft, upperright], [lowerleft, lowerright]]
        return result

    minSize = max([width, height])
    depth = ceil(log(minSize - 1, 2))
    nodes = [(random.random() * 2 - 1) for i in range(4)]

    env = generateMDA(depth, *nodes)

    # for row in env:
    #     print(*map(lambda node: '%6.2f' % node, row))

    return env


# generateEnvironmentMDA()