from logging_setup import setup_logging
import logging
import sys
import tokens
from lexer import Lexer
from parser import Parser
from ast_to_algebra import Converter
from simplify import Simplifier

setup_logging(level=__import__("logging").DEBUG)
log = logging.getLogger(__name__)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        raise TypeError("Wrong number of Arguments")
    source = args[0]
    log.info(f"Received {source} as input")

    lex = Lexer(source)
    tokens = lex.tokenize()
    log.info("Tokenized succefully")
    tok_printable = "\n".join(str(tok) for tok in tokens)
    log.debug(f"Tokens: \n {tok_printable}")

    p = Parser(tokens)
    tree = p.parse()
    log.info("Parsed successfully")
    log.debug(f"AST tree: \n {tree}")

    c = Converter(tree)
    alg_tree = c.convert_full()
    log.debug(alg_tree)

    s = Simplifier(alg_tree)
    print(s.eval())
