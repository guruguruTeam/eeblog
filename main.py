# -*- coding: UTF-8 -*-

from flask import Flask,jsonify,request,render_template,send_file
from json import dump,load
from codecs import open
from time import time
from os import path,listdir

def test(path_):
    if not path.exists(path_):
        dump((),load_(path_,"w"))

    return path_

def load_(file,mode="r"):
    return open(file,mode,"UTF-8-sig")

def time_(path_):
    return round(path.getmtime(path_))

app=Flask("guru",template_folder="client")
app.secret_key="guru"

method=("POST","GET")

@app.errorhandler(Exception)
def error(error):
    return render_template("404.html")

@app.route("/",methods=method)
def index():
    list_=((file.rsplit(".",1)[0],time_(f"notes/{file}")) for file in listdir("notes"))
    data=sorted(list_,key=lambda essay:essay[1],reverse=True)
    return render_template("index.html",data=data)

@app.route("/<path:folder>/<path:file>",methods=method)
def essay(folder,file):
    path_=f"{folder}/{file}.md"
    data=(folder,file,load_(path_).read(),time_(path_),load(load_(test(f"client/_/{file}.json"))))

    return render_template("essay.html",folder=folder,title=file,data=data)

@app.route("/files/<path:folder>/<path:file>",methods=method)
def file(folder,file):
    return send_file(f"{folder}/{file}")

@app.route("/comment",methods=method)
def comment():
    form=request.form
    note=form.get("note","")
    list_=(form.get("nick",""),form.get("text",""),round(time()))

    if not all(list_):
        return jsonify((0,"评论","昵称/评论内容可能不完善？"))

    if not list_[0].isalnum() or len(list_[0])>12:
        return jsonify((0,"评论","用数字/字母/汉字取个12字内的昵称吧！"))

    if note+".md" not in listdir("notes"):
        return jsonify((0,"评论","呃 找不到这篇笔记……"))

    path_=f"client/_/{note}.json"
    data=load(load_(test(path_)))
    data.append(list_)
    dump(data,load_(path_,"w"))
    return jsonify((1,"评论","评论发送成功！",list_))

if __name__=="__main__":
    app.run(host="0.0.0.0",port=1234,debug=True)