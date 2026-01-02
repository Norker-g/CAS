import sys
import tokens
from lexer import Lexer

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        raise TypeError
    source = args[0]
    l = Lexer(source)
    out = l.tokenize()
    for i in out:
        print(i)
