import unittest
from minilang import Parser

class TestParse(unittest.TestCase):
    def test_int(self):
        self.assertEqual(Parser("12;").parse(), ["block", 12])

    def test_factor(self):
        self.assertEqual(Parser("2 * 3;").parse(), ["block", ["*", 2, 3]])
        self.assertEqual(Parser("2 * 3 * 4;").parse(), ["block", ["*", ["*", 2, 3], 4]])
        self.assertEqual(Parser("24 / 3;").parse(), ["block", ["/", 24, 3]])
        self.assertEqual(Parser("24 / 3 / 2;").parse(), ["block", ["/", ["/", 24, 3], 2]])

if __name__ == '__main__':
    unittest.main()
