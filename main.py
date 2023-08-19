# main.py
# -*- coding: UTF-8 -*-

from flask import Flask,jsonify,request,render_template,send_file
from flask import redirect, url_for, flash, session, make_response
from flask_limiter import Limiter
import sqlite3
import logging
from json import dump,load
from codecs import open
from time import time
from os import path,listdir
from tools import *
import cap
from funclimiter import funclimiter
from flask_session import Session
from redis import Redis
import IPy

# 连接sqlite
con = sqlite3.connect('sqlite.db', check_same_thread=False)
c = con.cursor()
def getIP():
    return str(request.headers.get("X-Real-IP", request.remote_addr))

def test(path_):
    if not path.exists(path_):
        dump((),load_(path_,"w"))

    return path_

def load_(file,mode="r"):
    return open(file,mode,"UTF-8-sig")

def time_(path_):
    return round(path.getmtime(path_))

def getComment(note):
    sql = 'select nickname,content,ctime from comment where note=?;'
    c.execute(sql, (note,))
    fet = c.fetchall()
    ls = []
    for f in fet:
        ls.append((f[0],f[1],f[2]))
    return ls


# ------------全局变量------------
admin_username = 'ee'
admin_password = 'ee4514'

redis_uri = "redis://127.0.0.1:6379/"
redis_passwd = 'redispassword'
# redis设置密码：config set requirepass redispassword
app=Flask("guru",template_folder="client")
app.secret_key="guru"
method=("POST","GET")
app.config['SESSION_TYPE'] = 'redis'   #session存储格式为redis
app.config['SESSION_REDIS'] = Redis(password=redis_passwd)
app.config['SESSION_USE_SIGNER'] = True   #是否强制加盐，混淆session
app.config['SECRET_KEY'] = app.secret_key  #如果加盐，那么必须设置的安全码，盐
app.config['SESSION_PERMANENT'] = True  #sessons是否长期有效，false，则关闭浏览器，session失效
app.config['PERMANENT_SESSION_LIFETIME'] = 36000   #session长期有效，则设定session生命周期，整数秒，
Session(app)
bantypes = ['ip','word']
auxiliary_ban = {}
limiter = Limiter(app, key_func=getIP, default_limits=["1 per second"], storage_uri=redis_uri, storage_options={"password": redis_passwd})

@app.before_request
def before_request_func():
    if request.path.startswith('/admin/') and not request.path.startswith('/admin/login'):
        if 'ADMIN_NAME' not in session:
            return '仅允许管理员访问'
    
    ipcheck_ret = checkBan('ip', getIP())
    if ipcheck_ret != 'pass':
        return '您已被禁止访问！'

@app.errorhandler(Exception)
def error(error):
    return render_template("404.html")

@app.route('/captche', methods=['POST'])
def captche():
    ip = getIP()
    ret = cap.getCaptche('none', ip, c, con)
    print(ret)
    return jsonify(ret)

@app.route("/",methods=method)
@limiter.limit("5/minute")
def index():
    sql = 'select title,mtime,type from context;'
    c.execute(sql)
    fet = c.fetchall()

    list_ = []
    list__ = []
    for f in fet:
        print(f)
        if f[2] == 'note':
            list_.append((f[0], f[1]))
        else:
            list__.append(f[0])

    #data=sorted(list_,key=lambda essay:essay[1],reverse=True)
    bing="</a><a href='".join([f"/article/notes/{file_[0]}'>{file_[0]}" for file_ in list_]+[f"/article/pages/{file_}'>{file_}" for file_ in list__])
    print(list_, 'aaa', list__, 'aaa''aaa', bing)
    return render_template("index.html",data=(list_,list__),bing="<a href='"+bing+"</a>")

@app.route("/article/<path:folder>/<path:file>",methods=method)
def essay(folder,file):
    sql = 'select title,mtime,tags,content from context where type=? and title=?;'
    c.execute(sql, (folder[:-1], file))
    fet = c.fetchone()
    text="#"+fet[3].split("#",1)[-1]
    print(getComment(file))
    data=(folder,file,text,fet[1],getComment(file))
    return render_template("essay.html",folder=folder,title=file,data=data,bing=text[:min(50,len(text))].replace("\n","\\n")+"……")

@app.route("/files/<path:folder>/<path:file>",methods=method)
@limiter.limit("5/second")
def file(folder,file):
    #return send_file(f"{folder}/{file}")
    print(folder, file)
    sql = 'select content from context where type=? and title=?;'
    c.execute(sql, (folder[:-1], file))
    fet = c.fetchone()[0]
    return jsonify(fet)

