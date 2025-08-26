import asyncio
from random import randint



async def async_sleep(sleep_range: list):
    await asyncio.sleep(randint(*sleep_range))
