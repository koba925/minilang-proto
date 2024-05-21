import unittest
from minilang import Evaluator, Parser, run

class TestRun(unittest.TestCase):
    def test_int(self):
        self.assertEqual(run("12;"), 12)

    def test_factor(self):
        self.assertEqual(run("2 * 3;"), 6)
        self.assertEqual(run("2 * 3 * 4;"), 24)
        self.assertEqual(run("24 / 3;"), 8)
        self.assertEqual(run("24 / 3 / 2;"), 4)
        self.assertEqual(run("24 / 3 * 2;"), 16)

    def test_term(self):
        self.assertEqual(run("2 + 3;"), 5)
        self.assertEqual(run("6 - 3 - 2;"), 1)
        self.assertEqual(run("2 * 3 + 4;"), 10)
        self.assertEqual(run("6 - 4 / 2;"), 4)

    def test_grouping(self):
        self.assertEqual(run("2 * (3 + 4);"), 14)
        self.assertEqual(run("(6 - 4) / 2;"), 1)

    def test_ternary(self):
        self.assertEqual(run("1 ? 2 : 3;"), 2)
        self.assertEqual(run("0 ? 2 : 3;"), 3)
        self.assertEqual(run("1 ? 1 ? 2 : 3 : 1 ? 4 : 5;"), 2)
        self.assertEqual(run("1 ? 0 ? 2 : 3 : 1 ? 4 : 5;"), 3)
        self.assertEqual(run("0 ? 1 ? 2 : 3 : 1 ? 4 : 5;"), 4)
        self.assertEqual(run("0 ? 1 ? 2 : 3 : 0 ? 4 : 5;"), 5)

    def test_equality(self):
        self.assertEqual(run("1 = 1;"), 1)
        self.assertEqual(run("1 = 0;"), 0)
        self.assertEqual(run("1 # 1;"), 0)
        self.assertEqual(run("1 # 0;"), 1)
        self.assertEqual(run("1 + 3 = 2 * 2;"), 1)
        self.assertEqual(run("1 + 3 # 2 * 2;"), 0)

    def test_if(self):
        self.assertEqual(run("if (1 = 1) 2;"), 2)
        self.assertEqual(run("if (1 # 1) 2;"), None)
        self.assertEqual(run("if (1 = 1) 2; else 3;"), 2)
        self.assertEqual(run("if (1 # 1) 2; else 3;"), 3)

    def test_while(self):
        self.assertEqual(run("""
            var sum = 0;
            var i = 1;
            while (i # 11) { set sum = sum + i; set i = i + 1; }
            sum;
        """), 55)

    def test_block(self):
        self.assertEqual(run("{}"), None)
        self.assertEqual(run("{1 + 2;}"), 3)
        self.assertEqual(run("{1 + 2; 3 * 4;}"), 12)
        self.assertEqual(run("{1 + 2; {3 * 4; 5 = 6;}}"), 0)
        self.assertEqual(run("if (1=1) {2; 3;} else {4; 5;}"), 3)
        self.assertEqual(run("if (1=2) {2; 3;} else {4; 5;}"), 5)

    def test_var(self):
        self.assertEqual(run("var a = 1; a + 2;"), 3)
        self.assertEqual(run("var a = 2; set a = a + 3; a;"), 5)
        self._test_out("var a = 2; var b = 3; print(a); print(b);", [2, 3])

    def test_print(self):
        self._test_out("print(3);", [3])
        self._test_out("print(2); print(3); 1;", [2, 3])

    def test_scope(self):
        self._test_out("var a = 2; print(a); {var a = 4; print (a);} print(a);", [2, 4, 2])
        self._test_out("var a = 2; print(a); {set a = 4; print (a);} print(a);", [2, 4, 4])

    def test_func(self):
        self.assertEqual(run("func () {2;}();"), 2)
        self.assertEqual(run("func (a) {a + 1;}(2);"), 3)
        self.assertEqual(run("func (a, b) {a + b;}(2, 3);"), 5)

    def test_return(self):
        self._test_out("func () { print(1); return; print(0); }();", [1])
        self._test_out("""
            var f = func (a) { print(1); return a + 1; print(0); 0; };
            print(f(2));
        """, [1, 3])

    def test_fib(self):
        self.assertEqual(run("""
            var fib = func (n) {
                if (n = 1) 1;
                else if (n = 2) 1;
                else fib(n - 1) + fib(n - 2);
            };
            fib(6);
        """), 8)
        self.assertEqual(run("""
            var fib = func (n) {
                if (n = 1) return 1;
                if (n = 2) return 1;
                return fib(n - 1) + fib(n - 2);
            };
            fib(6);
        """), 8)
        self.assertEqual(run("""
            var fib = func (n) {
                if (n = 1) return 1;
                if (n = 2) return 1;
                var a = 1;
                var b = 1;
                var c = 0;
                var i = 3;
                while (i # n + 1) {
                    set c = a + b;
                    set a = b;
                    set b = c;
                    set i = i + 1;
                }
                return c;
            };
            fib(6);
        """), 8)

    def test_mutual_recursion(self):
        self._test_out("""
            var is_even = func (a) { if (a = 0) 1; else is_odd(a - 1); };
            var is_odd = func (a) { if (a = 0) 0; else is_even(a - 1); };
            print(is_even(3));
            print(is_odd(3));
            print(is_even(4));
            print(is_odd(4));
        """, [0, 1, 1, 0])

    def test_closure(self):
        self.assertEqual(run("""
            var make_adder = func (a) { func (b) { a + b; }; };
            var add3 = make_adder(3);
            add3(4);
        """), 7)

    def _test_out(self, src, out):
        e = Evaluator()
        e.eval(Parser(src).parse())
        self.assertEqual(e.out, out)

if __name__ == '__main__':
    unittest.main()
