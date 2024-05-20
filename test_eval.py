import unittest
from minilang import Evaluator

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
        self.assertEqual(Evaluator().eval(["block", ["var", "a", 3], "a"]), 3)

    def test_calc(self):
        self.assertEqual(Evaluator().eval(["*", ["+", 1, 2], 3]), 9)

    def test_func(self):
        self.assertEqual(Evaluator().eval([["func", ["a", "b"],  ["+", "a", "b"]], 2, 3]), 5)

    def test_mutual_recursion(self):
        self.assertEqual(Evaluator().eval(["block",
            ["var", "is_even", ["func", ["a"], ["if", ["=", "a", 0], 1, ["is_odd", ["-", "a", 1]]]]],
            ["var", "is_odd", ["func", ["a"], ["if", ["=", "a", 0], 0, ["is_even", ["-", "a", 1]]]]],
            ["is_even", 4],
        ]), 1)

    def test_closure(self):
        self.assertEqual(Evaluator().eval(["block",
            ["var", "make_adder", ["func", ["a"], ["func", ["b"], ["+", "a", "b"]]]],
            ["var", "add3", ["make_adder", 3]],
            ["add3", 4]
        ]), 7)

    def test_fib(self):
        self.assertEqual(Evaluator().eval(["block",
            ["var", "fib", ["func", ["a"], [
                "if", ["=", "a", 1], 1, [
                    "if", ["=", "a", 2], 1, [
                        "+", ["fib", ["-", "a", 1]], ["fib", ["-", "a", 2]]]]]]],
            ["fib", 6]
        ]), 8)

    def test_print(self):
        e = Evaluator()
        e.eval(["print", 3])
        self.assertEqual(e.out, [3])
        e.out.clear()
        e.eval(["block", ["print", 3], ["print", 2]])
        self.assertEqual(e.out, [3, 2])


    def test_scope(self):
        e = Evaluator()
        e.eval(["block",
            ["var", "a", 3], ["print", "a"],
            ["block", ["var", "a", 4], ["print", "a"]],
            ["print", "a"],
        ])
        self.assertEqual(e.out, [3, 4, 3])
        e.out.clear()
        e.eval(["block",
            ["var", "a", 3], ["print", "a"],
            ["block", ["set", "a", 4], ["print", "a"]],
            ["print", "a"],
        ])
        self.assertEqual(e.out, [3, 4, 4])

if __name__ == '__main__':
    unittest.main()
