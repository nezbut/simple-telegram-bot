import aiohttp
import asyncio
from random import randint

# Request Function
async def request_to_numbers_api(number: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://numbersapi.com/{str(number)}') as response:
            return await response.text()

__all__ = (
    'request_to_numbers_api',
)