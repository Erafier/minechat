import asyncio
import datetime

import aiofiles

from parser import parser
from writer import send_message


async def read_chat(host, port, history):
    reader, writer = await asyncio.open_connection(
        host, port
    )
    while True:
        message = await reader.read(1024)
        current_time = datetime.datetime.now().strftime("%d.%m.%y %H:%M")
        async with aiofiles.open(history, mode="a") as file:
            message = f"[{current_time}] {message.decode()}"
            print(message)
            await file.write(message)


async def main():
    args = parser.parse_args()
    host, port, history = args.host, int(args.port), args.history
    await asyncio.gather(
        read_chat(host, port, history),
        send_message("Привет")
    )
    # asyncio.run(read_chat(host, port, history))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
