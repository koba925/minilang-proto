import unittest
from minilang import Scanner

class TestScanner(unittest.TestCase):
    def test_int(self):
        s = Scanner("  1 12 a ab + +- ")
        self.assertEqual(s.next(), 1)
        self.assertEqual(s.next(), 12)
        self.assertEqual(s.next(), "a")
        self.assertEqual(s.next(), "ab")
        self.assertEqual(s.next(), "+")
        self.assertEqual(s.next(), "+")
        self.assertEqual(s.next(), "-")
        self.assertEqual(s.next(), "")

if __name__ == '__main__':
    unittest.main()
