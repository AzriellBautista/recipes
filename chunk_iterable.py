from collections import deque
from collections.abc import Iterator
from typing import Any, Iterable

def chunk_iterable(
    __iterable: Iterable,
    __chunk_size: int = 1, 
    /,
) -> Iterator[Iterable[Any]]:
    """Split an iterable into chunks of a specified size.

    Args:
        iterable (Iterable): The iterable to be chunked.
        chunk_size (int, optional): The size of each chunk. Default is 1.

    Yields:
        Iterator[Iterable[Any]]: An iterator yielding chunks of the input 
                                 iterable.
        
    Raises:
        TypeError: If the input is not an iterable or the chunk size is not an
                   integer.
        ValueError: If the chunk size is not a positive integer.
    """
    # Validate arguments
    if not isinstance(__iterable, Iterable):
        raise TypeError("Iterable to be chunked expected type `Iterable`. "
                        f"Got `{type(__iterable).__name__}`.")
        
    if not isinstance(__chunk_size, int):
        raise TypeError("Chunk size expected type `int`. "
                        f"Got `{type(__chunk_size).__name__}`.")
        
    if __chunk_size <= 0:
        raise ValueError("Chunk size must be positive integer.")
    
    if isinstance(__iterable, str):
        dequed = deque(
            __iterable[i:i + __chunk_size]
            for i in range(0, len(__iterable), __chunk_size)
        )
        while dequed:
            yield dequed.popleft()
    else:
        dequed = deque(__iterable)
        while dequed:        
            yield type(__iterable)(
                dequed.popleft() 
                for _ in range(__chunk_size) 
                if dequed
            )

if __name__ == "__main__":
    import unittest
    
    # Define the test
    class TestChunkIterable(unittest.TestCase):
        # Supported types
        def test_chunk_list_into_2s(self):
            iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            chunk_size = 2
            expected = [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]
            actual = list(chunk_iterable(iterable, chunk_size))
            self.assertEqual(expected, actual)
            
        def test_chunk_list_into_3s(self):
            iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            chunk_size = 3
            expected = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]
            actual = list(chunk_iterable(iterable, chunk_size))
            self.assertEqual(expected, actual)
        
        def test_chunk_tuple_into_4s(self):
            iterable = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            chunk_size = 4
            expected = [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10)]
            actual = list(chunk_iterable(iterable, chunk_size))
            self.assertEqual(expected, actual)
        
        def test_chunk_empty_list(self):
            iterable = []
            chunk_size = 1
            expected = []
            actual = list(chunk_iterable(iterable, chunk_size))
            self.assertEqual(expected, actual)
            
        def test_chunk_str_into_2s(self):
            iterable = "abcdefghij"
            chunk_size = 2
            expected = ["ab", "cd", "ef", "gh", "ij"]
            actual = list(chunk_iterable(iterable, chunk_size))
            self.assertEqual(expected, actual)
            
        def test_chunk_str_into_3s(self):
            iterable = "abcdefghijk"
            chunk_size = 3
            expected = ["abc", "def", "ghi", "jk"]
            actual = list(chunk_iterable(iterable, chunk_size))
            self.assertEqual(expected, actual)
            
        def test_chunk_set_into_2s(self):
            iterable = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
            chunk_size = 2
            expected = [{1, 2}, {3, 4}, {5, 6}, {7, 8}, {9, 10}]
            actual = list(chunk_iterable(iterable, chunk_size))
            self.assertEqual(expected, actual)
        
        # Test exceptions
        def test_chunk_list_into_0s(self):
            iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            chunk_size = 0

            with self.assertRaises(ValueError) as exception_context:
                list(chunk_iterable(iterable, chunk_size))
                
            self.assertEqual(
                "Chunk size must be positive integer.",
                exception_context.exception.args[0]
            )
        
        def test_chunk_bool_into_2s(self):
            iterable = True
            chunk_size = 2
            
            with self.assertRaises(TypeError) as exception_context:
                list(chunk_iterable(iterable, chunk_size))
                
            self.assertEqual(
                "Iterable to be chunked expected type `Iterable`. Got `bool`.",
                exception_context.exception.args[0]
            )
            
    # Run the tests
    unittest.main(verbosity=2)