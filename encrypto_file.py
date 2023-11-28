import pandas as pd
from cryptography.fernet import Fernet
from data_process_func import *
"""
from cryptography.fernet import Fernet
key = Fernet.generate_key()
with open('mykey.key','wb') as mykey:
    mykey.write(key)

with open('mykey.key','rb') as filekey:
    key = filekey.read()
fernet = Fernet(key)

with open('credentials_2023new.csv','rb') as file:
    orgin = file.read()

encrypted = fernet.encrypt(orgin)

with open('encryp_cred_2023.csv','wb') as encryp_file:
    encryp_file.write(encrypted)

sz1,sz2 = file1.shape
for i in range(sz1):
    file1.iloc[i,1] = random_password_generator(8)
    


file1.to_csv('credentials.csv',index = False)

"""

#decrypting data
def checkpassword(username:str,password:str)->int:
    import pandas as pd
    from cryptography.fernet import Fernet
    from io import StringIO
    cred_dict = {}
    with open('mykey.key','rb') as filekey:
        key = filekey.read()
    fernet = Fernet(key)

    with open('encryp_cred_2023.csv','rb') as encrypt_file:
        encrep_data = encrypt_file.read()

    decrypted_data = fernet.decrypt(encrep_data)


    from io import StringIO
    s = str(decrypted_data,'utf-8')
    data = StringIO(s)
    df = pd.read_csv(data)
    sz1,_ = df.shape
    for i in range(sz1):
        cred_dict[df.iloc[i,0]]= df.iloc[i,1]
    
    if username not in cred_dict:
        return 0
    elif password!= cred_dict[username]:
        return 0

    try:
    
        record_login(username)
    except:
        pass
    if username =='admin':

        return 1
    else:

        return 2
    
    
    
    return 0


def random_password_generator(a:int)->str:
    import random
    import string
    
    password = ''.join([random.choice(string.ascii_letters + string.digits ) for n in range(a)])
    
    
    return password
    