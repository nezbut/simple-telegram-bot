import asyncio

async def test1():
    print('opa 1')
    await asyncio.sleep(2)
    print('opa 2')

async def test2():
    print('aaaaa')
    print('aaaaa')
    print('aaaaa')
    print('aaaaa')


async def main():
    tasks = [test1(), test2()]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())