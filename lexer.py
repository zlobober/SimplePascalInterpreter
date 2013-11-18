from logging import getLogger
import re

log = getLogger("lexer   ")

LEXEMS = {
    "KEYWORD"          : ["program", "if", "while", "do", "begin", "end", "else", 
                          "var", "case", "then", "end"],
    "TYPE"             : ["real", "integer", "boolean", "string"],
    "OPERATOR_COM"     : ["<", ">", "<=", ">=", "!=", "="],
    "OPERATOR_MUL"     : ["*", "and", "/", "div", "mod"],
    "OPERATOR_ADD"     : ["+", "-", "or"],
    "OPERATOR_UNR"     : ["not"],
    "SEMICOLON"        : [";"],
    "COLON"            : [":"],
    "COMMA"            : [","],
    "STRING"           : [],
    "BOOLEAN"          : ["false", "true"],
    "INTEGER"          : [],
    "REAL"             : [],
    "VARIABLE"         : [],
    "BRACKET"          : ["(", ")"],
    "EOF"              : ["#EOF"]
}

DIVIDERS = ["(", ")", "*", "+", "-", "/", ";", ",", ":", "=", "<>", "<=", ">=", "<", ">", "\n", " "]
DIGITS = "0123456789"

ALL = sum(LEXEMS.values(), [])
#print(ALL)

class SyntaxError(Exception):
    def __init__(self, msg):
        log.error(msg)

class Lexem:
    def __init__(self, l, v=None, pos=(-42,-42)):
        assert l in LEXEMS
        self.l, self.v, self.pos = l, v, (pos[0] + 1, pos[1] + 1)
        log.info("Found new %s '%s' at %s" % (l, v, self.pos))

    def __str__(self):
        return ''
#print(ALL)
    
class SyntaxError(Exception):
    def __init__(self, msg):
        log.error(msg)

class Lexem:
    def __init__(self, l, v=None, pos=(-42,-42)):
        assert l in LEXEMS
        self.l, self.v, self.pos = l, v, (pos[0] + 1, pos[1] + 1)
        log.info("Found new %s '%s' at %s" % (l, v, self.pos))

    def __str__(self):
        return "(%s | %s)" % (self.l, self.v)

def parseNumber(s, pos):
    try:
        if ('.' in s or 'e' in s):
            return Lexem("REAL", float(s), pos)
        else:
            return Lexem("INTEGER", int(s), pos)
    except ValueError:
        raise SyntaxError("Wrong number: %s" % s) 
        

def parseLexem(s, pos):
    if (s in [" ", "", "\n"]):
        return None    
    log.debug("Trying to parse lexem %s at %s", s, pos)
    assert s != ' ' and s != ''
    s = s.lower()
    if s in LEXEMS["BOOLEAN"]:
        return Lexem("BOOLEAN", s == "true", pos)
    for lt, l in LEXEMS.items():
        if (s in l):
            return Lexem(lt, s, pos)
    #log.warning("It can be number, but currently I can't determine whether " +
    #            "it's variable or not")
    if (s[0] in DIGITS):
        return parseNumber(s, pos)
    else:
        if not re.match("^[a-zA-Z0-9_]", s):
            raise SyntaxError("Bad identifer: %s" % s)
        return Lexem("VARIABLE", s, pos)

def mySplit(s):
    pt = 0
    s += '\n'
    for i, v in enumerate(s):
        if v in DIVIDERS:
            yield (s[pt:i], pt)
            yield (s[i], i)
            pt = i + 1


# here can be passed generator insted of string
def lexems(code):
    log.info("Lexer started")
    
    for i, line in enumerate(code):
        #l = list(filter(lambda x: not x[0] in ['', ' ', '\n'], mySplit(rep)))
        l = line.replace("end.", "end")
        log.info("Parsing line > %s", l)
        lt = 0
        pt = 0
        l += ' '
        while (pt < len(l)):
            bad = True
            if (l[pt] == '{'):
                beg = pt
                while (l[pt] != '}'):
                    pt += 1
                    if pt >= len(l):
                        raise SyntaxError("Unfinished commentary in line %d" % (i + 1)) 
                pt += 1
                lt = pt 
            elif (l[pt] == "'"):
                lt = pt
                pt += 1
                while (l[pt] != "'"):
                    pt += 1
                    if pt >= len(l):
                        raise SyntaxError("Unfinished string in line %d" % (i + 1))
                yield Lexem("STRING", l[lt + 1:pt], (i, lt))
                pt += 1
                lt = pt

            for d in DIVIDERS:
                if d == l[pt:pt+len(d)]:
                    bad = False
                    l1 = parseLexem(l[lt:pt], (i, lt))
                    if not l1 is None:
                        yield l1
                    l2 = parseLexem(l[pt:pt+len(d)], (i, pt))
                    if not l2 is None:
                        yield l2
                    pt += len(d)
                    lt = pt
                    break
            if bad:
                pt += 1
    yield Lexem("EOF", "#EOF")

    #yield lexem("KEYWORD", "PROGRAM")
    #for i in range(3):
    #    yield lexem("BRICK", i)
    log.info("Lexer finished")
    
    
