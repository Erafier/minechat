import argparse

parser = argparse.ArgumentParser(description="Minechat gui")
parser.add_argument("--host", dest="host", default="minechat.dvmn.org",
                    help="")
parser.add_argument("--read_port", dest="read_port", default=5000,
                    help="")
parser.add_argument("--write_port", dest="write_port", default=5050,
                    help="")
parser.add_argument("--history", dest="history", default="minechat.history",
                    help="")
parser.add_argument("--token", dest="token", default="token.json",
                    help="path to user token (default to token.json)")
