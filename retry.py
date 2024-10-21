from functools import wraps
from inspect import iscoroutinefunction, getfullargspec
from asyncio import sleep as async_sleep
from time import sleep
from random import uniform
from collections.abc import Callable, Iterable
from typing import Any


"""
This module provides a retry decorator that can be used to retry a function over
a list of exceptions for a specified number of attempts with a specified delay 
between each attempt.The decorator supports both synchronous and asynchronous 
functions.
"""

__version__ = "1.1.0"


class MaxRetryExceededError(Exception):
    """Exception raised when the maximum number of retries is exceeded."""
    pass


class retry:
    """
    Retry decorator that supports both synchronous and asynchronous functions.

    Sample Usage:
        @retry(max_retries=3, delay=1.0, exceptions=(ValueError,))
        def my_function():
            raise ValueError("Something went wrong")
        my_function() # Will be retried 3 times with a delay of 1.0 seconds

    Args:
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
        Callable[..., Any]: The retry decorator.
    """

    def __init__(
        self,
        *,
        max_retries: int = -1,
        delay: float = 0.0,
        max_delay: float | None = None,
        jitter: float = 0.0,
        exceptions: Iterable[type[BaseException]] | type[BaseException] = Exception,
        backoff: Callable[[float, int], float] | None = None,
    ) -> None:
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
        
        
        # Check if `exceptions` is a single exception or an iterable of exceptions
        if isinstance(exceptions, type):
            if not issubclass(exceptions, BaseException):
                raise TypeError(
                    "Type of `exceptions` must be a subclass of `BaseException`."
                    " Got `{}`"
                    .format(type(exceptions).__name__)
                )
            exceptions = (exceptions,)
        elif isinstance(exceptions, Iterable):
            # Ensure all are subclasses of BaseException   
            if not all(issubclass(exc, BaseException) for exc in exceptions):
                raise TypeError(
                    "Exceptions must all be subclasses of `BaseException`."
                )
        else:
            raise TypeError(
                "Exceptions must be a class or an iterable of classes derived "
                "from `BaseException`."
            )


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
            backoff = lambda delay, attempt: delay  # noqa: E731

        self.max_retries = max_retries
        self.delay = delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.exceptions = exceptions
        self.backoff = backoff


    def __call__(self, func: Callable[..., Any], /) -> Callable[..., Any]:
        if not callable(func):
            raise TypeError("The `func` argument must be callable.")
           
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            attempts = 0

            # If tries is negative, allow infinite retries. Use another variable to 
            # allow infinite values since only float allows this
            max_retries = self.max_retries if self.max_retries > 0 \
                else float("inf")

            while attempts <= max_retries:
                try:
                    # Execute function (sync or async based on wrapper)
                    return func(*args, **kwargs)
                
                except self.exceptions as exc: # type: ignore
                    attempts += 1

                    if attempts == max_retries:
                        raise MaxRetryExceededError(
                            "Maximum number of retries ({}) exceeded."
                            .format(self.max_retries)
                        ) from exc

                    # Calculate delay with optional backoff and jitter
                    delay = self.backoff(self.delay, attempts) if self.backoff \
                        else self.delay
                    delay += uniform(-self.jitter, self.jitter)

                    # Cap delay if max_delay is set
                    if self.max_delay is not None:
                        delay = min(delay, self.max_delay)

                    # Wait for the calculated delay
                    sleep(delay)

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            attempts = 0

            # If tries is negative, allow infinite retries. Use another variable to 
            # allow infinite values since only float allows this
            max_retries = self.max_retries if self.max_retries > 0 \
                else float("inf")

            while attempts <= max_retries:
                try:
                    # Execute function (sync or async based on wrapper)
                    return await func(*args, **kwargs)
                
                except self.exceptions as exc: # type: ignore
                    attempts += 1

                    if attempts == max_retries:
                        raise MaxRetryExceededError(
                            "Maximum number of retries ({}) exceeded."
                            .format(self.max_retries)
                        ) from exc

                    # Calculate delay with optional backoff and jitter
                    delay = self.backoff(self.delay, attempts) if self.backoff \
                        else self.delay
                    delay += uniform(-self.jitter, self.jitter)

                    # Cap delay if max_delay is set
                    if self.max_delay is not None:
                        delay = min(delay, self.max_delay)

                    # Wait for the calculated delay
                    await async_sleep(delay)

        return async_wrapper if iscoroutinefunction(func) else sync_wrapper