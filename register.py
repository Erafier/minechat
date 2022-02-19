import asyncio
import tkinter as tk

from main import ChatHandler


def register(username: str, description: tk.Label):
    handler = ChatHandler(host="minechat.dvmn.org", write_port=5050, read_port=5000)
    asyncio.run(handler.register(username))
    description["text"] = "Регистрация завершена успешно"


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Регистрация нового пользователя")
    description = tk.Label(width=30, height=3, text="Введите имя пользователя")
    description.pack()
    ent = tk.Entry(width=20)
    ent.pack()
    button = tk.Button(text="Создать пользователя")
    button['command'] = lambda: register(ent.get(), description=description)
    button.pack()
    root.mainloop()
