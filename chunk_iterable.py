from collections import deque
from collections.abc import Iterator
from typing import Any, Iterable


def chunk_iterable(
    iterable: Iterable,
    n: int = 1,
    *,
    preserve_iterable_type: bool = True,
) -> Iterator[Iterable[Any]]:
    """Split an iterable into chunks of a specified size.
    
    Notes:
        Iterable type is preserved on chunking, i.e. an input of tuple is 
        chunked into several tuples. Supports strings as an iterable and yields 
        slices of the string.

    Args:
        iterable (Iterable): The iterable to be chunked.
        n (int, optional): The size of each chunk. Default is 1.
        preserve_iterable_type (bool, optional): Whether to preserve the 
            iterable type. Default is True. If False, chunks are yielded as 
            tuples instead.

    Yields:
        Iterator[Iterable[Any]]: An iterator yielding chunks of the input 
                                 iterable.
        
    Raises:
        TypeError: If `iterable` is not an iterable or the `n` is not an integer.
        ValueError: If `n` is not a positive integer.
    """
    # Validate arguments
    # Equivalent to iterable=iter(iterable) which raises a TypeError exception
    # if iterable cannot be iterated.
    if not isinstance(iterable, Iterable):
        raise TypeError("Iterable to be chunked expected type `Iterable`, "
                        f"not `{type(iterable).__name__}`.")

    if not isinstance(n, int):
        raise TypeError("Chunk size expected type `int`, "
                        f"not `{type(n).__name__}`.")
        
    if not isinstance(preserve_iterable_type, bool):
        raise TypeError("Preserve iterable type expected type `bool`, "
                        f"not `{type(preserve_iterable_type).__name__}`.")
                
    if n <= 0:
        raise ValueError("Chunk size must be a positive integer.")
    
    # Perform chunking of iterable
    # Handle str type separately
    if isinstance(iterable, str):
        for i in range(0, len(iterable), n):
            yield iterable[i:i + n]
    else:
        dequed = deque(iterable)
        while dequed:
            # Preserve iterable type
            if preserve_iterable_type:
                yield type(iterable)(dequed.popleft() for _ in range(n) if dequed)
            else:
                yield tuple(dequed.popleft() for _ in range(n) if dequed)
                
            
if __name__ == "__main__":
    import unittest
    import sys    
    
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
                "Iterable to be chunked expected type `Iterable`, not `bool`.",
                str(exception_context.exception)
            )
            
        def test_chunk_list_into_2s_as_tuples(self):
            iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            chunk_size = 2
            expected = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
            actual = list(chunk_iterable(iterable, chunk_size, preserve_iterable_type=False))
            self.assertEqual(expected, actual)
        
        # Python >=3.12 
        if sys.version_info >= (3, 12, 0):
            # Python 3.12 introduced a new itertools.batched.
            # itertools.batched is not compatible with chunk_iterable since the
            # iterable type is preserved on chunking, whereas itertools.batched
            # always yields tuples
            
            def test_compare_with_itertools_batched_list(self):
                from itertools import batched
                
                iterable = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                expected = list(batched(iterable, 4))
                actual = list(chunk_iterable(iterable, 4))
                self.assertEqual(expected, actual)
            
            def test_compare_with_itertools_batched_tuple(self):
                from itertools import batched
                
                iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                expected = list(batched(iterable, 4))
                actual = list(chunk_iterable(iterable, 4))
                
                with self.assertRaises(AssertionError):
                    self.assertEqual(expected, actual)
                    
            def test_compare_with_itertools_batched_tuple_fix(self):
                # Band-aid fix to be compatible with itertools.batched is to
                # convert the chunked iterables to a tuple.
                from itertools import batched
                
                iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                expected = list(batched(iterable, 4))
                actual = list(chunk_iterable(iterable, 4, preserve_iterable_type=False))
                
                self.assertEqual(expected, actual)
            
    # Run the tests
    unittest.main(verbosity=2)