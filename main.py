from logging_setup import setup_logging
import logging
import sys
import tokens
from lexer import Lexer, LexerError
from parser import Parser, ParserError
from ast_nodes import *

setup_logging(level=__import__("logging").DEBUG)
log = logging.getLogger(__name__)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        raise TypeError("Wrong number of Arguments")
    source = args[0]
    log.info(f"Received {source} as input")

    l = Lexer(source)
    tokens = l.tokenize()
    log.info("Tokenized succefully")
    log.debug(f"Tokens: {tokens}")

    p = Parser(tokens)
    tree = p.parse()
    log.info("Parsed successfully")
    log.debug(f"AST tree: {tree}")
