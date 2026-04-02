from logging_setup import setup_logging
import logging
import sys

# import tokens
from lexer import Lexer
from parser import Parser
from ast_to_algebra import Converter
from algebra_nodes import Var
from simplify import Simplifier, SimplifierError

setup_logging(level=__import__("logging").INFO)
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
    log.info("Converted from AST to Algebra succefully")
    log.debug(alg_tree)

    # for i in alg_tree.children():
    #     log.debug(i)
    # log.debug("\n")
    # for i in alg_tree.walk():
    #     log.debug(i)

    s = Simplifier()
    simplified = s.simplify(alg_tree)
    log.info("simplified successfully")
    print(simplified)
