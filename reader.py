import asyncio
import datetime

import aiofiles

from parser import parser


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


def main():
    args = parser.parse_args()
    host, port, history = args.host, int(args.port), args.history
    asyncio.run(read_chat(host, port, history))


if __name__ == '__main__':
    main()
