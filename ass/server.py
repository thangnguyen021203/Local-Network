import socket
from threading import Thread
import pickle
import os
import json
import sys
import queue
import threading
import message as msg
import bcrypt


class Server:
    host = None
    port = None
    serverSocket = None
    database_path = None
    server_on = True

    def __init__(self, host, port, database_name):
        self.host = host
        self.port = port
        # self.database_path = database_path
        self.database_path = os.path.join(os.path.dirname(__file__),"..",database_name)

        # create socket for server
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((self.host, self.port))

        # Create queue to store events related to the server.
        self.output_queue = queue.Queue()
        self.queue_mutex = threading.Lock()
        
        # create database for sever
        if not (os.path.exists(self.database_path)):
            with open(self.database_path, "w") as json_file:
                json.dump({}, json_file)
        self.db_mutex = threading.Lock()

    # function to put events to queue
    def putQueueRequire(self, hostname, require, status):
        self.queue_mutex.acquire()
        self.output_queue.put(f"Hostname: {hostname}\nRequire: {require}\nStatus: {status}\n>>\n")
        self.queue_mutex.release()
    
    def putQueueMessage(self,message):
        self.queue_mutex.acquire()
        self.output_queue.put(f"{message}\n>>\n")
        self.queue_mutex.release()

    def listen(self, numberlisten):
        self.serverSocket.listen(numberlisten)
        print(f"Server {self.host}, port = {self.port} is listening...")
        self.putQueueMessage(f"Server {self.host} is listening...")
        while True:
            try:
                conn, addr = self.serverSocket.accept()
            except socket.error as e:
                if not self.server_on:
                    print(f"Server {self.host} is offline")
                    return
                else:
                    print(f"An error occurred: {e}")
                    return
                    
            Thread(target=self.Threadconnection, args=(conn, addr), daemon=True).start()
        
    def Threadconnection(self, conn, addr):
        print("Connect from ", addr)
        self.putQueueMessage(f"Connect from {addr}")
        while True:
            try:
                message = self.receive_message(conn)
            except ConnectionError:
                print(f"{addr[0]} has closed connection")
                self.putQueueMessage(f"{addr[0]} has closed connection")
                conn.close()
                return None
            except Exception as e:
                print(f"An error occurred: {e}")
                self.putQueueMessage(f"An error occurred: {e}")
                conn.close()
                return None

            self.handle_message_type(conn, addr[0], message)

    def handle_message_type(self, conn, ip_address, message):
        msg_type = message.header.type_msg

        match msg_type:
            case "regist":
                self.regist(conn, ip_address, message.header.username, message.header.password, message.header.port)
            case "login":
                self.login(conn, ip_address, message.header.username, message.header.password)
            case "announce":
                self.announce(ip_address, message.body.file_name)
            case "fetch":
                self.fetch(conn, ip_address, message.body.file_name)

    def userInfo(self):
        self.db_mutex.acquire()
        with open(self.database_path, "r") as json_file:
            userinfo = json.load(json_file)
        self.db_mutex.release()
        return userinfo

    def regist(self, conn, ipAddress, username, password, port):
        if self.checkExistIpAddress(ipAddress):
            res = msg.Message(
                "regist", None, None, None,  "Your computer has already registed", None
            )
            print(ipAddress," regist not success")
            # self.putQueueRequire(f'{ipAddress} regist not success')
            self.putQueueRequire(ipAddress,'Regist','Not success')
        elif self.checkExistUsername(username):
            res = msg.Message(
                "regist", None, None, None,  "The username is existant", None
            )
            print(ipAddress," regist not success")
            # self.putQueueRequire(f'{ipAddress} regist not success')
            self.putQueueRequire(ipAddress,'Regist','Not success')
        else:
            res = msg.Message(
                "regist", None, None, None,  "Regist success", None
            )
            print(f'Regist a new account, ip: {ipAddress}, username: {username}')
            # self.putQueueRequire(f'{ipAddress} regist success')
            self.putQueueRequire(ipAddress,'Regist','Success')

            hashpassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
            user = {
                ipAddress: {
                    "Username": username,
                    "Password": hashpassword.decode('utf-8'),
                    "Port": port,
                    "File in repository": []
                }
            }
            self.insertUserInfo(user)

        self.send_message(conn,res)

    def login(self, conn, ipAddress, username, password):
        if self.checkExistIpAddress(ipAddress):
            userinfo = self.userInfo()

            if username!=userinfo[f'{ipAddress}']["Username"]:
                res = msg.Message(
                    "regist", None, None, None, "The account is not exist on this computer", None
                )
                print(ipAddress," login not success")
                # self.putQueueRequire(f'{ipAddress} login not success')
                self.putQueueRequire(ipAddress,'Login','Not success')
            elif not bcrypt.checkpw(password.encode('utf-8'),userinfo[f'{ipAddress}']["Password"].encode('utf-8')):
                res = msg.Message(
                    "regist", None, None, None, "Password is not correct", None
                )
                print(ipAddress," login not success")
                # self.putQueueRequire(f'{ipAddress} login not success')
                self.putQueueRequire(ipAddress,'Login','Not success')
            else:
                res = msg.Message(
                    "regist", None, None, None, "Login success", None
                )
                print(ipAddress," login success")
                # self.putQueueRequire(f'{ipAddress} login not success')
                self.putQueueRequire(ipAddress,'Login','Success')
        else:
            res = msg.Message(
                "regist", None, None, None, "Your computer has not registed", None
            )
            print(ipAddress," login not success")
            # self.putQueueRequire(f'{ipAddress} login success')
            self.putQueueRequire(ipAddress,'Login','Not success')
        
        self.send_message(conn,res)

    def announce(self, ipAddress, filename):
        print(ipAddress, f"has upload {filename} on local repository")
        # self.putQueueRequire(f'{ipAddress} has upload {filename} on local repository')
        ipaddress=ipAddress

        self.db_mutex.acquire()
        with open(self.database_path, "r") as json_file:
            userinfo = json.load(json_file)
        userinfo[ipaddress]["File in repository"].append(filename)
        with open(self.database_path, "w") as json_file:
            json.dump(userinfo, json_file)
        self.db_mutex.release()

        self.putQueueRequire(ipAddress, f'Announce has uploaded {filename}', 'Success')


    def fetch(self, conn, ipAddress, filename):
        print(ipAddress, f"request file {filename}")
        # self.putQueueRequire(f'{ipAddress} request file {filename}')
        
        listres=[]

        userinfo = self.userInfo()
        
        for ipAddr in userinfo.keys():
            listfile=userinfo[ipAddr]["File in repository"]
            if filename in listfile:
                if self.ping_host(ipAddr):
                    listres.append({"ipAdress":ipAddr, "port":userinfo[ipAddr]["Port"]})

        if(listres!=[]):
            res = msg.Message(
                "regist", None, None, None, listres, None
            )
            self.send_message(conn,res)
            print(f"Server sent to {ipAddress} list ip address having {filename}")
            self.putQueueRequire(ipAddress, f'Fetch {filename}', 'Success')

        else:
            res = msg.Message(
                "regist", None, None, None, f"There is no live account having the {filename}", None
            )
            self.send_message(conn,res)
            print(f"The server cannot find an live account containing the file {filename}")
            self.putQueueRequire(ipAddress, f'Fetch {filename}', f'Not find an live account having file {filename}')

    
    def discover(self, hostname):
        userinfo = self.userInfo()

        if hostname in userinfo.keys():
            listFile=userinfo[hostname]["File in repository"]
            print(f"List files in {hostname}'s repository: {listFile}")
            self.result=f"List files in {hostname}'s repository: {listFile}\n"
            return listFile
        print(f"Hostname is not regist account\n")
        self.result=f"Hostname is not regist account\n"
        return None

    def ping_host(self,hostname):
        response = os.system("ping -w 1 " + hostname)
        if response == 0:
            print (hostname, 'is live')
            self.result=f"{hostname} is live\n"
            return True
        else:
            print (hostname, 'is not live')
            self.result=f"{hostname} is not live\n"
            return False

    def checkExistIpAddress(self, ipAddress):
        userinfo = self.userInfo()
        if ipAddress in userinfo.keys():
            return True
        else:
            return False   
        
    def checkExistUsername(self, username):
        userinfo = self.userInfo()
        for ipAddress in userinfo.keys():
            if(userinfo[ipAddress]["Username"]==username):
                return ipAddress
        return None

    def insertUserInfo(self, user):
        self.db_mutex.acquire()
        with open(self.database_path, "r") as json_file:
            userinfo = json.load(json_file)
            userinfo.update(user)
        with open(self.database_path, "w") as json_file:
            json.dump(userinfo, json_file)
        self.db_mutex.release()

    def send_message(self, conn, msg):
        conn.send(pickle.dumps(f"{sys.getsizeof(pickle.dumps(msg))}"))
        conn.send(pickle.dumps(msg))

    def receive_message(self,conn):
        received_data = pickle.loads(conn.recv(1024))
        mgs=b''
        while not(mgs):
            mgs=conn.recv(int(received_data))
        res = pickle.loads(mgs)
        return res

    def mainthread(self):
        while True:
            option=input("Enter your option:\n1. Discover the list of local files of the hostname\n2. Live check the hostname\n3. Close Server\n")
            if(option=="3"):
                self.close()
                break
            hostname=input("Enter the hostname: ")
            if(option=="1"):
                Thread(target=self.discover, args=(hostname,)).start()
            elif(option=="2"):
                Thread(target=self.ping_host, args=(hostname,)).start()
                
    
    def run(self,opcode,hostname):
        if(opcode=="DISCOVER"):
            self.discover(hostname)
            return self.result

        elif(opcode=="PING"):
            self.ping_host(hostname)
            return self.result
    
    def close(self):
        self.server_on = False
        self.serverSocket.close()
    
if __name__ == "__main__":
    host=socket.gethostbyname(socket.gethostname())
    port=3000
    databaseName = "serverdatabase.json"
    server = Server(host, port, databaseName)
    Thread(target=server.listen, args=(10,)).start()
    server.mainthread()
