import asyncio
import datetime

import aiofiles


async def read_chat():
    reader, writer = await asyncio.open_connection(
        "minechat.dvmn.org", 5000
    )
    while True:
        message = await reader.read(1024)
        current_time = datetime.datetime.now().strftime("%d.%m.%y %H:%M")
        async with aiofiles.open("chat_log.txt", mode="a") as file:
            message = f"[{current_time}] {message.decode()}"
            print(message)
            await file.write(message)


if __name__ == '__main__':
    asyncio.run(read_chat())
