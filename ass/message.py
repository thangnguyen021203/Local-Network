import socket
import pickle
import sys
TYPE = ["regist","login", "fetch", "announce", "download"]


class header:
    type_msg = None
    username = None
    password = None
    port = None

    def __init__(self, type_msg, username=None, password=None, port=None):
        self.type_msg = type_msg
        self.username = username
        self.password = password
        self.port = port


class body:
    file_name = None
    content = None

    def __init__(self, content, file_name=None):
        self.content = content
        self.file_name = file_name


class Message:
    header = None
    body = None

    def __init__(
        self, type_msg, username, password, port, content, file_name
    ):
        self.header = header(type_msg, username, password, port)
        self.body = body(content, file_name)
    
    