@app.route("/comment",methods=method)
@limiter.limit("5/minute")
def comment():
    form=request.form
    print(form.get('note'))
    note=form.get("note","")
    list_=(form.get("nick",""),form.get("text",""), nowTime())

    if not all(list_):
        return jsonify((0,"评论","昵称/评论内容可能不完善？"))

    if not list_[0].isalnum() or len(list_[0])>12:
        return jsonify((0,"评论","用数字/字母/汉字取个12字内的昵称吧！"))
    
    commentcheck_ret = checkBan('word', list_[0])
    if commentcheck_ret != 'pass':
        return jsonify((0,'评论','您输入的昵称包含屏蔽词，请修改。'))
    commentcheck_ret = checkBan('word', list_[1])
    if commentcheck_ret != 'pass':
        return jsonify((0,'评论','您输入的内容包含屏蔽词，请修改。'))

    sql = 'select count(ctime) from context where title=?;'
    c.execute(sql, (note,))
    fet = c.fetchone()[0]
    if int(fet)==0:
        return jsonify((0,"评论","呃 找不到这篇笔记……"))

    sql = 'insert into comment(nickname,note,content,ip) values(?,?,?,?);'
    c.execute(sql, (list_[0], note, list_[1], getIP()))
    con.commit()
    return jsonify((1,"评论","评论发送成功！",list_))

# -------------admin----------------
# 别问鱼为什么不写到另一个文件里，因为鱼在飞机上没办法上网而且不会（划掉
# 吐槽：南航这个787真不要太烂，787这么新的飞机，南航把它搞的连空联网都没有，位置还这么挤，qswl
@app.route('/admin/login',methods=method)
def adminLogin():
    username = request.args['username']
    password = request.args['password']
    cap_token = request.args['cap_token']
    cap_answer = request.args['vercode']
    remember_password = request.args['remember_password']
    need_decrypt = request.args['need_decrypt']
    ip = getIP()
    verify_ret = cap.verifyCap(cap_token, cap_answer, ip, 'none', c, con)
    if (verify_ret['code'] !=0):
        return jsonify(verify_ret)

    if (need_decrypt == 'true'):
        decrypted_password = decrypt(password).split('|')[0]
        if (decrypted_password!='base64decode_error' and decrypted_password!=''):
            password = decrypted_password
    
    
    if not(username==admin_username and password==admin_password):
        msg = {'code': -1, 'msg': '未找到该用户，请核实账号或密码'}
        return jsonify(msg)
    session['ADMIN_NAME'] = username
    msg = {'code': 0, 'msg': '登录成功', 'encrypted_password':'', 'username':username}
    if (remember_password == 'true'):
        msg['encrypted_password'] = encrypt("{}|{}".format(password, ip))

    # 记录本次登录ip、时间
    logAdminOp(username, getIP(), 'adminLogin', '登陆了管理员后端', c,con)
    return jsonify(msg)

@app.route('/admin')
def gotoAdmin():
    if 'ADMIN_NAME' not in session:
        return render_template('background/login.html')
    return render_template('background/index.html')

@app.route('/admin/logout')
def adminLogout():
    session.clear()
    return redirect('/')

def loadBeforeStart():
    for select_l in bantypes:
        auxiliary_ban[select_l] = {}
        sql = 'select id,content from ban where type=?'
        c.execute(sql, (select_l,))
        fet = c.fetchall()
        for l in fet:
            auxiliary_ban[select_l][int(l[0])] = l[1]
loadBeforeStart()

def checkBan(check_type, content):
    if check_type == 'ip':
        all_bannedip = list(auxiliary_ban['ip'].values())
        for l in all_bannedip:
            if content in IPy.IP(l):
                return 'banned'
            
    if check_type == 'word':
        all_bannedword = list(auxiliary_ban['word'].values())
        for l in all_bannedword:
            if l in content:
                return 'banned'
    return 'pass'

@app.route('/admin/page/ban/<bantype>/view')
def adminPageBanView(bantype):
    return render_template('background/ban/view.html', bantype=bantype)

@app.route('/admin/page/ban/<bantype>/add')
def adminPageBanAdd(bantype):
    return render_template('background/ban/add.html', bantype=bantype)

@app.route('/admin/page/ban/<bantype>/edit', methods=['GET'])
def adminPageBanEdit(bantype):
    id = request.args['id']
    sql = "select content from ban where id=? and type=?"
    c.execute(sql, (id,bantype))
    fet = c.fetchone()
    msg = {"id":id, 'content':fet[0]}
    return render_template("background/ban/edit.html", baninfo=msg, bantype=bantype)

@app.route('/admin/page/op_log/<logtype>/view')
def adminPageOplogView(logtype):
    return render_template('background/op_log/view.html', logtype=logtype)

@app.route('/admin/api/ban/<bantype>/data', methods=['POST'])
def adminApiBanData(bantype):
    page = request.form['page']
    limit = request.form['limit']
    title = ''
    if 'title' in request.form:
        title = request.form['title']

    sql = "select id,content,ctime from ban where type=?"
    sql2 = 'select count(id) from ban where type=?'
    sql_args = [bantype]
    sql2_args = [bantype]
    if title != '' and title is not None:
        sql += " and (content like ?)"
        sql2 += " and (content like ?)"
        sql_args.append('%{}%'.format(title))
        sql2_args.append('%{}%'.format(title))
    
    sql += " order by id desc limit ?,?" #.format((int(page)-1)*int(limit), int(limit))
    sql_args.append((int(page)-1)*int(limit))
    sql_args.append(int(limit))
    
    c.execute(sql, sql_args)
    fet = c.fetchall()
    c.execute(sql2, sql2_args)
    fet2 = c.fetchone()[0]

    ls = []
    for l in fet:
        msg = {'id':l[0], 'content':l[1], 'ctime':l[2]}
        ls.append(msg)
    
    return jsonify({"code": 0, "msg": "", "count": fet2, "data": ls})

