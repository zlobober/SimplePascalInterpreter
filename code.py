import logging

lines = []

def codePart(pos):
    if (pos[0] < 0):
        return "EOF"
    pos = (pos[0] - 1, pos[1] - 1)
    assert 0 <= pos[0] < len(lines)
    l = lines[pos[0]]
    assert 0 <= pos[1] < len(l)
    mn = max(0, pos[1] - 20)
    mx = min(len(l), pos[1] + 21)
    return ("\n" + ' ' * 32 + "line %d, pos %d:\n" + ' ' * 32 + "(...%s...)") % (pos[0] + 1, pos[1] + 1, l[mn:mx])

def readCode(s):    
    global code, lines
    log = logging.getLogger('main    ')

    code = open(s).read()
    log.info("Successfully read program code")

    lines = list(code.split('\n'))
    return code 
