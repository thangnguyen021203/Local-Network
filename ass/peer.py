import socket
from threading import Thread
import pickle
import message as msg
import time
import sys
import os
import shutil

_SERVER_PORT = 3000
_PEER_PORT = 5001
_SERVER_HOST = "192.168.137.170"
_LOCAL_FILE_SYSTEM = './local-system/'
_LOCAL_REPOSITORY = './ass/local-repo/'


class peer_peer:
    
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port =_PEER_PORT
        
        
    def receive_message_from(self,conn):
        received_data = int(pickle.loads(conn.recv(1024)))
        res = pickle.loads(conn.recv(received_data))
        return res
    
    def send_message(self, conn, msg):
        conn.sendall(pickle.dumps(f"{sys.getsizeof(pickle.dumps(msg))}"))
        conn.sendall(pickle.dumps(msg))
    
    def Threadlisten(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip,self.port))
        self.socket.listen(5)
        while True:
            conn, addr = self.socket.accept()
            nconn = Thread(target=self.listen, args=(conn,))
            nconn.start()
    
    def listen(self, conn):
        query = self.receive_message_from(conn)
        file_get = query.body.file_name
        
        #protocol transfer file
        print(f"{file_get} transferred success.")
    
    def send(self, host, file_name):
        conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, _PEER_PORT))
        
        message = msg.Message("download",username,password,_PEER_PORT,None,file_name)
        
        self.send_message(conn, message)
        
        
    
    
class peer_server:
    def __init__(self):
        # self.ip = socket.gethostbyname(socket.gethostname())
        # self.port = 3001
        self.username=None
        self.password=None
        self.status = "OFF"
      
    def connect(self, host, port):
        conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, port))
        return conn
        
    def peer_client_program(self,host,port):
        conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, port))
        
    def login_message(self,conn,username,password):
        message = msg.Message("login",username,password,_PEER_PORT,None,None)
        self.send_message(conn,message)
        #message.send_message(conn)
        response = self.receive_message_from(conn).body.content
        print(response)
        if (response == 'Login success'):
            self.username = username
            self.password = password
            self.status = "ON"

    def regist_message(self, conn,username,password):
        message = msg.Message("regist",username,password,_PEER_PORT,None,None)
        self.send_message(conn,message)
        #message.send_message(conn)
        response = self.receive_message_from(conn).body.content
        print(response)
        if (response == " Regist success"):
            if not os.path.exists('./ass/local-repo'):
        # If not existed, create new folder 
                os.makedirs('./ass/local-repo')
            self.username = username
            self.password = password
            self.status = "ON"
     
    def receive_message_from(self,conn):
        received_data = int(pickle.loads(conn.recv(1024)))
        res = pickle.loads(conn.recv(received_data))
        return res
    
    def send_message(self, conn, msg):
        conn.sendall(pickle.dumps(f"{sys.getsizeof(pickle.dumps(msg))}"))
        conn.sendall(pickle.dumps(msg))
        
    def publish(self, conn, lname, fname):
        if not os.path.exists(f'./local-system/{lname}'):
            print(f'There is no file named: {lname} in your local file system!')
        else:
            #coppy original file to local repository
            shutil.copy(_LOCAL_FILE_SYSTEM+ f'{lname}',  _LOCAL_REPOSITORY+ f'{fname}')
            
            #Convey server
            message = msg.Message("announce",None,None,_PEER_PORT,None,fname)     
            self.send_message(conn,message) 

    def fetch(self, conn, fname):
        message = msg.Message("fetch",None,None,_PEER_PORT,None,fname)     
        self.send_message(conn,message)
        response = self.receive_message_from(conn)
        print(response.body.content)
        
    
    
    def controller(self, conn):
        while True:
            input_command = input("Enter a command: ").split()
            match input_command[0]:
                case "help":
                    print("""
                        Command format: command "parameter1" "parameter2" ...
                        List of command:
                        > stop: stop the client
                        > publish "lname" "fname": a local file (which is stored in the client's file system at "lname") is added to the 
                            client's repository as a file named "fname" and this information is conveyed to the server
                        > fetch "file name": fetch some copy of the target file and add it to the local repository
                        > download "index": download the file with the index <index> return from the fetch command to local repository on your computer""");
                case "stop":
                    return
                case "fetch":
                    if len(input_command) != 2:
                        print("Invalid command. Type 'help' for more information.")
                    else:
                        self.fetch(conn,input_command[1])
                case "publish":
                    if len(input_command) < 3:
                        print("Invalid command. Type 'help' for more information.")
                    else:
                        self.publish(conn, input_command[1], input_command[2]);
                case "download":
                    if len(input_command) != 3:
                        print("Invalid command. Type 'help' for more information.")
                    else:
                        peer_download = peer_peer()
                        Thread(target=peer_download.send, args=(input_command[1] ,input_command[2])).start()
                case default:
                    print("Invalid command. Type 'help' for more information.")
            time.sleep(1)
    


if __name__ == '__main__':
    peer_server = peer_server()
    p2p = peer_peer()

    Thread(target=p2p.Threadlisten, args=()).start()

    conn = peer_server.connect(_SERVER_HOST,_SERVER_PORT)
    # peer.peer_client_program(_SERVER_HOST,_SERVER_PORT)
    
    #LOGIN
    option = input("Login: 1\nRegist: 2\n")
    if (option == '1' or option == '2'):
        username = input("Input your username: ")
        password = input("Input your password: ")

    if (option == '1'):
        peer_server.login_message(conn, username,password)
    if (option == '2'):
        peer_server.regist_message(conn, username, password)
        
    if peer_server.status == "ON":
        peer_server.controller(conn)
    
    
    # print(conn.recv(1024).decode())
    # while True:
    #     datainput=input("Add list, Get list or Exit: " )
    #     if datainput=="Add list":
    #         conn.
    # (datainput.encode())
    #         conn.send(str(port).encode()) 
    #         print(conn.recv(1024).decode())                                 
    #     # if datainput=="Get list":
    #     #     conn.send(datainput.encode())
    #     #     portlist=pickle.loads(conn.recv(1024))
    #     #     for lport in portlist:
    #     #         if lport!=port:
    #     #             lconn=socket.socket()
    #     #             lconn.connect((socket.gethostname(),lport))
    #     #             lconn.send((f"\nHello from {port}").encode())
    #     #     print(conn.recv(1024).decode())
    #     if datainput=="Exit":
    #         conn.close()
    #         break