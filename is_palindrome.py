from numbers import Number

def is_palindrome(i: str | Number, /) -> bool:
    """Checks if the given input is a palindrome. Supports numbers.Number.

    Args:
        i (str | numbers.Number): The input to check.

    Raises:
        TypeError: _description_
        TypeError: _description_

    Returns:
        bool: `True` if the input is a palindrome, `False` otherwise.
    """
    if not isinstance(i, (str, Number)):
        raise TypeError("Expected input to be `str` or `numbers.Number`, " 
                        f"got `{type(i).__name__}`.")

    return str(i) == str(i)[::-1]


if __name__ == "__main__":
    import unittest
    
    class IsPalindromeTestCases(unittest.TestCase):
        def test_palindrome_int(self):
            self.assertTrue(is_palindrome(123454321))

        def test_palindrome_str(self):
            self.assertTrue(is_palindrome("aibohphobia"))  # 😱
            self.assertTrue(is_palindrome("tacocat"))  # 🌮🐱

        def test_palindrome_float(self):
            self.assertTrue(is_palindrome(123.321))

        def test_non_palindrome_int(self):
            self.assertFalse(is_palindrome(1234))
            self.assertFalse(is_palindrome(-1234321))

        def test_non_palindrome_str(self):
            self.assertFalse(is_palindrome("abc"))

        def test_non_palindrome_float(self):
            self.assertFalse(is_palindrome(12.34))

        def test_incorrect_type(self):
            with self.assertRaises(TypeError) as exception:
                is_palindrome(None)

            self.assertEqual(
                str(exception.exception),
                "Expected input to be `str` or `numbers.Number`, got `NoneType`."
            )
        
    unittest.main(verbosity=2)