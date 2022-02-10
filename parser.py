import argparse

parser_reader = argparse.ArgumentParser(description="Minechat reader")
parser_reader.add_argument("--host", dest="host", default="minechat.dvmn.org",
                           help="")
parser_reader.add_argument("--port", dest="port", default=5000,
                           help="")
parser_reader.add_argument("--history", dest="history", default="minechat.history",
                           help="")

parser_writer = argparse.ArgumentParser(description="Minechat writer")
parser_writer.add_argument("message", help="message in chat")
parser_writer.add_argument("--host", dest="host", default="minechat.dvmn.org",
                           help="URL of minechat server")
parser_writer.add_argument("--port", dest="port", default=5050,
                           help="port of minechat server for writing messages")
parser_writer.add_argument("--token", dest="token", default="token.json",
                           help="path to user token (default to token.json)")
parser_writer.add_argument("--username", dest="username",
                           help="username for user registration. Required if token doesn't exist."
                                "Create new user token if parameter is present")
