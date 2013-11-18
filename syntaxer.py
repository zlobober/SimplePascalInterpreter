from logging import getLogger
from lexer import Lexem
from code import codePart

log = getLogger("syntaxer")

Lpt = 0
__debugRL__ = 0
__RL__ = 0

class Node:
    def __getitem__(self, k):
        return None if not k in self.D else self.D[k]
    def __init__(self, t):
        self.t = t
        self.D = {}
    def __setitem__(self, k, v):
        self.D[k] = v
    def __str__(self):
        global __debugRL__
        __debugRL__ += 1
        T = '|  ' * __debugRL__
        ret = ""
        if 'pos' in dir(self):
            ret = ((T + "=== %s [#%s] ===\n") % (self.t, str(self.pos)))
        else:
            ret = ((T + "=== %s ===\n") % (self.t, ))
        for k, v in self.D.items():
            if type(k) is int:
                k = "[%d]" % (k, )
            ret += T + "+-" + k + ":\n"
            if (type(v) is Node): 
                ret += str(v)
            else:
                ret += T + '|  ' + str(v) + '\n'
        __debugRL__ -= 1
        return ret
    def __iter__(self):
        return iter(self.D.items())

class SyntaxError(Exception):
    def __init__(self, text):
        log.error(text)



def buildTree(L):

    cur = None

    def Builder(name):
        def wrapper(f):
            def go(*args, **kwargs):
                try:
                    global __RL__
                    __RL__ += 1
                    T = __RL__ * '   '
                    log.debug(T + "inside %s" % (name, ))
                    ret = f(*args, **kwargs)
                    log.debug(T + "outside %s" % (name, ))
                    __RL__ -= 1
                    return ret
                except:
                    log.error("Can't parse block '%s'" % (name,))
                    raise
            return go
        return wrapper
    
    def match(nxt, t):
        l = t[0]
        v = t[1]
        good = (nxt.l == l or l is None) and (nxt.v == v or v is None)
        return good

    def scan(*args, delta = None):
        global Lpt

        if delta is None:
            nxt = L[Lpt]
            Lpt += 1
        else:
            nxt = L[Lpt + delta]
        wewant = ' | '.join("(%s | %s)" % arg for arg in args)
        if (delta is None):
            log.info("Waiting for %s...", wewant)
        if not True in list(match(nxt, arg) for arg in args):
            raise SyntaxError("Expecting %s instead of %s at %s" % (wewant, nxt, codePart(nxt.pos)))
        if (delta is None):
            log.info(".....found: %s at %s", nxt, nxt.pos)
        return nxt
        assert 0 <= Lpt < len(L)

    @Builder("variable group")
    def buildVarGroup():
        node = Node("varGroup")
        node.sz = 1
        node[0] = scan(("VARIABLE", None)).v
        while (scan(("COLON", ":"), ("COMMA", ","), delta=0).l == "COMMA"):
            scan(("COMMA", ","))
            node[node.sz] = scan(("VARIABLE", None)).v
            node.sz += 1
        return node

    @Builder("variable line")
    def buildVarLine():
        node = Node("varLine")
        node["varGroup"] = buildVarGroup()
        node.pos = scan(("COLON", ":")).pos
        node["type"] = scan(("TYPE", None)).v
        scan(("SEMICOLON", ";"))
        return node

    @Builder("variable block")
    def buildVarBlock():
        scan(("KEYWORD", "var"))
        scan(("VARIABLE", None), delta = 0)
        node = Node("varBlock")
        node.sz = 1
        node[0] = buildVarLine()
        while (scan(("VARIABLE", None), ("KEYWORD", "begin"), delta=0).l == "VARIABLE"):
            node[node.sz] = buildVarLine()
            node.sz += 1
        return node

    @Builder("array index")

    def buildArrayIndex():
        node = Node("arrayIndex")
        node["arr"] = scan(("VARIABLE", None)).v
        scan(("BRACKET", "["))
        node["idx"] = scan(("INTEGER", None)).v
        scan(("BRACKET", "]"))
        return node


    @Builder("atom")
    def buildAtom():
        s = scan(
            ("BRACKET", "("), 
            ("INTEGER", None),
            ("REAL", None),
            ("BOOLEAN", None),
            ("STRING", None),
            ("VARIABLE", None),
            (None, "-"),
            (None, "not"),
            delta=0
        )
        if (s.l == "BRACKET"):
            scan(("BRACKET", "("))
            ret = buildExpr()
            scan(("BRACKET", ")"))
            return ret
        elif s.l in ("INTEGER", "REAL", "BOOLEAN", "STRING"):
            return scan(("INTEGER", None), ("REAL", None), ("BOOLEAN", None), ("STRING", None)).v
        elif s.l == "VARIABLE":
            if (scan((None, None), delta=0).l == "VARIABLE" and scan((None, None), delta=1).v == "("):
                return buildFunction()
            elif (scan((None, None), delta=0).l == "VARIABLE" and scan((None, None), delta=1).v == "["):
                return buildArrayIndex()
            node = Node("var")
            l = scan(("VARIABLE", None))
            node["name"], node.pos = l.v, l.pos
            return node
        else:
            scan((None, "-"), (None, "not"))
            node = Node("unar")
            node["oper"] = s.v
            node["left"] = buildSum()
            return node
    
    @Builder("mul")
    def buildMul():
        node = Node("mul")
        node[0] = buildAtom()
        node.sz = 1
        node.pos = {}
        while (scan((None, None),delta=0).l == "OPERATOR_MUL"):
            l = scan(("OPERATOR_MUL", None))
            v, pos = l.v, l.pos
            node[node.sz] = v
            node.pos[node.sz] = pos 
            node[node.sz + 1] = buildAtom()
            node.sz += 2
        if (node.sz == 1):
            return node[0]
        return node


    @Builder("sum")
    def buildSum():
        m = buildMul()
        node = Node("sum")
        node[0] = m
        node.sz = 1
        node.pos = {}
        while (scan((None, None),delta=0).l == "OPERATOR_ADD"):
            l = scan(("OPERATOR_ADD", None))
            v, pos = l.v, l.pos
            node[node.sz] = v
            node[node.sz + 1] = buildMul()
            node.pos[node.sz + 1] = pos
            node.sz += 2
        if (node.sz == 1):
            return node[0]
        return node
    
    @Builder("expr")
    def buildExpr():
        node = Node("expr")
        node[0] = buildSum()
        node.sz = 1
        node.pos = {}
        while (scan((None, None), delta=0).l == "OPERATOR_COM"):
            l = scan(("OPERATOR_COM", None))
            v, pos = l.v, l.pos
            node[node.sz] = v
            node.pos[node.sz] = pos
            node[node.sz + 1] = buildSum()
            node.sz += 2
        if (node.sz == 1):
            return node[0]
        return node

    @Builder("while")
    def buildWhile():
        node = Node("while")
        node.pos = scan(("KEYWORD", "while")).pos
        node["condition"] = buildExpr()
        scan(("KEYWORD", "do"))
        node["body"] = buildOperator()
        return node

    @Builder("if")
    def buildIf():
        node = Node("if")
        node.pos = scan(("KEYWORD", "if")).pos
        node["condition"] = buildExpr()
        scan(("KEYWORD", "then"))
        node["body"] = buildOperator()
        return node

    @Builder("do")
    def buildDo():
        node = Node("do")
        scan(("KEYWORD", "do"))
        node["body"] = buildOperator()
        node.pos = scan(("KEYWORD", "while")).pos
        node["condition"] = buildExpr()
        return node

    @Builder("case")
    def buildCase():
        raise NotImplementedError

    @Builder("assignment")
    def buildAssignment():
        node = Node("assignment")
        node["left"] = scan(("VARIABLE", None)).v
        node.pos = scan(("COLON", ":")).pos
        scan(("OPERATOR_COM", "="))
        node["right"] = buildExpr()
        scan(("SEMICOLON", ";"))
        return node

    @Builder("function")
    def buildFunction():
        node = Node("function")
        l = scan(("VARIABLE", None))
        node["func"], node.pos = l.v, l.pos
        scan(("BRACKET", "("))
        node.sz = 0
        while True:
            s = (scan((None, None), delta=0))
            if (s.v == ')'):
                scan(("BRACKET", ")"))
                break
            node[node.sz] = buildExpr()
            node.sz += 1
            s = scan(("BRACKET", ")"), ("COMMA", ","))
            if (s.v == ')'):
                break
        return node

    @Builder("operator")
    def buildOperator():
        l = scan(
            ("KEYWORD", "begin"), 
            ("KEYWORD", "while"),
            ("KEYWORD", "if"),
            ("KEYWORD", "case"),
            ("KEYWORD", "do"),
            ("VARIABLE", None), 
            delta=0)
        if (l.l == "VARIABLE"):
            if scan(("COLON", ":"), ("BRACKET", "("), delta=1).l == "COLON":  
                return buildAssignment()
            else:
                b = buildFunction()
                scan(("SEMICOLON", ";"))
                return b

        elif (l.v == "begin"):
            return buildOperatorSection()
        elif (l.v == "while"):
            return buildWhile()
        elif (l.v == "do"):
            return buildDo()
        elif (l.v == "if"):
            return buildIf()
        elif (l.v == "case"):
            return buildCase()
        else:
            assert False

    @Builder("operator block")
    def buildOperatorBlock():
        node = Node("operatorBlock")
        node[0] = buildOperator()
        node.sz = 1
        while (scan((None, None), delta=0).v != "end"):
            node[node.sz] = buildOperator()
            node.sz += 1
        return node

    @Builder("operator section")
    def buildOperatorSection():
        scan(("KEYWORD", "begin"))
        op = buildOperatorBlock()
        lex = scan(("KEYWORD", "end"))
        return op

    @Builder("program")
    def buildProgram():
        scan(("KEYWORD", "program"))
        program_name = scan(("VARIABLE",None))
        node = Node("program")
        node["name"] = program_name.v
        scan(("SEMICOLON", None))
        try:
            node["var"] = buildVarBlock()
            node["body"] = buildOperatorSection()
            scan(("EOF", "#EOF"))
        except:
            global Lpt
            l = max(0, Lpt - 5)
            r = min(len(L), Lpt + 6)
            log.error("Error around part: ..." + ' '.join(str(x.v) for x in L[l:r]) + "...")
            raise

        assert Lpt == len(L)

        return node
   
    Lpt = 0
    
    log.info("Syntaxer started")
    tree = buildProgram()
    log.debug("Program tree:\n" + str(tree))
    log.info("Syntaxer finished")
    return tree    

