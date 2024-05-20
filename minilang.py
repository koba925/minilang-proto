import operator as op
from typing import Any

class Evaluator:
    def __init__(self) -> None:
        self.out = []
        self.env = {
            "+": op.add, "-": op.sub, "*": op.mul, "/": op.floordiv,
            "=": lambda a, b: 1 if a == b else 0,
            "print": self.out.append
        }

    def eval(self, s):
        match s:
            case int(n): return n
            case str(s): return self.get(s)
            case ["if", cnd, thn, els]:
                return self.eval(thn) if self.eval(cnd) else self.eval(els)
            case ["block", *exps]: return self.block(exps)
            case ["define", name, val]: return self.define(name, self.eval(val))
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

    def define(self, name, val):
        self.env[name] = val

    def set(self, name, val):
        def _set(env, name):
            if name in env:
                env[name] = val
            else:
                _set(env["_enclosing"], name)

        return _set(self.env, name)

    def get(self, name):
        def _get(env, name):
            return env[name] if name in env else _get(env["_enclosing"], name)

        return _get(self.env, name)

class Scanner:
    def __init__(self, src) -> None:
        self.src = src
        self.current = 0

    def next(self):
        while self.curchar().isspace():
            self.current += 1
        start = self.current
        match self.curchar():
            case "": return ""
            case c if c.isnumeric():
                while self.curchar().isnumeric():
                    self.current += 1
            case c if c.isalpha():
                while self.curchar().isalnum() or self.curchar() == "_":
                    self.current += 1
            case _: self.current += 1
        lexeme = self.src[start:self.current]
        return int(lexeme) if lexeme.isnumeric() else lexeme

    def curchar(self):
        return self.src[self.current] if self.current < len(self.src) else ""

class Parser:
    def __init__(self, src):
        self.scanner = Scanner(src)
        self.current = ""
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
            case "define" | "set":
                return self.define_set(self.current)
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

    def define_set(self, op):
        self.advance()
        name = self.primary()
        self.consume("=")
        val = self.expression()
        self.consume(";")
        return [op, name, val]

    def expression(self):
        return self.equality()

    def equality(self):
        left = self.ternary()
        while self.current in ("=",):
            op = self.advance()
            right = self.ternary()
            left = [op, left, right]
        return left

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
        left = self.call()
        while self.current in ("*", "/"):
            op = self.advance()
            right = self.primary()
            left = [op, left, right]
        return left

    def call(self):
        name = self.primary()
        while self.current in ("(",):
            self.advance()
            name = [name] + self.arguments()
        return name

    def arguments(self):
        args = []
        while self.current != ")":
            args.append(self.expression())
            if self.current != ")":
                self.consume(",")
        self.consume(")")
        return args

    def primary(self):
        match self.current:
            case "(":
                self.advance()
                expr = self.expression()
                self.consume(")")
                return expr
            case "func": return self.func()
            case int(_) | str(_): return self.advance()
            case _: assert False, f"Unexpected `{self.current}`"

    def func(self):
        self.advance()
        self.consume("(")
        params = []
        while self.current != ")":
            param = self.current
            assert isinstance(param, str)
            self.advance()
            params.append(param)
            if self.current != ")":
                self.consume(",")
        self.consume(")")
        assert self.current == "{"
        body = self.block()
        return ["func", params, body]

    def consume(self, token):
        assert self.current == token, f"Expected `{token}`, found `{self.current}`"
        self.advance()

    def advance(self):
        current = self.current
        self.current = self.scanner.next()
        return current

def run(src):
    return Evaluator().eval(Parser(src).parse())

if __name__ == "__main__":
    ev = Evaluator()
    while True:
        src = input(": ")
        if src == "": break
        result = ev.eval(Parser(src).parse())
        if ev.out: print(*ev.out, sep="\n")
        if result is not None: print(">", result)
        ev.out.clear()
