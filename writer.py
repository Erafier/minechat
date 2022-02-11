import asyncio
import logging
import json
from typing import Optional

from parser import parser_writer

logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.basicConfig(
    format="%(levelname)s:%(filename)s:%(message)s",
    level=logging.DEBUG
)


class ChatHandler:
    logger = logging.getLogger()

    def __init__(self, host: str, port: int, token_file_name: str = "token.json"):
        self.port = port
        self.host = host
        self.token_file_name = token_file_name

    async def _init_connection(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port
        )

    async def _get_message_from_server(self) -> str:
        answer = await self.reader.read(1000)
        answer = answer.decode()
        self.logger.debug(answer)
        return answer

    async def _send_message_to_server(self, message: str):
        message = rf"{message}"
        message += "\n"
        self.writer.write(message.encode())
        await self.writer.drain()

    def _get_token_hash_from_file(self) -> str:
        with open(self.token_file_name, "r") as file:
            token = json.load(file)
        return token["account_hash"]

    @staticmethod
    def _parse_token_from_server(answer: str) -> Optional[dict]:
        return json.loads(answer.split("\n")[0])

    async def register(self, username: str):
        await self._init_connection()
        print("Введите имя нового пользователя")
        await self._send_message_to_server(username)
        answer = await self._get_message_from_server()
        token = self._parse_token_from_server(answer)
        with open(self.token_file_name, "w") as file:
            json.dump(token, file)

    async def authorize(self):
        await self._init_connection()
        await self._get_message_from_server()
        try:
            token_hash = self._get_token_hash_from_file()
        except FileNotFoundError:
            print("Токен не найден. Зарегистрируйте нового пользователя. \n"
                  "Для этого запустите скрипт с параметром --username")
        else:
            await self._send_message_to_server(token_hash)
            answer = await self._get_message_from_server()
            is_user_exist = self._parse_token_from_server(answer)
            if not is_user_exist:
                print("Неизвестный токен. Проверьте его или зарегистрируйте заново. \n"
                      "Для этого запустите скрипт с параметром --username")

    async def submit_message(self, message):
        await self._send_message_to_server(message + "\n")


async def main():
    args = parser_writer.parse_args()
    message, host, port, username, token = args.message, args.host, int(args.port), args.username, args.token
    chat_handler = ChatHandler(host, port, token)
    if username:
        await chat_handler.register(username)
    await chat_handler.authorize()
    await chat_handler.submit_message(message)


if __name__ == '__main__':
    asyncio.run(main())
