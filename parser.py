import argparse

parser = argparse.ArgumentParser(description="Minechat reader")
parser.add_argument("--host", dest="host", default="minechat.dvmn.org",
                    help="")
parser.add_argument("--port", dest="port", default=5000,
                    help="")
parser.add_argument("--history", dest="history", default="minechat.history",
                    help="")
