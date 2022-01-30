import asyncio

ACCOUNT_HASH = "70dda132-81b9-11ec-8c47-0242ac110002"


async def send_message(message):
    reader, writer = await asyncio.open_connection(
        "minechat.dvmn.org", 5050
    )
    # writer.write("Ghbdtn".encode())
    writer.write(ACCOUNT_HASH.encode() + "\n".encode())
    await writer.drain()
    answer = await reader.read(1000)
    print(answer)
    message += "\n\n"
    writer.write(message.encode())
    await writer.drain()
    # writer.close()
    # print(await reader.read(1000))


if __name__ == '__main__':
    asyncio.run(send_message("Привет"))
