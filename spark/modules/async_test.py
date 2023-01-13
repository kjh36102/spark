# import asyncio
# import itertools
# import sys

# async def spin(msg):
#     write, flush = sys.stdout.write, sys.stdout.flush
#     for char in itertools.cycle('|/-\\'):
#         status = char + ' ' + msg
#         write(status)
#         flush()
#         write('\x08' * len(status))
#         try:
#             await asyncio.sleep(.1)  # 1
#         except asyncio.CancelledError:  # 2
#             break
#     write(' ' * len(status) + '\x08' * len(status))

# async def slow_function():  # 3
#     await asyncio.sleep(3)  # 4
#     return 42

# async def supervisor():  # 5
#     spinner = asyncio.ensure_future(spin('thinking!'))  # 6
#     print('spinner object:', spinner)  # 7
#     result = await slow_function()  # 8
#     spinner.cancel()  # 9
#     return result

# def main():
#     loop = asyncio.get_event_loop()  # 10
#     result = loop.run_until_complete(supervisor())  # 11
#     loop.close()
#     print('Answer:', result)

# if __name__ == '__main__':
#     main()


import asyncio

async def test1():
    for i in range(5):
        print('test1:', i)
        await asyncio.sleep(1)
        
async def main():
    future = asyncio.ensure_future(test1())


loop = asyncio.get_event_loop()
result = loop.run_until_complete(main())
loop.close()

print('result:', result)