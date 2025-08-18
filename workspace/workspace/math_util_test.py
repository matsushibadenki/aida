import unittest
from workspace.math_util import add

class TestMathUtil(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(add(5, 3), 8)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, 1), 0)

    def test_add_positive_and_negative(self):
        self.assertEqual(add(5, -3), 2)

    def test_add_zero(self):
        self.assertEqual(add(0, 5), 5)

if __name__ == '__main__':
    unittest.main()