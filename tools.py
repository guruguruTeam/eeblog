import random
import time
import rsa
import uuid
import base64
import imghdr
import re
from PIL import Image


pubkey = '''
-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAJovC4AhDqF4LqAcgHWqdZcskpykM0uGm7yPuqmtKvyVhnAt22RKsYWB
SdHcK9COSPrjnXpLAYEbMRGJTbQWftICd04kY9SRyRIj68oZgWbv66B9QpT0X+1i
crHzlkoFpxo7kV17eBIXJSH42rUnEZh2Xonzzzz33GMojcPbCoB5AgMBAAE=
-----END RSA PUBLIC KEY-----
'''
prikey = '''
-----BEGIN RSA PRIVATE KEY-----
MIICYAIBAAKBgQCaLwuAIQ6heC6gHIB1qnWXLJKcpDNLhpu8j7qprSr8lYZwLdtk
SrGFgUnR3CvQjkj64516SwGBGzERiU20Fn7SAndOJGPUkckSI+vKGYFm7+ugfUKU
9F/tYnKx85ZKBacaO5Fde3gSFyUh+Nq1JxGYdl6J888899xjKI3D2wqAeQIDAQAB
AoGAEla0JHpKFjSIPy0Ernom4GNB0PXK0BnjniruRc4+Bar3QZKCvMwRj1KQaDCq
2XSDA6xdB7WyKRwF2xMcm/AfzuAusYWzRcboFUe3OnXIBoALDD5M43688t/C5PBy
w0aTczeLCsr3iDcXybUgITNpcGqwiRNMFlMzmjPa+/n9yYECRQDaQi7Z5FTln+Wm
h62ollehAAcKHFlID3bDkZ/ZQXbwoO3vB9Qc9RWFRUEYC2Q9cPZSFfEaTz0g5814
tpIBpnhRTCqbKQI9ALTYamc0WzdHYQ6AbKk6AZQw5rnZ+dgIi4Qj57KuGDOVBIPJ
hLV4a1NIQBoo9SWv/XxPl6InMwcqvAG00QJFAKGacXA6JTYkT3kfatCyCM4X5B5z
YRP/BzPFBnNpinSe462hwUdznGyiG5F/Fch8dJXQ00VkuGE94SBpJfB83wdq+v0J
Ajwfb38PcYppkX7NhoVc5ThhCh8RL1K+ur2FurgL1zddwAmI3v6yjLwbPfPmmDgE
1RK7CRrSlP3JwSPtKAECRCOTDgFoOCLz2nbD8ZrzjKgY3BELs/0MS0rZICKOO1tS
v6thZKXOq7sCF3JXCgRNE5T6D6ap4Vboinmji87d4SyONAAN
-----END RSA PRIVATE KEY-----
'''

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tif', 'webp', 'bmp', 'heic', 'svg'])

def getRandomString(randomlength=4):
    """
    生成一个指定长度的随机字符串
    """
    digits = '3456789' #012
    ascii_letters = 'abcdefghgkmnopqrstwxyzABCDEFGHJKMNOPQRSTWXYZ'#ijluvILUV
    str_list = [random.choice(digits + ascii_letters)
                for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str

def dataTimeToTimeStamp(datatime):
    timeArray = time.strptime(datatime, "%Y-%m-%d %H:%M:%S")
    timeStamp = time.mktime(timeArray)
    return timeStamp


def nowTime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

def sort_dict_ls(list):
    print('starting sort')
    for i in range(0, len(list)-1):
        for j in range(0, len(list)-i-1):
            if list[j]['num'] > list[j+1]['num']:
                temp = list[j]
                list[j] = list[j+1]
                list[j+1] = temp
    return list


def encrypt(msg):
    public_key = rsa.PublicKey.load_pkcs1(pubkey.encode())
    msg_bytes = msg.encode()
    encryptd_msg = b''
    chunk_size = len(msg_bytes) // 117 + 1
    for chunk_index in range(chunk_size + 1):
        chunk = msg_bytes[chunk_index * 117: (chunk_index + 1) * 117]
        encryptd_msg += rsa.encrypt(chunk, public_key)
    encryptd_msg_str = base64.b64encode(encryptd_msg).decode()
    return encryptd_msg_str


def decrypt(encryptd_msg_str):
    private_key = rsa.PrivateKey.load_pkcs1(prikey.encode())
    try:
        encryptd_msg = base64.b64decode(encryptd_msg_str.encode())
    except:
        return 'base64decode_error'
    chunk_size = len(encryptd_msg) // 128
    msg_bytes = b''
    for chunk_index in range(chunk_size):
        chunk = encryptd_msg[chunk_index * 128: (chunk_index + 1) * 128]
        try:
            msg_bytes += rsa.decrypt(chunk, private_key)
        except:
            return 'decrypt_error'
    return msg_bytes.decode()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def getFileExt(filename):
    return filename.rsplit('.', 1)[1]

def getUUID4():
    return ''.join(str(uuid.uuid4()).split('-'))

def findDictKeyFromList(key, value, ls):
    if len(ls) == 0:
        return -1
    for i in range(len(ls)):
        if key in ls[i] and ls[i][key] == value:
            return i
    return -1

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


def verifyImg(image_path):
    try:
        Image.open(image_path).verify()
        return True
    except:
        return False

def checkUsername(username):
    res = re.search(u'^[\u4e00-\u9fa5_a-zA-Z0-9]{1,24}$', username)
    if res:
        return True
    return False

def logAdminOp(admin_name, ip, op_type, msg,c,con, notice='暂无'):
    sql = 'insert into admin_op_log(admin_name,ip,type,msg,notice) values(?,?,?,?,?)'
    c.execute(sql, (admin_name,ip,op_type,msg,notice))
    con.commit()
    return 0

if __name__ == "__main__":
    pass