import unittest

from compiler.lexer import Lexer, TokenType


class TestLexer(unittest.TestCase):

    def test_duration_literals(self):
        source = "1mo 30d 1yr"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.DURATION)
        self.assertEqual(tokens[0].value, "1mo")

        self.assertEqual(tokens[1].type, TokenType.DURATION)
        self.assertEqual(tokens[1].value, "30d")

        self.assertEqual(tokens[2].type, TokenType.DURATION)
        self.assertEqual(tokens[2].value, "1yr")

        self.assertEqual(tokens[3].type, TokenType.EOF)

if __name__ == "__main__":
    unittest.main()
