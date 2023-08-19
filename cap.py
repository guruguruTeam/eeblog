from captcha.image import ImageCaptcha
import uuid
from tools import *

def makeCaptche():
    verification_code = getRandomString(4)
    img = ImageCaptcha().generate_image(verification_code)  # 想要生成的验证码abchef
    return img, verification_code

def verifyCap(cap_token, cap_answer, ip, username, c, con):
    # 查找是否存在这个token的验证码
    sql = 'select vercode,ctime,ip,username from captche where used="false" and token=?'
    c.execute(sql, (cap_token,))
    #fet = c.fetchone() if c.fetchone() else 'none'
    fet = c.fetchone()
    #fet[0] = fet[0].lower()
    cap_answer = cap_answer.lower()
    
    #if (fet!='none' and len(fet)!=0):
    if (str(fet)!='None' and len(fet)!=0):
        cap_time = dataTimeToTimeStamp(fet[1])
        now_time = dataTimeToTimeStamp(nowTime())
        if (int(cap_time)+5*60) < now_time:
            return {'code':-1, 'msg':'验证码已过期'}
        if (fet[0].lower()!=cap_answer):
            sql = 'UPDATE "captche" SET "used" = "true" WHERE token=?;'
            c.execute(sql, (cap_token,))
            con.commit()
            return {'code':-1, 'msg':'验证码不正确'}
        if (fet[2]!=ip):
            return {'code':-1, 'msg':'环境异常，ip不符'}
        if (fet[3]!=username and username!='none'):
            return {'code':-1, 'msg':'用户名不符'}
    else:
        return {'code':-1, 'msg':'验证码token不存在，请刷新重新获取'}
    sql = 'UPDATE "captche" SET "used" = "true" WHERE token=?;'
    c.execute(sql, (cap_token,))
    con.commit()
    return {'code':0, 'msg':'验证通过'}

def getCaptche(username, ip, c, con):
    img, vercode = makeCaptche()
    token = getRandomString(25)
    sql = 'insert into captche(vercode,token,ip,username,used) values(?,?,?,?,"false");'
    c.execute(sql, (vercode, token, ip, username))
    con.commit()
    path = 'static/captche/{}.png'.format(''.join(str(uuid.uuid4()).split('-')))
    img.save(path)
    return {'code':0, 'captche':path, 'token':token}

if __name__ == "__main__":
    import sqlite3
    # 连接sqlite
    con2 = sqlite3.connect('layim.db', check_same_thread=False)
    c2 = con2.cursor()
    print(getRandomString(4))
    print(int(dataTimeToTimeStamp('2022-12-13 11:11:46')))
    print(getCaptche('test', '0.0.0.0', c2, con2))
    #print(verifyCap('eaTT3EnNFbpOXsodZnM8Pd5ax', '6wxb', '0.0.0.0', 'test', c2, con2))