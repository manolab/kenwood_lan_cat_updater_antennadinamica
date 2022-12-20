# telnetdemo.py
import asyncio
from asyncio import StreamReader, StreamWriter

from kenwood_lan import KenwoodLan

KENWOOD_LOCK = asyncio.Lock()


async def ping():
    print("Ping")
    await asyncio.sleep(2)
    asyncio.create_task(ping())


async def echo(reader: StreamReader, writer: StreamWriter, k: KenwoodLan):
    print('New connection.')
    loop = asyncio.get_running_loop()
    try:
        while data := await reader.readline():
            async with KENWOOD_LOCK:
                command = data.decode('ascii').strip()
                output = await loop.run_in_executor(None, lambda: k.send_command(command))
                writer.write((output + "\n").encode('ascii'))
                await writer.drain()
        print('Leaving Connection.')

    except asyncio.CancelledError:
        print('Connection dropped!')


async def main(host, port, k):
    asyncio.create_task(ping())
    server = await asyncio.start_server(lambda r, w: echo(r, w, k), host, port)

    async with server:
        await server.serve_forever()


try:
    k = KenwoodLan("localhost", 8081, "admin", "admin")
    asyncio.run(main("127.0.0.1", 8888, k))
except KeyboardInterrupt:
    print('Bye!')