@app.route('/admin/api/ban/<bantype>/del', methods=['POST'])
def adminApiBanDel(bantype):
    ids_txt = request.form['ids']
    ids = ids_txt.split(',')
    sql = 'delete from ban where type=? and ('
    sql_args = [bantype]
    for l in ids:
        sql += 'id=? or '
        sql_args.append(l)
        del auxiliary_ban[bantype][int(l)]
    sql = sql[:-3]
    sql += ')'
    c.execute(sql, sql_args)
    con.commit()

    logAdminOp(session['ADMIN_NAME'], getIP(), 'ban', '删除了ID为 {} 的{}辅助封禁'.format(ids_txt,bantype), c,con)
    return jsonify({"code": 0, "msg": ""})

def checkAddEditBan(bantype,content):
    if not(bantype in bantypes):
        return jsonify({'code':-1, 'msg':'不存在的规则'}) 
    
    if bantype == 'ip':
        try:
            IPy.IP(content)
        except:
            return jsonify({'code':-1, 'msg':'IP不符合要求'})
    return 0

@app.route('/admin/api/ban/<bantype>/add', methods=['POST'])
def adminApiBanAdd(bantype):
    content = request.form['content']

    check_ret = checkAddEditBan(bantype,content)
    if check_ret!=0:
        return check_ret
    
    sql = 'select count(id) from ban where type=? and content=?'
    c.execute(sql, (bantype,content))
    fet = c.fetchone()
    if fet[0]>0:
        return jsonify({'code':-1, 'msg':'该规则已存在'}) 

    sql = "INSERT into ban(type,content) VALUES(?, ?);"
    c.execute(sql, (bantype,content))
    con.commit()

    sql = 'select id from ban where type=? and content=?'
    c.execute(sql, (bantype,content))
    id = c.fetchone()[0]
    auxiliary_ban[bantype][int(id)] = content
    print(auxiliary_ban)

    logAdminOp(session['ADMIN_NAME'], getIP(), 'ban', '添加了ID为 {} 的{}辅助封禁'.format(id,bantype), c,con, '添加的具体内容为：content={}'.format(content))
    return jsonify({"code":0})

@app.route('/admin/api/ban/<bantype>/edit', methods=['POST'])
def adminApiBanEdit(bantype):
    id = request.form['id']
    content = request.form['content']
    id = int(id)

    check_ret = checkAddEditBan(bantype,content)
    if check_ret!=0:
        return check_ret
    
    sql = 'update ban set content=? where id=?'
    c.execute(sql, (content,id))
    con.commit()

    auxiliary_ban[bantype][id] = content

    logAdminOp(session['ADMIN_NAME'], getIP(), 'ban', '修改了ID为 {} 的{}辅助封禁'.format(id,bantype), c,con, '修改的具体内容为：content={}'.format(content))
    return jsonify({'code':0, 'msg':'操作成功', 'data':{}})

@app.route('/admin/api/op_log/<logtype>/data', methods=['POST'])
def adminApiOplogData(logtype):
    page = request.form['page']
    limit = request.form['limit']
    title = ''
    if 'title' in request.form:
        title = request.form['title']

    sql = "select id,admin_name,ip,msg,ctime,notice from admin_op_log where type=?"
    sql2 = 'select count(id) from admin_op_log where type=?'
    sql_args = [logtype]
    sql2_args = [logtype]
    if title != '' and title is not None:
        sql += " and (admin_name like ? or msg like ?)"
        sql2 += " and (admin_name like ? or msg like ?)"
        sql_args.append('%{}%'.format(title))
        sql_args.append('%{}%'.format(title))
        sql2_args.append('%{}%'.format(title))
        sql2_args.append('%{}%'.format(title))
    
    sql += " limit ?,?" #.format((int(page)-1)*int(limit), int(limit))
    sql_args.append((int(page)-1)*int(limit))
    sql_args.append(int(limit))
    
    c.execute(sql, sql_args)
    fet = c.fetchall()
    c.execute(sql2, sql2_args)
    fet2 = c.fetchone()[0]

    ls = []
    for l in fet:
        msg = {'id':l[0], 'admin_name':l[1], 'ip':l[2], 'msg':l[3], 'ctime':l[4], 'notice':l[5]}
        ls.append(msg)
    
    return jsonify({"code": 0, "msg": "", "count": fet2, "data": ls})
# -------------admin----------------

if __name__=="__main__":
    app.run(host="127.0.0.1",port=1234,debug=True)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)