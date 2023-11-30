import socket
from threading import Thread
import pickle
import os
import json
import sys
# import time
import message as msg

class server:
    host = None
    port = None
    serverSocket = None
    database = None

    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((self.host, self.port))

        # create database for sever
        if not (os.path.exists(self.database)):
            with open(self.database, "w") as json_file:
                json.dump({}, json_file)

    def listen(self, numberlisten):
        self.serverSocket.listen(numberlisten)
        print(f"Server {self.host} is listening...")

        while True:
            conn, addr = self.serverSocket.accept()
            nconn = Thread(target=self.Threadconnection, args=(conn, addr))
            nconn.start()
        
    def Threadconnection(self, conn, addr):
        print("Connect from ", addr)
        while True:
            try:
                message = self.receive_message(conn)
            except Exception as e:
                print(f"{addr[0]} has closed connection")
                conn.close()
                return None

            msgType=message.header.type_msg

            match msgType:
                case "regist":
                    self.regist(conn, addr[0], message.header.username, message.header.password, message.header.port) 
                case "login":
                    self.login(conn, addr[0], message.header.username, message.header.password)
                case "announce":
                    self.announce(addr[0], message.body.file_name)
                case "fetch":
                    self.fetch(conn, addr[0], message.body.file_name)

            
                
    def regist(self, conn, ipAddress, username, password, port):
        if self.checkExistIpAddress(ipAddress):
            # Send message to inform regist not success
            res = msg.Message(
                "regist", None, None, None,  "Your computer has already registed", None
            )
            self.send_message(conn,res)
        elif self.checkExistUsername(username):
            res = msg.Message(
                "regist", None, None, None,  "The username is existant", None
            )
            self.send_message(conn,res)
        else:
            # Send message to inform regist success
            res = msg.Message(
                "regist", None, None, None,  "Regist success", None
            )
            self.send_message(conn,res)
            print(f'Regist a new account, ip: {ipAddress}, username: {username}')

            # Append new account into serverdatabase
            user = {
                ipAddress: {
                    "Username": username,
                    "Password": password,
                    "Port": port,
                    "File in repository": []
                }
            }
            self.insertUserInfo(user)

    def login(self, conn, ipAddress, username, password):
        print(ipAddress," want to login")
        if self.checkExistIpAddress(ipAddress):
            with open(self.database, "r") as json_file:
                userinfo = json.load(json_file)
            if username!=userinfo[f'{ipAddress}']["Username"]:
                res = msg.Message(
                    "regist", None, None, None, "The account is not exist on this computer", None
                )
                self.send_message(conn,res)
                print(ipAddress," login not success")
            elif password != userinfo[f'{ipAddress}']["Password"]:
                res = msg.Message(
                    "regist", None, None, None, "Password is not correct", None
                )
                self.send_message(conn,res)
                print(ipAddress," login not success")
            else:
                res = msg.Message(
                    "regist", None, None, None, "Login success", None
                )
                self.send_message(conn,res)
                print(ipAddress," login success")
        else:
            res = msg.Message(
                "regist", None, None, None, "Your computer has not registed", None
            )
            self.send_message(conn,res)
            print(ipAddress," login not success")

    def announce(self, ipAddress, filename):
        print(ipAddress, f"has upload {filename} on local repository")
        ipaddress=ipAddress
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        userinfo[ipaddress]["File in repository"].append(filename)
        with open(self.database, "w") as json_file:
            json.dump(userinfo, json_file)

    def fetch(self, conn, ipAddress, filename):
        print(ipAddress, f"request file {filename}")
        listres=[]
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        for ipAdress in userinfo.keys():
            listfile=self.discover(ipAdress)
            for i in listfile:
                if i==filename:
                    if self.ping_host(ipAdress):
                        listres.append({"ipAdress":ipAdress, "port":userinfo[ipAdress]["Port"]})
                    break
        res = msg.Message(
            "regist", None, None, None, listres, None
        )
        self.send_message(conn,res)
        print(f"Server sent list ip address having {filename}")
    
    def discover(self, hostname):
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        if self.checkExistIpAddress(hostname):
            listFile=userinfo[hostname]["File in repository"]
            print(f"List files in {hostname}'s repository: {listFile}")
            return listFile
        print("Hostname is not regist account")
        return None

    def ping_host(self,hostname):
        response = os.system("ping -w 1 " + hostname)
        
        if response == 0:
            print (hostname, 'is live')
            return 1
        else:
            print (hostname, 'is not live')
            return 0

    def checkExistIpAddress(self, ipAddress):
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        if ipAddress in userinfo.keys():
            return True
        else:
            return False
        
    def checkExistUsername(self, username):
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
        for ipAddress in userinfo.keys():
            if(userinfo[ipAddress]["Username"]==username):
                return ipAddress
        return None

    def insertUserInfo(self, user):
        with open(self.database, "r") as json_file:
            userinfo = json.load(json_file)
            userinfo.update(user)
        with open(self.database, "w") as json_file:
            json.dump(userinfo, json_file)

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
                break
            hostname=input("Enter the hostname: ")
            if(option=="1"):
                Thread(target=self.discover, args=(hostname,)).start()
            elif(option=="2"):
                Thread(target=self.ping_host, args=(hostname,)).start()
            
    
if __name__ == "__main__":
    host=socket.gethostbyname(socket.gethostname())
    port=3000
    database = "serverdatabase.json"
    server = server(host, port, database)

    serverlisten=Thread(target=server.listen, args=(10,))
    serverlisten.setDaemon(True)
    serverlisten.start()

    server.mainthread()
