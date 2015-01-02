def generateEnviromnentMDA(width=50, height=50, k=5, seed=False):

    def t(n, x, y):
        for i in range(n):
            z = 2*(y%2**(i+1) == 2**i) + (x%2**(i+1) == 2**i)
            if z != 0:
                return z*4**(n-i-1) + (y//2^(i+1))*2**(n-i-1) + (x//2**(i+1))
        return -1

    if seed: random.seed(seed)

    minSize = max([width, height])
    nodes = [random.random() * 10 for i in range(4)]
    n = 1
    while 2**(n-1) + 1 < minSize:
        nodes.extend([None]*(3*(4**n)))
        for y in range(2**(n-1)+1):
            for x in range(2**(n-1)):
                node = 0.5 * (nodes[t(n, x, y)] + nodes[t(n, x+1, y)])
                nodes[4**n + y*(2**(n-1)+1) + x] = node
        for y in range(2**(n-1)):
            for x in range(2**(n-1)+1):
                node = 0.5 * (nodes[t(n, x, y)] + nodes[t(n, x, y+1)])
                nodes[2*4**n + y*(2**(n-1)+1) + x] = node
        for y in range(2**(n-1)):
            for x in range(2**(n-1)):
                node = 0.25 * (nodes[4**n + y*(2**(n-1)+1) + x] + nodes[4**n + (y+1)*(2**(n-1)+1) + x])
                node += 0.25 * (nodes[2*4**n + y*(2**(n-1)+1) + x] + nodes[4**n + y*(2**(n-1)+1) + (x+1)])
                nodes[3*4**n + y*(2**(n-1)+1) + x] = k*(random.random() - 0.5)/(2**2n) + node
        n += 1

    env = [[0] * width] * height

    env[0][0] = nodes[0]
    for t in range(1, len(nodes)):
        node = nodes[t]
        if not node: continue
        m = math.floor(math.log(t)/math.log(4))
        z = t // 4**m
        y = (z>1)*2**(n-m-1) + ((t % 4**m) // (2**(m-1)+1))*2**(n-m)
        x = z%2==1)*2**(n-m-1) + ((t % 4**m) % (2**(m-1)+1))*2**(n-m)
        if y < height and x < width:
            env[y][x] = node

    for row in env:
        print(*map(lambda node: '%5.2f' % node, row))


generateEnviromnentMDA()