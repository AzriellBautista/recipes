from collections import deque
from collections.abc import Iterator
from typing import Any, Iterable


def chunk_iterable(
    iterable: Iterable,
    /,
    size: int = 1, 
) -> Iterator[Iterable[Any]]:
    """Split an iterable into chunks of a specified size.
    
    Notes:
        Iterable type is preserved on chunking, i.e. an input of tuple is 
        chunked into several tuples. Supports strings as an iterable and yields 
        slices of the string.

    Args:
        iterable (Iterable): The iterable to be chunked.
        size (int, optional): The size of each chunk. Default is 1.

    Yields:
        Iterator[Iterable[Any]]: An iterator yielding chunks of the input 
                                 iterable.
        
    Raises:
        TypeError: If the input is not an iterable or the size is not an
                   integer.
        ValueError: If the size is not a positive integer.
    """
    # Validate arguments
    if not isinstance(iterable, Iterable):
        raise TypeError("Iterable to be chunked expected type `Iterable`. "
                        f"Got `{type(iterable).__name__}`.")
        
    if not isinstance(size, int):
        raise TypeError("Chunk size expected type `int`. "
                        f"Got `{type(size).__name__}`.")
                
    if size <= 0:
        raise ValueError("Chunk size must be a positive integer.")
    
    # Perform chunking of iterable
    if isinstance(iterable, str):
        dequed = deque(
            iterable[i:i + size]
            for i in range(0, len(iterable), size)
        )
        while dequed:
            yield dequed.popleft()
    else:
        dequed = deque(iterable)
        while dequed:        
            yield type(iterable)(
                dequed.popleft() 
                for _ in range(size) 
                if dequed
            )
            

if __name__ == "__main__":
    import unittest
    
    # Define the test
    class ChunkIterableTestCases(unittest.TestCase):
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
            expected = []
            actual = list(chunk_iterable(iterable))
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
            
        def test_chunk_list_default_chunk_size_arg(self):
            iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            expected = [[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]]
            actual = list(chunk_iterable(iterable))
            self.assertEqual(expected, actual)
    
        def test_chunk_str_default_chunk_size_arg(self):
            iterable = "abcdefghij"
            expected = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
            actual = list(chunk_iterable(iterable))
            self.assertEqual(expected, actual)
        
        # Test exceptions
        def test_chunk_list_into_0s(self):
            iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            chunk_size = 0

            with self.assertRaises(ValueError) as exception_context:
                list(chunk_iterable(iterable, chunk_size))
                
            self.assertEqual(
                "Chunk size must be a positive integer.",
                exception_context.exception.args[0]
            )
        
        def test_chunk_bool_into_2s(self):
            iterable = True
            chunk_size = 2
            
            with self.assertRaises(TypeError) as exception_context:
                list(chunk_iterable(iterable, chunk_size))
                
            self.assertEqual(
                "Iterable to be chunked expected type `Iterable`. Got `bool`.",
                str(exception_context.exception)
            )
            
    # Run the tests
    unittest.main(verbosity=2)