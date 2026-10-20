import os
import tempfile
import unittest

from stack_evaluator import (ExpressionError, Stack, evaluate, evaluate_entries,
                             format_result, read_input_file, write_output_file)


class StackTests(unittest.TestCase):
    def test_push_pop_order_is_lifo(self):
        s = Stack()
        for item in (1, 2, 3):
            s.push(item)
        self.assertEqual([s.pop(), s.pop(), s.pop()], [3, 2, 1])

    def test_peek_does_not_remove(self):
        s = Stack()
        s.push("a")
        self.assertEqual(s.peek(), "a")
        self.assertEqual(s.size(), 1)

    def test_is_empty_and_size(self):
        s = Stack()
        self.assertTrue(s.is_empty())
        s.push(5)
        self.assertFalse(s.is_empty())
        self.assertEqual(len(s), 1)

    def test_pop_empty_raises(self):
        with self.assertRaises(IndexError):
            Stack().pop()

    def test_peek_empty_raises(self):
        with self.assertRaises(IndexError):
            Stack().peek()


class EvaluateTests(unittest.TestCase):
    def check(self, expr, expected):
        self.assertAlmostEqual(evaluate(expr), expected, places=9, msg=expr)

    def test_assignment_samples(self):
        self.check("3 + 5 * 2", 13)
        self.check("(8 / 4) + 7 * 2", 16)
        self.check("10 - (2 + 3) * 4", -10)

    def test_precedence(self):
        self.check("2 + 3 * 4 - 5", 9)
        self.check("2 * 3 + 4 * 5", 26)

    def test_left_associativity(self):
        self.check("10 - 4 - 3", 3)
        self.check("100 / 10 / 5", 2)

    def test_parentheses_and_nesting(self):
        self.check("((2 + 3) * (4 - 1)) / 5", 3)
        self.check("(((7)))", 7)

    def test_unary_minus(self):
        self.check("-5 + 2", -3)
        self.check("2 - -3", 5)
        self.check("2 * -3", -6)
        self.check("-(4 + 6) * 2", -20)

    def test_decimals_and_whitespace(self):
        self.check("1.5 * 4 + 0.25", 6.25)
        self.check("   7*(  2+1 )  ", 21)

    def test_integer_division_stays_integer(self):
        self.assertIsInstance(evaluate("8 / 4"), int)
        self.assertEqual(evaluate("10 / 4"), 2.5)

    def test_errors(self):
        for bad in ["10 / (5 - 5)", "(3 + 4", "3 + 4)", "7 +", "* 3", "()",
                    "4 $ 2", "3 4", "2 (3)", "1..2 + 1", ""]:
            with self.subTest(expr=bad):
                with self.assertRaises(ExpressionError):
                    evaluate(bad)


class FormatTests(unittest.TestCase):
    def test_format_result(self):
        self.assertEqual(format_result(13), "13")
        self.assertEqual(format_result(4.0), "4")
        self.assertEqual(format_result(10 / 3), "3.333333")
        self.assertEqual(format_result(0.1 + 0.2), "0.3")
        self.assertEqual(format_result(-1e-12), "0")


class FileTests(unittest.TestCase):
    def test_round_trip_preserves_format(self):
        with tempfile.TemporaryDirectory() as folder:
            src = os.path.join(folder, "in.txt")
            dst = os.path.join(folder, "out.txt")
            with open(src, "w") as f:
                f.write("3 + 5 * 2\n-----\n(8 / 4) + 7 * 2\n=====\n10 - (2 + 3) * 4\n")
            write_output_file(dst, evaluate_entries(read_input_file(src)))
            with open(dst) as f:
                self.assertEqual(f.read(), "13\n-----\n16\n=====\n-10\n")

    def test_error_line_does_not_stop_processing(self):
        lines = evaluate_entries([("expr", "1 / 0"), ("sep", "-----"), ("expr", "2 + 2")])
        self.assertEqual(lines, ["Error: Division by zero", "-----", "4"])


if __name__ == "__main__":
    unittest.main()
