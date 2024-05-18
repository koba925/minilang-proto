def get(env, name):
    return env[name] if name in env else get(env["_enclosing"], name)

def set(env, name, val):
    env[name] = val
    return name

def eval_exps(exps):
    val = None
    for exp in exps: val = eval_exp(exp)
    return val

def apply(op, args):
    global env
    prev = env
    env = dict(zip(op[1], args)) | {"_enclosing": op[3]}
    val = eval_exps(op[2])
    env = prev
    return val

def eval_exp(exp):
    match exp:
        case int(i): return i
        case str(s): return get(env, exp)
        case ["if", cnd, thn, els]: return eval_exp(thn) if eval_exp(cnd) else eval_exp(els)
        case ["define", name, val]: return set(env, name, eval_exp(val))
        case ["lambda", param, *body]: return ["lambda", param, body, env]
        case [op, *args]:
            op, args = eval_exp(op), [eval_exp(arg) for arg in args]
            return op(args) if callable(op) else apply(op, args)

def eval(exps):
    global env
    env = {
        "add1": lambda args: args[0] + 1,
        "sub1": lambda args: args[0] - 1,
        "equal": lambda args: args[0] == args[1],
        "print": lambda args: print(*args)
    }
    return eval_exps(exps)

import unittest

class TestClass(unittest.TestCase):

    def lib(self):
        eval([
            ["define", "is_zero", ["lambda", ["a"], ["equal", "a", 0]]],
            ["define", "add", ["lambda", ["a", "b"], ["if", ["is_zero", "a"], "b", ["add", ["sub1", "a"], ["add1", "b"]]]]],
        ])

    def test_int(self):
        self.assertEqual(eval([1]), 1)
                              
    def test_if(self):
        self.assertEqual(eval([["if", 0, 1, 2]]), 2)
        self.assertEqual(eval([["if", 1, 1, 2]]), 1)

    def test_eval_exps(self):
        self.assertEqual(eval([]), None)
        self.assertEqual(eval([1]), 1)
        self.assertEqual(eval([1, 2]), 2)
    
    def test_var(self):
        self.assertEqual(eval([["define", "a", 3], "a"]), 3)
    
    def test_add1(self):
        self.assertEqual(eval([["add1", 1]]), 2)
    
    def test_lambda(self):
        self.assertEqual(eval([[["lambda", ["a"],  ["add1", "a"]], 2]]), 3)

    def test_recursion(self):
        self.lib()
        self.assertEqual(eval_exps([
            ["add", ["add", 2, 3], 4]
        ]), 9)

    def test_mutual_recursion(self):
        self.assertEqual(eval([
            ["define", "is_even", ["lambda", ["a"], ["if", ["equal", "a", 0], 1, ["is_odd", ["sub1", "a"]]]]],
            ["define", "is_odd", ["lambda", ["a"], ["if", ["equal", "a", 0], 0, ["is_even", ["sub1", "a"]]]]],
            ["is_even", 4],
        ]), 1)

    def test_closure(self):
        self.lib()
        self.assertEqual(eval_exps([
            ["define", "make_adder", ["lambda", ["a"], ["lambda", ["b"], ["add", "a", "b"]]]],
            ["define", "add3", ["make_adder", 3]],
            ["add3", 4]
        ]), 7)

    def test_fib(self):
        self.lib()
        self.assertEqual(eval_exps([
            ["define", "fib", ["lambda", ["a"],[
                "if", ["equal", "a", 1], 1, [
                    "if", ["equal", "a", 2], 1, [
                        "add", ["fib", ["sub1", "a"]], ["fib", ["sub1", ["sub1", "a"]]]]]]]],
            ["fib", 6]
        ]), 8)

unittest.main()