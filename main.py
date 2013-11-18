#!/usr/bin/env python3

from sys import argv, exit, stderr
from os import devnull
import logging


#logfile = stderr if "--verbose" in argv or "-v" in argv else open(devnull, 'w')

logging.basicConfig(format='%(name)s\t | %(levelname)s    \t%(message)s', level=logging.DEBUG if "-v" in argv else logging.WARNING)

log = logging.getLogger("main    ")

from code import readCode

if len(argv) < 2:
    log.error("I'm expecting .pas file to interpret as command-line argument!")
    exit(1)

code = readCode(argv[1])

from lexer import lexems, SyntaxError
try:
    L = list(lexems(code.split('\n')))
except SyntaxError:
    log.error("Syntax error, terminating interpretation... See details above")
    exit(1)
except:
    log.error("Something strange happened :-(")
    raise

from syntaxer import buildTree, SyntaxError
try:
    T = buildTree(L)
except SyntaxError:
    log.error("Syntax error, terminating interpretation... See details above.")
    exit(1)
except:
    log.error("Something strange :-(")
    raise

from runner import go, InterpretationError

try:
    go(T)
except InterpretationError:
    log.error("Interpretation error, terminating interpretation... See details above")
except:
    log.error("Something strange :-(")
    raise
