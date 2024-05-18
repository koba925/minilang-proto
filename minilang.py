import operator as op
from typing import Any


class Evaluator:
    def __init__(self) -> None:
        self.out = []
        self.env = {
            "+": op.add, "-": op.sub, "*": op.mul, "/": op.floordiv, "=": op.eq,
            "print": self.out.append
        }

    def eval(self, exp):
        match exp:
            case int(n): return n
            case str(s): return self.get(exp)
            case ["if", cnd, thn, els]:
                return self.eval(thn) if self.eval(cnd) else self.eval(els)
            case ["block", *exps]: return self.block(exps)
            case ["set", name, val]: return self.set(name, self.eval(val))
            case ["func", param, body]: return ["func", param, body, self.env]
            case [op, *args]:
                op, args = self.eval(op), [self.eval(arg) for arg in args]
                return op(*args) if callable(op) else self.apply(op, args)

    def block(self, exps):
        prev = self.env
        self.env = {"_enclosing": prev}
        val = None
        for exp in exps:
            val = self.eval(exp)
        self.env = prev
        return val

    def apply(self, op, args):
        prev = self.env
        self.env = dict(zip(op[1], args)) | {"_enclosing": op[3]}
        val = self.eval(op[2])
        self.env = prev
        return val

    def get(self, name):
        def _get(env, name):
            return env[name] if name in env else _get(env["_enclosing"], name)

        return _get(self.env, name)

    def set(self, name, val):
        self.env[name] = val

class Scanner:
    def __init__(self, src) -> None:
        self.src = src
        self.start = 0
        self.current = 0

    def next(self):
        while self.curchr().isspace():
            self.current += 1
        self.start = self.current
        match self.curchr():
            case "": return ""
            case c if c.isnumeric():
                while self.curchr().isnumeric():
                    self.current += 1
            case c if c.isalpha():
                while self.curchr().isalnum():
                    self.current += 1
            case _:
                self.current += 1
        lexeme = self.src[self.start : self.current]
        self.start = self.current
        return int(lexeme) if lexeme.isnumeric() else lexeme

    def curchr(self):
        return self.src[self.current] if self.current < len(self.src) else ""

class Parser:
    def __init__(self, src):
        self.scanner = Scanner(src)
        self.current = self.next = ""
        self.advance()
        self.advance()

    def parse(self):
        statements: list[Any] = ["block"]
        while self.current != "":
            statements.append(self.statement())
        return statements

    def statement(self):
        match self.current:
            case "{": return self.block()
            case "if": return self.if_()
            case _:
                expr = self.expression()
                self.consume(";")
                return expr

    def block(self):
        self.advance()
        block: list[Any] = ["block"]
        while self.current != "}":
            block.append(self.statement())
        self.consume("}")
        return block

    def if_(self):
        self.advance()
        self.consume("(")
        cnd = self.expression()
        self.consume(")")
        thn = self.statement()
        els = None
        if self.current == "else":
            self.advance()
            els = self.statement()
        return ["if", cnd, thn, els]

    def expression(self):
        return self.ternary()

    def ternary(self):
        cnd = self.term()
        if self.current != "?": return cnd
        self.advance()
        thn = self.ternary()
        self.consume(":")
        els = self.ternary()
        return ["if", cnd, thn, els]

    def term(self):
        left = self.factor()
        while self.current in ("+", "-"):
            op = self.advance()
            right = self.factor()
            left = [op, left, right]
        return left

    def factor(self):
        left = self.primary()
        while self.current in ("*", "/"):
            op = self.advance()
            right = self.primary()
            left = [op, left, right]
        return left

    def primary(self):
        match self.current:
            case "(":
                self.advance()
                expr = self.expression()
                self.consume(")")
                return expr
            case int(_):
                return self.advance()
            case _:
                assert False, f"Unexpected `{self.current}`"

    def advance(self):
        ret = self.current
        self.current = self.next
        self.next = self.scanner.next()
        return ret

    def consume(self, token):
        assert self.current == token, f"Expected `{token}`, found `{self.current}`"
        self.advance()

def run(src): return Evaluator().eval(Parser(src).parse())

def repl(parser):
    ev = Evaluator()
    while True:
        src = input(": ")
        if src == "":
            break
        result = ev.eval(parser(src))
        if ev.out:
            print(*ev.out, sep="\n")
        if result is not None:
            print(">", result)
        ev.out.clear()

if __name__ == "__main__":
    # repl(eval)
    repl(lambda src: Parser(src).parse())