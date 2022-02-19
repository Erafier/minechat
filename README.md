# Minechat

Application for interacting with chat at minechat.dvmn.org

## Install

App required python 3.8 or above Installing required packages
`pip install -r requirements.txt`

## Usage

### Chat application

All arguments are optional

`python main.py --host minechat.dvmn.org --write_port 5050 --read_port 5000 --history minechat.history --token token.json`

### Register in chat

`python register.py`

After successful registration application creates file `token.json` with secret token 
