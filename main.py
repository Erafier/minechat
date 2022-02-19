import asyncio
import json
import logging
import socket

import anyio
from anyio import create_task_group, run, sleep
from asyncio import Queue, open_connection
from datetime import datetime
from json import JSONDecodeError
from typing import Optional

import aiofiles
from async_timeout import timeout

import gui
from parser import parser

logging.basicConfig(level=logging.DEBUG)

TIMEOUT = 5
PING_PONG_TIMEOUT = 10


class ChatHandler:
    watchdog_logger = logging.getLogger("watchdog_logger")

    def __init__(
            self, host: str,
            read_port: int,
            write_port: int,
            token_file_name: str = "token.json",
            history_file: str = "minechat.history"
    ):
        self.read_port = read_port
        self.write_port = write_port
        self.host = host
        self.token_file_name = token_file_name
        self.history_file = history_file

        self.messages_queue = Queue()
        self.sending_queue = Queue()
        self.status_updates_queue = Queue()
        self.saved_messages_queue = Queue()
        self.watchdog_queue = Queue()
        self._load_messages_from_history()

    async def _init_connection(self):
        self.watchdog_queue.put_nowait("Establishing connection")
        self.status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.INITIATED)

        self.reader_r, _ = await open_connection(
            self.host, self.read_port
        )
        self.status_updates_queue.put_nowait(gui.ReadConnectionStateChanged.ESTABLISHED)

        self.status_updates_queue.put_nowait(gui.SendingConnectionStateChanged.INITIATED)
        self.reader_w, self.writer_w = await open_connection(
            self.host, self.write_port
        )
        self.status_updates_queue.put_nowait(gui.SendingConnectionStateChanged.ESTABLISHED)
        self.watchdog_queue.put_nowait("Connection is establish")

    async def _get_message_from_server(self) -> str:
        answer = await self.reader_w.read(1000)
        answer = answer.decode()
        print(answer)
        return answer

    def _get_token_hash_from_file(self) -> str:
        with open(self.token_file_name, "r") as file:
            token = json.load(file)
        return token["account_hash"]

    @staticmethod
    def _parse_token_from_server(answer: str) -> Optional[dict]:
        print(answer)
        return json.loads(answer.split("\n")[0])

    async def _send_message_to_server(self, message: str):
        message = rf"{message}"
        message += "\n"
        self.writer_w.write(message.encode())
        await self.writer_w.drain()

    def _load_messages_from_history(self):
        with open(self.history_file, mode="r") as file:
            while message := file.readline():
                self.messages_queue.put_nowait(message.strip())

    async def register(self, username: str):
        await self._init_connection()
        await self._get_message_from_server()
        await self._send_message_to_server("")
        answer = await self._get_message_from_server()
        await self._send_message_to_server(username)
        answer = await self._get_message_from_server()
        token = self._parse_token_from_server(answer)
        with open(self.token_file_name, "w") as file:
            json.dump(token, file)

    async def authorize(self):
        await self._get_message_from_server()
        try:
            token_hash = self._get_token_hash_from_file()
            await self._send_message_to_server(token_hash)
            answer = await self._get_message_from_server()
            is_user_exist = self._parse_token_from_server(answer)
            if not is_user_exist:
                raise gui.InvalidToken
            else:
                self.status_updates_queue.put_nowait(gui.NicknameReceived(is_user_exist["nickname"]))

        except (gui.InvalidToken, FileNotFoundError, JSONDecodeError):
            raise gui.InvalidToken
        await self.watchdog_queue.put("Authorization done")

    async def save_messages(self):
        while message := await self.saved_messages_queue.get():
            async with aiofiles.open(self.history_file, mode="a") as file:
                await file.write(message + "\n")

    async def read_msgs(self):
        while message := await self.reader_r.read(1024):
            current_time = datetime.now().strftime("%d.%m.%y %H:%M")
            message = f"[{current_time}] {message.decode().strip()}"
            async with create_task_group() as tg:
                tg.start_soon(self.messages_queue.put, message)
                tg.start_soon(self.saved_messages_queue.put, message)
                tg.start_soon(self.watchdog_queue.put, "New message in chat")

    async def handle_read(self):
        async with create_task_group() as tg:
            tg.start_soon(self.read_msgs)
            tg.start_soon(self.save_messages)

    async def submit_message(self, message):
        await self._send_message_to_server(message + "\n")

    async def send_msgs(self):
        await self.authorize()
        while message := await self.sending_queue.get():
            async with create_task_group() as tg:
                tg.start_soon(self.submit_message, message)
                tg.start_soon(self.watchdog_queue.put, "Message sent")
                tg.start_soon(self.ping_pong)

    async def _watch_for_connection(self):
        while True:
            try:
                async with timeout(TIMEOUT):
                    message = await self.watchdog_queue.get()
                    self.watchdog_logger.debug(f"[{datetime.now()}] Connection is alive. {message}")
            except asyncio.TimeoutError:
                self.watchdog_logger.debug(f"[{datetime.now()}] {TIMEOUT}s timeout is elapsed")
                raise ConnectionError

    async def ping_pong(self):
        while True:
            try:
                self.writer_w.write("\n".encode())
                await self.writer_w.drain()
                await self.reader_r.read()
                await sleep(PING_PONG_TIMEOUT)
            except socket.gaierror:
                self.watchdog_queue.put_nowait("Internet connection is lost")
                raise ConnectionError

    async def handle_connection(self):
        while True:
            try:
                await self._init_connection()
                async with create_task_group() as tg:
                    tg.start_soon(self._watch_for_connection)
                    tg.start_soon(self.handle_read)
                    tg.start_soon(self.send_msgs)

            except ConnectionError:
                self.watchdog_logger.debug("Reconnecting to server")
                await anyio.sleep(TIMEOUT)


async def main():
    args = parser.parse_args()
    host, read_port, write_port, history = args.host, int(args.read_port), int(args.write_port), args.history

    try:
        chat_handler = ChatHandler(host, read_port, write_port, history_file=history)

        async with create_task_group() as tg:
            tg.start_soon(gui.draw,
                          chat_handler.messages_queue,
                          chat_handler.sending_queue,
                          chat_handler.status_updates_queue
                          )
            tg.start_soon(chat_handler.handle_connection)
    except (gui.TkAppClosed, KeyboardInterrupt):
        print("App is closed")


if __name__ == '__main__':
    run(main)
