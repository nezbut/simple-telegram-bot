import aiohttp
import asyncio
from random import randint

async def request(number: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://numbersapi.com/{number}') as response:
            return await response.text()

async def while_true():
    while True:
        await asyncio.sleep(10)
        num = str(randint(1, 1_000_000))
        resp = await request(num)
        print(f"\n{resp}")


async def while_true2():
    loop = asyncio.get_running_loop()
    while True:
        inp = await loop.run_in_executor(None, input, 'Укажите число: ')

        if inp == 'exit':
            raise KeyboardInterrupt

        elif not inp.isdigit():
            print('Это не число')
            continue

        print(await request(inp))

async def main():
    async with asyncio.TaskGroup() as g:
        g.create_task(while_true())
        g.create_task(while_true2())


if __name__ == "__main__":
    asyncio.run(main())