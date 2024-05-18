import unittest
from minilang import Evaluator, run

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
        self.assertEqual(run("1 + 3 = 2 * 2;"), 1)

    def test_if(self):
        self.assertEqual(run("if (1 = 1) 2;"), 2)
        self.assertEqual(run("if (1 = 2) 2;"), None)
        self.assertEqual(run("if (1 = 1) 2; else 3;"), 2)
        self.assertEqual(run("if (1 = 0) 2; else 3;"), 3)

    def test_block(self):
        self.assertEqual(run("{}"), None)
        self.assertEqual(run("{1 + 2;}"), 3)
        self.assertEqual(run("{1 + 2; 3 * 4;}"), 12)
        self.assertEqual(run("{1 + 2; {3 * 4; 5 = 6;}}"), 0)
        self.assertEqual(run("if (1=1) {2; 3;} else {4; 5;}"), 3)
        self.assertEqual(run("if (1=2) {2; 3;} else {4; 5;}"), 5)

    def test_var(self):
        self.assertEqual(run("set a = 1; a + 2;"), 3)

if __name__ == '__main__':
    unittest.main()
