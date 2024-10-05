from functools import wraps, partial
from inspect import iscoroutinefunction, getfullargspec
from asyncio import sleep as asleep
from time import sleep
from random import uniform
from collections.abc import Callable, Iterable, Mapping
from typing import Any


"""
This module provides a retry decorator that can be used to retry a function over
a list of exceptions for a specified number of attempts with a specified delay 
between each attempt.The decorator supports both synchronous and asynchronous 
functions.
"""

__version__ = "1.0.0"

class MaxRetryExceededError(Exception):
    """Exception raised when the maximum number of retries is exceeded."""
    pass


def retry(
    func: Callable[..., Any] | None = None,
    /,
    *,
    max_retries: int = -1,
    delay: float = 0.0,
    max_delay: float | None = None,
    jitter: float = 0.0,
    exceptions: Iterable[type[BaseException]] = (Exception,),
    backoff: Callable[[float, int], float] | None = None,
) -> Callable[..., Any]:
    """
    Retry decorator that supports both synchronous and asynchronous functions.
    If no function is passed, it returns a partial retry function.

    Sample Usage:
        @retry(max_retries=3, delay=1.0, exceptions=(ValueError,))
        def my_function():
            raise ValueError("Something went wrong")
        my_function() # Will be retried 3 times with a delay of 1.0 seconds

    Args:
        func (Callable[..., Any] | None): The function to be retried. Defaults 
            to None.
        max_retries (int): The maximum number of retries. Negative values are 
            equivalent to infinite retries. Defaults to -1.
        delay (float): Base delay between retries in seconds. Defaults to 0.0.
        max_delay (float | None): The maximum delay between retries. None means
            no maximum delay will be set. Defaults to None.
        jitter (float): The jitter to add/subtract to the delay. Defaults to 0.
        exceptions (Iterable[type[BaseException]]): The exceptions to 
            catch and retry the fi. Defaults to (Exception,).
        backoff (Callable[[float, int], float] | None, optional): The backoff 
            function. Accepts a callable with arguments for attempt and delay 
            values. Defaults to None.
    Raises:
        MaxRetryExceededError: If the retry attempts exceeded the value of 
            max_retries.
        TypeError: For incorrect argument types.
        ValueError: For incorrect argument values.

    Returns:
        Callable[..., Any]: The retry decorator or a partial retry function.
    """
    # Return a partial function if first argument is None
    if func is None:
        return partial(
            retry, 
            max_retries=max_retries, 
            delay=delay,
            max_delay=max_delay,
            jitter=jitter,
            exceptions=exceptions,
            backoff=backoff,            
        )
    
    # * Start of argument validations
    if not callable(func):
        raise TypeError(
            "First argument must be a callable function. Got `{}`."
            .format(type(func).__name__)
        )

    if not isinstance(max_retries, int):
        raise TypeError(
            "Type of `max_retries` must be `int`. Got `{}`."
            .format(type(max_retries).__name__)
        )

    if max_retries == 0:
        raise ValueError(
            "Value of `max_retries` must be a non-zero integer. Got `{}`."
            .format(max_retries)
        )

    if not isinstance(delay, float):
        raise TypeError(
            "Type of `delay` must `float`. Got `{}`."
            .format(type(delay).__name__)
        )

    if delay < 0:
        raise ValueError(
            "Value of `delay` must be a non-negative integer. Got `{}`."
            .format(delay)
        )
    
    if not isinstance(jitter, float):
        raise TypeError(
            "Type of `jitter` must be `float`. Got `{}`."
            .format(type(jitter).__name__)
        )
    
    if jitter < 0:
        raise ValueError(
            "Value of `jitter` must be a non-negative integer. Got `{}`."
            .format(jitter)
        )
    
    # Check exceptions are subclasses of Exception
    if not all(issubclass(exc, BaseException) for exc in exceptions):
        raise TypeError("Exceptions must all be subclasses of BaseException.")

    # Validate backoff if callable and two
    if callable(backoff):
        backoff_argspec = getfullargspec(backoff)
        if len(backoff_argspec.args) != 2:
            raise ValueError(
                "The `backoff` function must accept exactly 2 arguments."
            )
    elif backoff is not None:
        raise TypeError(
            "Type of `backoff` must be `Callable`. Got `{}`."
            .format(type(backoff).__name__)
        )
    # If backoff is None, declare a lambda function that returns the delay
    # value without modification due to backoff strategy.
    else:
        backoff = lambda delay, attempt: delay
        
    # If tries is negative, allow infinite retries. Use another variable to 
    # allow infinite values since only float allows this
    _max_retries: int | float = float("inf") if max_retries < 0 else max_retries 
    
    # * End of argument validations

    # Wrapper function for asynchronous functions.
    @wraps(func)
    async def async_wrapper(
        *args: Iterable[Any] | None,
        **kwargs: Mapping[str, Any] | None
    ) -> Any | None:
        attempts = 0
        while attempts < _max_retries:
            try:
                return await func(*args, **kwargs)
            except exceptions as exc:  # type: ignore
                attempts += 1
                if attempts == max_retries:
                    raise MaxRetryExceededError(
                        "Maximum number of retries ({}) exceeded."
                        .format(max_retries)
                    ) from exc

            total_delay = backoff(delay, attempts) + uniform(-jitter, jitter)
            if max_delay is not None:
                total_delay = min(total_delay, max_delay)

            await asleep(total_delay)

    # Wrapper function for synchronous functions.
    @wraps(func)
    def wrapper(
        *args: Iterable[Any] | None,
        **kwargs: Mapping[str, Any] | None
    ) -> Any:
        attempts = 0
        while attempts < _max_retries:
            try:
                return func(*args, **kwargs)
            except exceptions as exc:  # type: ignore
                attempts += 1
                if attempts == max_retries:
                    raise MaxRetryExceededError(
                        "Maximum number of retries ({}) exceeded."
                        .format(max_retries)
                    ) from exc
            
            total_delay = backoff(delay, attempts) + uniform(-jitter, jitter)
            if max_delay is not None:
                total_delay = min(total_delay, max_delay)

            sleep(total_delay)

    return async_wrapper if iscoroutinefunction(func) else wrapper