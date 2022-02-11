# Minechat

Script for interacting with chat at minechat.dvmn.org

## Install

Script is not required any special packages. Only python 3.8 or above

## Usage

### Read chat messages

All arguments are optional

`python reader.py --host minechat.dvmn.org --port 5000 --history minechat.history`

### Write message to chat

Script contains only one required positional parameter - `message`. Other parameters are not required and set to default
values

* host = minechat.dvmn.org
* port = 5050
* token = token.json

If token file does not exist in working directory, registration will be offered. For this you have to execute script
with parameter `username`.
`python writer.py  Hey --username Bob`

If token exist you can authorize as existing user and send message
`python writer.py Hey`