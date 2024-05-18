import operator as op

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
            case ["if", cnd, thn, els]: return self.eval(thn) if self.eval(cnd) else self.eval(els)
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
        for exp in exps: val = self.eval(exp)
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

# def repl():
#     ev = Evaluator()
#     while True:
#         src = input(": ") 
#         result = ev.eval(eval(src))
#         if ev.out: print(*ev.out, sep="\n")
#         if result is not None: print("> ", result)
#         ev.out = []

# repl(); exit()

class Scanner:
    def __init__(self, src) -> None:
        self.src = src
        self.start = 0
        self.current = 0

    def next(self):
        while self.curchr().isspace(): self.current += 1
        if self.curchr() == "": return ""
        self.start = self.current
        if self.curchr().isnumeric():
            while self.curchr().isnumeric(): self.current += 1
        elif self.curchr().isalpha():
            while self.curchr().isalnum(): self.current += 1
        else:
            self.current += 1
        lexeme = self.src[self.start:self.current]
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
        statements = []
        while self.current != "": statements.append(self.statement())
        return statements
    
    def statement(self):
        if self.current == "if": return self.if_()
        expr = self.expression()
        self.consume(";")
        return expr

    def if_(self):
        self.advance()
        self.consume("(") 
        cnd = self.expression()
        self.consume(")")
        thn = self.statement()
        self.consume("else")
        els = self.statement()
        return ["if", cnd, thn, els]

    def expression(self):
        return self.ternary()

    def ternary(self):
        cnd = self.term()
        if self.current == "?":
            self.advance()
            thn = self.ternary()
            self.consume(":")
            els = self.ternary()
            return ["if", cnd, thn, els]
        return cnd

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
        if self.current == "(":
            self.advance()
            expr = self.expression()
            self.consume(")")
            return expr
        if isinstance(self.current, int): return self.advance()
        assert False, "primary(): Invalid Expression"

    def advance(self):
        ret = self.current
        self.current = self.next
        self.next = self.scanner.next()
        return ret
    
    def consume(self, token):
        assert(self.current == token)
        self.advance()

def run(src):
    return Evaluator().eval(Parser(src).parse())

import unittest

# class TestScanner(unittest.TestCase):
#     def test_int(self):
#         s = Scanner("  1 12 a ab + +- ")
#         self.assertEqual(s.next(), 1)
#         self.assertEqual(s.next(), 12)
#         self.assertEqual(s.next(), "a")
#         self.assertEqual(s.next(), "ab")
#         self.assertEqual(s.next(), "+")
#         self.assertEqual(s.next(), "+")
#         self.assertEqual(s.next(), "-")
#         self.assertEqual(s.next(), "")

# class TestParse(unittest.TestCase):
#     def test_int(self):
#         self.assertEqual(Parser("12;").parse(), [12])
    
#     def test_factor(self):
#         self.assertEqual(Parser("2 * 3;").parse(), [["*", 2, 3]])
#         self.assertEqual(Parser("2 * 3 * 4;").parse(), [["*", ["*", 2, 3], 4]])
#         self.assertEqual(Parser("24 / 3;").parse(), [["/", 24, 3]])
#         self.assertEqual(Parser("24 / 3 / 2;").parse(), [["/", ["/", 24, 3], 2]])

# class TestRun(unittest.TestCase):
#     def test_int(self):
#         self.assertEqual(run("12;"), 12)
    
#     def test_factor(self):
#         self.assertEqual(run("2 * 3;"), 6)
#         self.assertEqual(run("2 * 3 * 4;"), 24)
#         self.assertEqual(run("24 / 3;"), 8)
#         self.assertEqual(run("24 / 3 / 2;"), 4)
#         self.assertEqual(run("24 / 3 * 2;"), 16)

#     def test_term(self):
#         self.assertEqual(run("2 + 3;"), 5)
#         self.assertEqual(run("6 - 3 - 2;"), 1)
#         self.assertEqual(run("2 * 3 + 4;"), 10)
#         self.assertEqual(run("6 - 4 / 2;"), 4)

#     def test_grouping(self):
#         self.assertEqual(run("2 * (3 + 4);"), 14)
#         self.assertEqual(run("(6 - 4) / 2;"), 1)

#     def test_if(self):
#         self.assertEqual(run("if (1) 2; else 3;"), 2)
#         self.assertEqual(run("if (0) 2; else 3;"), 3)

#     def test_ternary(self):
#         self.assertEqual(run("1 ? 2 : 3;"), 2)
#         self.assertEqual(run("0 ? 2 : 3;"), 3)
#         self.assertEqual(run("1 ? 1  ? : 2 : 3 : 1 ? 4 : 5;"), 2)
#         self.assertEqual(run("1 ? 0  ? : 2 : 3 : 1 ? 4 : 5;"), 3)
#         self.assertEqual(run("0 ? 1  ? : 2 : 3 : 1 ? 4 : 5;"), 4)
#         self.assertEqual(run("0 ? 1  ? : 2 : 3 : 0 ? 4 : 5;"), 5)

class TestEval(unittest.TestCase):

    def test_int(self):
        self.assertEqual(Evaluator().eval(1), 1)
                              
    def test_if(self):
        self.assertEqual(Evaluator().eval(["if", 0, 1, 2]), 2)
        self.assertEqual(Evaluator().eval(["if", 1, 1, 2]), 1)

    def test_eval_block(self):
        self.assertEqual(Evaluator().eval(["block"]), None)
        self.assertEqual(Evaluator().eval(["block", 1]), 1)
        self.assertEqual(Evaluator().eval(["block", 1, 2]), 2)
    
    def test_var(self):
        self.assertEqual(Evaluator().eval(["block", ["set", "a", 3], "a"]), 3)
    
    def test_calc(self):
        self.assertEqual(Evaluator().eval(["*", ["+", 1, 2], 3]), 9)
    
    def test_func(self):
        self.assertEqual(Evaluator().eval([["func", ["a", "b"],  ["+", "a", "b"]], 2, 3]), 5)

    def test_mutual_recursion(self):
        self.assertEqual(Evaluator().eval(["block", 
            ["set", "is_even", ["func", ["a"], ["if", ["=", "a", 0], 1, ["is_odd", ["-", "a", 1]]]]],
            ["set", "is_odd", ["func", ["a"], ["if", ["=", "a", 0], 0, ["is_even", ["-", "a", 1]]]]],
            ["is_even", 4],
        ]), 1)

    def test_closure(self):
        self.assertEqual(Evaluator().eval(["block", 
            ["set", "make_adder", ["func", ["a"], ["func", ["b"], ["+", "a", "b"]]]],
            ["set", "add3", ["make_adder", 3]],
            ["add3", 4]
        ]), 7)

    def test_fib(self):
        self.assertEqual(Evaluator().eval(["block",
            ["set", "fib", ["func", ["a"], [
                "if", ["=", "a", 1], 1, [
                    "if", ["=", "a", 2], 1, [
                        "+", ["fib", ["-", "a", 1]], ["fib", ["-", "a", 2]]]]]]],
            ["fib", 6]
        ]), 8)

    def test_print(self):
        e = Evaluator()
        e.eval(["print", 3])
        self.assertEqual(e.out, [3])

    def test_scope(self):
        e = Evaluator()
        e.eval(["block",
            ["set", "a", 3], ["print", "a"],
            ["block", ["set", "a", 4], ["print", "a"]],
            ["print", "a"],
        ])
        self.assertEqual(e.out, [3, 4, 3])

unittest.main()