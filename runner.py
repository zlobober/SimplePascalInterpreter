from syntaxer import Node
from code import codePart
import logging 

log = logging.getLogger("runner  ")

def run(node):
    if type(node) is Node:
        return eval("Logic.run_" + node.t)(node)
    elif type(node) in (int, str, bool, float):
        return node
    else:
        assert false

class var: 
    def __init__(value = None, dtype = None):
        if (val is None):
            assert not dtype is None
            self.dtype = dtype
            self.value = dtype(0)
        elif (dtype is None):
            assert not value is None
            self.value = value
            self.dtype = type(value)
        else:
            assert False
V = {}    

types    = {"integer" : int, "real" : float, "boolean" : bool, "string" : str}
invtypes = dict((b, a) for a, b in types.items())

def default_value(t):
    if t in types:
        return t(0)
    return None

class Operator:
    def Type(*e):
        def decorator(f):
            def go(*args):
                for arg in args:
                    if not type(arg) in e:
                        raise TypeError()
                return f(*args)
            return go
        return decorator
    
    # Не удержался =)
    def getF(s):
        return eval("lambda x, y: x %s y" % s)

    log.info("Initializing functions...")

    B = {
        "+"   : Type(int, float)      (getF("+")),
        "-"   : Type(int, float)      (getF("-")),
        "*"   : Type(int, float)      (getF("*")),
        "/"   : Type(int, float)      (getF("/")),
        "mod" : Type(int)             (getF("%")),
        "div" : Type(int)             (getF("//")),
        "="   : Type(int, float, bool)(getF("==")),
        "<"   : Type(int, float)      (getF("<")),
        ">"   : Type(int, float)      (getF(">")),
        "<>"  : Type(int, float)      (getF("!=")),
        "<="  : Type(int, float)      (getF("<=")),
        ">="  : Type(int, float)      (getF(">=")),
        "and" : Type(bool)            (getF("and")),
        "or"  : Type(bool)            (getF("or"))
    }

    U = {
        "-"   : Type(int, float)(float.__neg__),
        "not" : Type(bool)(lambda x: not x)
    }

class InterpretationError(Exception):
    def __init__(self, pos, text):
        log.error(text + ' ' * 32 + codePart(pos))

class InFunctionError(Exception):
    def __init__(self, text):
        self.text = text

class Function:
    def Func(*param):
        assert len(param) == 1
        T = param[0]
        def wrap(f):
            def g(*args, **kwargs):
                pos = kwargs["pos"]
                if not T is None:
                    if len(args) != len(T):
                        raise InterpretationError(pos, "Function %s takes %d args, not %d", f.__name__, len(T), len(args))
                    for i, a, b in zip(range(len(T)), T, args):
                        if not a is None and not type(b) in a:
                            raise InterpretationError(pos, "%d argmunet of function %s should have type (%s), not %s" % (i + 1, f.__name__, ' | '.join(invtypes[x] for x in a), invtypes[type(b)]))
                return f(*args)
            return g

        return wrap

    @Func(None)
    def writeln(*args):
        print(''.join(map(str, args)))

    @Func([(int, float)])
    def ln(x):
        from math import log
        return log(x) 

    @Func([(int, float)])
    def sqrt(x):
        return x ** 0.5

    @Func([])
    def readint():
        return int(input())

    @Func([(float,)])
    def real_to_int(x):
        return int(x)
        

def calc(func, *args, pos=None):
    try:
        f = eval("Function.%s" % func)
        return f(*args, pos=pos)
    except AttributeError:
        raise InterpretationError(pos, "Function %s is undeclared" % func)
    except InFunctionError as e:
        raise InterpretationError(pos, "Error while evaluting function %s: \'%s\'" % (func, e.text))

class Logic:
    def runner(f):
        def go(*args, **kwargs):
            assert len(args) == 1 and len(kwargs) == 0 and type(args[0]) is Node
            try:
                return f(*args, **kwargs)
            except:
                log.error("Error while running %s", args[0].t)
                raise
        return go

    @runner
    def run_var(node):
        if not node["name"] in V:
            raise InterpretationError(node.pos, "Use of undeclared variable %s" % node["name"])
        return V[node["name"]]

    @runner
    def run_unar(node):
        try:
            v = Operator.U[node["oper"]](run(node["left"]))
        except TypeError:
            raise InterpretationError(node.pos, "Invalid type")
        except ZeroDivisionError:
            raise InterpretationError(node.pos, "Division by zero")
        return v

    @runner
    def run_comm_expr(node):
        v = run(node[0])
        #if (2 in node.D):
        #    log.debug("%s\n%s", node[1], node.sz)
        assert node.sz % 2 == 1
        for i in range(1, node.sz, 2):
            try:
                v = Operator.B[node[i]](v, run(node[i + 1]))
            except TypeError:
                raise InterpretationError(node.pos[i], "Invalid types")
            except ZeroDivisionError:
                raise InterpretationError(node.pos[i], "Division by zero")
        return v

    run_expr = run_comm_expr
    run_sum = run_comm_expr
    run_mul = run_comm_expr

    @runner
    def run_function(node):
        return calc(node["func"], *tuple(map(run, [v for k,v in node if type(k) is int])), pos=node.pos)

    @runner
    def run_assignment(node):
        global V
        if not node["left"] in V:
            raise InterpretationError(node.pos, "Use of undeclared variable %s" % node["left"])
        r = run(node["right"])
        #log.debug("assigning %s := %s", node["left"], r)
        V[node["left"]] = r 
        
    @runner
    def run_operatorBlock(node):
        for k, v in node:
            run(v)
    
    @runner
    def run_program(node):
        run(node["var"])
        log.info("Declared variables:\n%s", '\n'.join(str(k) + " : " + str(v) for k, v in V.items()))
        run(node["body"])

    @runner
    def run_varLine(node):
        global V
        global types
        for k, v in node["varGroup"]:
            if v in V:
                raise InterpretationError(node.pos, "Re-definition of variable %s" % (v,))
            V[v] = default_value(types[node["type"]])

    @runner
    def run_varBlock(node):
        for k, v in node:
            run(v)
            
    @runner
    def run_while(node):
        while (True):
            r = run(node["condition"])
            if (not type(r) is bool):
                raise InterpretationError("Condition has to be boolean value, but it is %s", r)
            if not r:
                break
            run(node["body"])

    def run_if(node):
        r = run(node["condition"])
        if (not type(r) is bool):
            raise InterpretationError("Condition has to be boolean value, but it is %s", r)
        if r:
            run(node["body"])

def go(node):
    log.info("Runner started")
    run(node)
    log.info("Runner finished")
    log.info("Variable values at the end:\n" + '\n'.join(str(k) + " = " + str(v) for k, v in V.items()))

