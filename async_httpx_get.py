# Tested on Python 3.12.0 with httpx==0.25.0
# This module provides asynchronous functions to get response data a URL or URLs.
# Run this module to test an example usage.

"""
Asynchronously get response data a URL or URLs.
"""

import asyncio
from itertools import batched
from typing import Coroutine

import httpx


async def get_data(
    url: str,
) -> Coroutine[None, None, httpx.Response]:
    """Asynchronously get response data from a URL. 

    Args:
        url (str): URL to get data from. 

    Returns:
        Coroutine[None, None, httpx.Response]: A coroutine that returns an
            httpx.Response object. 
            
    Raises:
        httpx.HTTPStatusError: Raised when the status code is not 200.
        httpx.RequestError: Raised when the request fails. 
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response
    except httpx.HTTPStatusError as e:
        return httpx.Response(status_code=e.response.status_code)
    except httpx.RequestError:
        return httpx.Response(status_code=500)
    

async def batched_get_data(
    urls: list[str],
    *,
    batch_len: int = 10,
) -> Coroutine[None, None, list[httpx.Response]]:
    """Asynchronously get response data from a list of URLs. 

    Args:
        urls (list[str]): List of URLs to get data from. 
        batch_len (int, optional): Batch length. Defaults to 10. 

    Returns:
        Coroutine[None, None, list[httpx.Response]]: A coroutine that returns a 
            list of httpx.Response objects.
    """
    # Split the list of URLs into batches of a specified size
    # and run the coroutine for each batch asynchronously
    responses = []
    for urls_batch in batched(urls, batch_len):
        tasks = [get_data(url.strip()) for url in urls_batch]
        responses.extend(await asyncio.gather(*tasks))
        
    return responses
    

if __name__ == "__main__":
    # Test this module by comparing the time it took to complete all requests
    # by changing the `batch_len` value from 1 to 20 
    from time import perf_counter
    
    # Change this value to change the batch size
    batch_len = 20  
    # Sample list of URLs
    urls = [
        "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
        "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
        "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html",
        "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html",
        "https://books.toscrape.com/catalogue/category/books/classics_6/index.html",
        "https://books.toscrape.com/catalogue/category/books/philosophy_7/index.html",
        "https://books.toscrape.com/catalogue/category/books/romance_8/index.html",
        "https://books.toscrape.com/catalogue/category/books/womens-fiction_9/index.html",
        "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html",
        "https://books.toscrape.com/catalogue/category/books/childrens_11/index.html",
        "https://books.toscrape.com/catalogue/category/books/religion_12/index.html",
        "https://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html",
        "https://books.toscrape.com/catalogue/category/books/music_14/index.html",
        "https://books.toscrape.com/catalogue/category/books/default_15/index.html",
        "https://books.toscrape.com/catalogue/category/books/science-fiction_16/index.html",
        "https://books.toscrape.com/catalogue/category/books/sports-and-games_17/index.html",
        "https://books.toscrape.com/catalogue/category/books/add-a-comment_18/index.html",
        "https://books.toscrape.com/catalogue/category/books/fantasy_19/index.html",
        "https://books.toscrape.com/catalogue/category/books/new-adult_20/index.html",
        "https://books.toscrape.com/catalogue/category/books/young-adult_21/index.html",
        "https://books.toscrape.com/catalogue/category/books/science_22/index.html",
        "https://books.toscrape.com/catalogue/category/books/poetry_23/index.html",
        "https://books.toscrape.com/catalogue/category/books/paranormal_24/index.html",
        "https://books.toscrape.com/catalogue/category/books/art_25/index.html",
        "https://books.toscrape.com/catalogue/category/books/psychology_26/index.html",
        "https://books.toscrape.com/catalogue/category/books/autobiography_27/index.html",
        "https://books.toscrape.com/catalogue/category/books/parenting_28/index.html",
        "https://books.toscrape.com/catalogue/category/books/adult-fiction_29/index.html",
        "https://books.toscrape.com/catalogue/category/books/humor_30/index.html",
        "https://books.toscrape.com/catalogue/category/books/horror_31/index.html",
        "https://books.toscrape.com/catalogue/category/books/history_32/index.html",
        "https://books.toscrape.com/catalogue/category/books/food-and-drink_33/index.html",
        "https://books.toscrape.com/catalogue/category/books/christian-fiction_34/index.html",
        "https://books.toscrape.com/catalogue/category/books/business_35/index.html",
        "https://books.toscrape.com/catalogue/category/books/biography_36/index.html",
        "https://books.toscrape.com/catalogue/category/books/thriller_37/index.html",
        "https://books.toscrape.com/catalogue/category/books/contemporary_38/index.html",
        "https://books.toscrape.com/catalogue/category/books/spirituality_39/index.html",
        "https://books.toscrape.com/catalogue/category/books/academic_40/index.html",
        "https://books.toscrape.com/catalogue/category/books/self-help_41/index.html",
        "https://books.toscrape.com/catalogue/category/books/historical_42/index.html",
        "https://books.toscrape.com/catalogue/category/books/christian_43/index.html",
        "https://books.toscrape.com/catalogue/category/books/suspense_44/index.html",
        "https://books.toscrape.com/catalogue/category/books/short-stories_45/index.html",
        "https://books.toscrape.com/catalogue/category/books/novels_46/index.html",
        "https://books.toscrape.com/catalogue/category/books/health_47/index.html",
        "https://books.toscrape.com/catalogue/category/books/politics_48/index.html",
        "https://books.toscrape.com/catalogue/category/books/cultural_49/index.html",
        "https://books.toscrape.com/catalogue/category/books/erotica_50/index.html",
        "https://books.toscrape.com/catalogue/category/books/crime_51/index.html",
    ]

    t0 = perf_counter()  # Start of timer
    results = asyncio.run(batched_get_data(urls, batch_len=batch_len))
    dt =  perf_counter() - t0  # Elapsed time from start and end timer
    print(f"Done in {dt:.5f}s")