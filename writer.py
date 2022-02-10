import asyncio
import logging
import json

import aiofiles

logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.basicConfig(
    format="%(levelname)s:%(filename)s:%(message)s",
    level=logging.DEBUG
)

ACCOUNT_HASH = "70dda132-81b9-11ec-8c47-0242ac110002ююююю"


async def register(reader, writer):
    print("Введите имя нового пользователя")
    name = input() + "\n"
    writer.write(name.encode())
    await writer.drain()
    answer = await reader.read(100)
    logging.debug(answer.decode())
    parsed_answer = json.loads(answer.decode().split("\n")[0])
    with open("token.json", "w") as file:
        json.dump(parsed_answer, file)


async def authorize(token=ACCOUNT_HASH):
    reader, writer = await asyncio.open_connection(
        "minechat.dvmn.org", 5050
    )
    writer.write(b"")
    await writer.drain()
    answer = await reader.read(100)
    logging.debug(answer.decode())
    writer.write(token.encode() + "\n".encode())
    await writer.drain()
    answer = await reader.read(100)
    logging.debug(answer.decode())
    parsed_answer = json.loads(answer.decode().split("\n")[0])
    if not parsed_answer:
        print("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
        await register(reader, writer)
        with open("token.json", "r") as file:
            token = json.load(file)

        await authorize(token["account_hash"])
    return reader, writer


async def send_message(reader, writer, message):
    message += "\n\n"
    writer.write(message.encode())
    await writer.drain()


if __name__ == '__main__':
    reader, writer = asyncio.run(authorize())
    while message := input():
        asyncio.run(send_message(reader, writer, message))
