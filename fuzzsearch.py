# Tested on Python 3.12.0 with rapidfuzz==3.4.0
# Provides a fuzzy_search() function to search for similar strings in an 
# iterable of strings

from typing import Iterable

from rapidfuzz import fuzz


def fuzzy_search(
    lines: Iterable[str], 
    string: str, 
    threshold: float | int,
    include_score: bool = True,
) -> list[tuple[str, float]] | list[str]:
    """
    Performs a fuzzy search within a collection of strings, identifying matches 
    that surpass a specified similarity threshold using the fuzz ratio, which is
    based on the Levenshtein distance.
    
    Args:
        lines (Iterable[str]): The iterable of strings to search in.
        string (str): The string to search for.
        threshold (float | int): The threshold level for similarity matching
            from 0 to 100.
        include_score (bool, optional): Whether to include the similarity score 
            in the returned list of matches. Defaults to True.
    
    Raises:
        TypeError: If lines is not an iterable of strings, or if string is
            not a string, or if threshold is not a number
        ValueError: If similarity is not between 0 and 100
    
    Examples:
        >>> from fuzzsearch import fuzzy_search
        >>> lines = ["hello", "world", "python"]
        >>> string = "hello"
        >>> similarity = 80
        >>> fuzzy_search(lines, string, similarity)
        [('hello', 100.0)]
    
    Returns:
        list[tuple[str, float]] | list[str] : Matched lines with similarity
            score higher than the fuzz ratio
    """    
    # Validation: Types
    if not isinstance(lines, Iterable) or isinstance(lines, str):
        raise TypeError("`lines` must be an iterable of strings")
    if not isinstance(string, str):
        raise TypeError("`string` must be a string")
    if not isinstance(threshold, (int, float)):
        raise TypeError("`threshold` must be a number")
    if not isinstance(include_score, bool):
        raise TypeError("`include_score` must be a boolean")
    
    # Validation: Values
    if not (0 <= threshold <= 100):
        raise ValueError("`similarity` must be between 0 and 100")
    
    # Create an empty list instance to append similar lines to
    similar_lines = list()
    
    # Loop through the iterable of strings
    for line in lines:
        line = str(line).strip()  # Make sure it's a string
        # Compare fuzz ratio to the threshold level
        if (ratio := fuzz.ratio(string, line)) >= threshold:
            similar_lines.append(
                # If include_score is True, append the line with the fuzz ratio
                (line, round(ratio, 2)) if include_score
                # Else, append only the line 
                else line
            )
    
    # Return the list of similar lines
    return similar_lines


# # Uncomment this to run an example program
# if __name__ == "__main__":
#     from pathlib import Path
#     from pprint import pprint
    
#     # `rockyou.txt` is a text file that contains list of commonly used passwords
#     file = Path(__file__).parent / "rockyou.txt"
    
#     # Open the file and read it line by line
#     with open(file, mode="r", encoding="utf-8", errors="ignore") as f:
#         lines = (l for l in f)  # Prefer generators
#         string = "password"     # Search for strings similar to `password`
#         threshold = 70          # with threshold of at least 80%

#         # Pretty-print the list of matches, sorted by threshold score
#         pprint(sorted(fuzzy_search(lines, string, similarity), 
#                       key=lambda x: x[1], reverse=True))