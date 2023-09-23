import re


# Regular expression to validate a roman numeral;
# Pattern accepts uppercase and lowercase letters, but integer_to_roman() will
# always return uppercase roman numerals;
# Only valid for roman numerals up to 3999;
ROMAN_PATTERN: re.Pattern = re.compile(
    r"^(M{0,3})(D?C{0,3}|CD|CM|)(L?X{0,3}|XL|XC)(V?I{0,3}|IV|IX|)$",
    re.IGNORECASE
)

# Mapping of roman numerals to integers;
# Value is based on the index of the roman numeral in the mapping;
ROMAN_MAPPING = {    
    "thousands" : ["", "M", "MM", "MMM"],
    "hundreds" : ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"],
    "tens" : ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"],
    "ones" : ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"],
}


# Validate a roman numeral string
def validate_roman(
    roman: str,
    /
) -> bool:
    """Validate a roman numeral string.

    Args:
        roman (str): The roman numeral to validate.

    Returns:
        bool: Whether the roman numeral is valid.
        
    Raises:
        TypeError: If the roman numeral is not a string.
    """
    if not isinstance(roman, str):
        raise TypeError("roman must be a string")
    
    if not len(roman):
        raise ValueError("roman must not be empty")
    
    return bool(ROMAN_PATTERN.match(roman))

# Converts a roman numeral string into its integer value
def roman_to_integer(
    roman: str,
    /
) -> int:
    """Converts a roman numeral string into its integer value.

    Args:
        roman (str): Roman numeral to convert.
        
    Returns:
        int: Integer value for the given roman numeral.

    Raises:
        TypeError: If the roman numeral is not of type `str`.
        ValueError: If the roman numeral is not a valid roman numeral string.
    """
    if not validate_roman(roman):
        raise ValueError("roman must be a valid roman numeral string")
    
    thousands, hundreds, tens, ones = re.findall(ROMAN_PATTERN, roman)[0]
    
    return sum([
        ROMAN_MAPPING.get("thousands").index(thousands.upper()) * 1000,
        ROMAN_MAPPING.get("hundreds").index(hundreds.upper()) * 100,
        ROMAN_MAPPING.get("tens").index(tens.upper()) * 10,
        ROMAN_MAPPING.get("ones").index(ones.upper()) * 1
    ])


# Converts an integer into its roman numeral string
def integer_to_roman(
    integer: int,
    /
) -> int:
    """Converts an integer into its roman numeral string.
    
    Notes:
        Valid only for integers between 1 and 3999, inclusive. 

    Args:
        integer (int): Integer to convert.
        
    Returns:
        str: Roman numeral string for the given integer.
        
    Raises:
        TypeError: If the integer is not of type `int`.
        ValueError: If the integer is not between 1 and 3999.
    """
    if not isinstance(integer, int):
        raise TypeError("integer to convert must be of type `int`, "
                        f"got `{type(integer).__name__}`")
        
    if not (1 <= integer <= 3999):
        raise ValueError("integer must be between 1 and 3999, inclusive")
    
    return "".join([
        ROMAN_MAPPING.get("thousands")[integer // 1000],
        ROMAN_MAPPING.get("hundreds")[(integer % 1000) // 100],
        ROMAN_MAPPING.get("tens")[(integer % 100) // 10],
        ROMAN_MAPPING.get("ones")[integer % 10]
    ])
    
    
if __name__ == "__main__":
    import unittest
    
    class ValidateRomanTestCases(unittest.TestCase):
        def test_valid_roman(self):
            # Uppercase
            self.assertTrue(validate_roman("I"))
            self.assertTrue(validate_roman("IV"))
            self.assertTrue(validate_roman("V"))
            self.assertTrue(validate_roman("LXIX"))
            self.assertTrue(validate_roman("CMXCIX"))
            self.assertTrue(validate_roman("MMXXIII"))
            self.assertTrue(validate_roman("MMMCMXCIX"))
            
            # Lowercase
            self.assertTrue(validate_roman("cmxcix"))
            self.assertTrue(validate_roman("mmxxiii"))
            
            # Mixed case (valid, but not recommended)
            self.assertTrue(validate_roman("mMmCmXCiX"))
            
        def test_invalid_roman(self):
            self.assertEqual(validate_roman("MMIXLX"), False)
            self.assertEqual(validate_roman("Hello world!"), False)
            
        def test_empty_string(self):
            with self.assertRaises(ValueError) as exception_context:
                validate_roman("")
            self.assertEqual(
                str(exception_context.exception),
                "roman must not be empty"
            )
                
    class IntegerToRomanTestCases(unittest.TestCase):
        def test_within_constraint(self):
            self.assertEqual(integer_to_roman(1), "I")
            self.assertEqual(integer_to_roman(4), "IV")
            self.assertEqual(integer_to_roman(5), "V")
            self.assertEqual(integer_to_roman(69), "LXIX")
            self.assertEqual(integer_to_roman(999), "CMXCIX")
            self.assertEqual(integer_to_roman(2023), "MMXXIII")
            self.assertEqual(integer_to_roman(3999), "MMMCMXCIX")
                        
        def test_outside_constraint(self):
            # Less than 1
            with self.assertRaises(ValueError) as exception_context:
                integer_to_roman(0)
            self.assertEqual(
                str(exception_context.exception), 
                "integer must be between 1 and 3999, inclusive"
            )
            
            # Greater than 3999
            with self.assertRaises(ValueError):
                integer_to_roman(4000)
                
            self.assertEqual(
                str(exception_context.exception), 
                "integer must be between 1 and 3999, inclusive"
            )
                
        def test_incorrect_type(self):
            with self.assertRaises(TypeError) as exception_context:
                integer_to_roman(1.0)
                
            self.assertEqual(
                str(exception_context.exception),
                "integer to convert must be of type `int`, got `float`"
            )
            
    class RomanToIntegerTestCases(unittest.TestCase):
        def test_valid_roman(self):
            self.assertEqual(roman_to_integer("I"), 1)
            self.assertEqual(roman_to_integer("IV"), 4)
            self.assertEqual(roman_to_integer("V"), 5)
            self.assertEqual(roman_to_integer("LXIX"), 69)
            self.assertEqual(roman_to_integer("CMXCIX"), 999)
            self.assertEqual(roman_to_integer("MMXXIII"), 2023)
            self.assertEqual(roman_to_integer("MMMCMXCIX"), 3999)
            
        def test_invalid_roman(self):
            with self.assertRaises(ValueError) as exception_context:
                roman_to_integer("IIII")
                
            self.assertEqual(
                str(exception_context.exception),
                "roman must be a valid roman numeral string"
            )
            
        def test_test_empty_string(self):
            with self.assertRaises(ValueError) as exception_context:
                roman_to_integer("")
                
            self.assertEqual(
                str(exception_context.exception),
                "roman must not be empty"
            )
        
        def test_incorrect_type(self):
            with self.assertRaises(TypeError) as exception_context:
                roman_to_integer(1.0)
            
    unittest.main(verbosity=2)