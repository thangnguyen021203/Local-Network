import os
import json

file=open("download.jpg","rb")
file_size=os.path.getsize("download.jpg")

data=file.read()

filerec=open("test.jpg","wb")
filerec.write(data)


file.close()
filerec.close()

##############################################################################
# print(os.path.dirname(__file__))

# path=os.path.join(os.path.dirname(os.path.dirname(__file__)),"a.txt")

# print (path)

# if not (os.path.exists(path)):
#     with open(path, "w") as json_file:
#         json.dump({}, json_file)


####################################################################
# import bcrypt
# # store your password:
# password = (input("input password: "))
# # Encode the stored password:
# # password = password.encode('utf-8')
# # Encrypt the stored pasword:
# hashed = bcrypt.hashpw(password, bcrypt.gensalt(10))
# print(hashed)
# Create an authenticating password input field to check if a user enters the correct password
# check = str(input("check password: "))
# # Encode the authenticating password as well
# check = check.encode('utf-8')
# # Use conditions to compare the authenticating password with the stored one:
# if bcrypt.checkpw(check, hashed):
#     print("login successfull")
# else:
#     print("Passward invalid")


import os
def get_fname():
        list_fname = []
        for filename in os.listdir('ass/local-repo'):
            if os.path.isfile(os.path.join('ass/local-repo', filename)):
                list_fname.append(filename)
        return list_fname

for filename in get_fname():
    print(filename)