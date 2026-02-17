import unittest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ast_nodes import PerDurationExpression, Distribution

class TestParser(unittest.TestCase):

    def test_per_duration_expression(self):
        source = "$500 / 1mo"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        expr = parser.parse_expression()
        self.assertIsInstance(expr, PerDurationExpression)
        self.assertEqual(expr.left.value, "$500")
        self.assertEqual(expr.duration, "1mo")

    def test_distribution_named_arguments(self):
        source = "~Normal(μ=0, σ=1)"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        dist = parser.parse_expression()
        self.assertIsInstance(dist, Distribution)
        self.assertEqual(dist.dist_type, "Normal")
        self.assertIn("μ", dist.params)
        self.assertEqual(dist.params["μ"].value, 0)
        self.assertIn("σ", dist.params)
        self.assertEqual(dist.params["σ"].value, 1)

if __name__ == "__main__":
    unittest.main()