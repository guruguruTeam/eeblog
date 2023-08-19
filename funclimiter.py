import time
from functools import wraps
from datetime import datetime
from datetime import timedelta
import random
from flask import request
def decorator(func):
    "cache for function result, which is immutable with fixed arguments"
    print("initial cache for %s" % func.__name__)
    cache = {}

    @wraps(func)
    def decorated_func(*args,**kwargs):
        # 函数的名称作为key
        key = func.__name__
        result = None
        #判断是否存在缓存
        if key in cache.keys():
            (result, updateTime) = cache[key]
            #过期时间固定为10秒
            if time.time() -updateTime < 1:
                print("limit call 1s", key)
                result = updateTime
            else :
                print("cache expired !!! can call ")
                result = None
        else:
            print("no cache for ", key)
        #如果过期，或则没有缓存调用方法
        if result is None:
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
        return result

    return decorated_func

def funclimiter(time_interval, need_wait_time, default=None):
    def decorator(function):
        # For first time always run the function
        function.__last_run = {'127.0.0.1':datetime.min}
        def guard(*args, **kwargs):
            #ip = testip()    #测试用
            ip = str(request.headers.get("X-Real-IP", request.remote_addr))
            now = datetime.now()
            if ip in function.__last_run:
                if now - function.__last_run[ip] >= timedelta(seconds=time_interval):
                    function.__last_run[ip] = now
                    return function(*args, **kwargs)
                elif default is not None:
                    function.__last_run[ip] = now + timedelta(seconds=need_wait_time)
                    return default(*args, **kwargs)
                else:
                    function.__last_run[ip] = now + timedelta(seconds=need_wait_time)
                    print('limited')
                    return
            else:
                function.__last_run[ip]=now
                return function(*args, **kwargs)
        return guard
    return decorator

# -------test----------
def de(e):
    print(type(e))

def testip():
    ips = ['0.0.0.0','1.1.1.1','2.2.2.2', '3', '4', '5', '6','7']
    ip = str(ips[random.randint(0,len(ips)-1)])
    print(ip)
    return ip

@funclimiter(1, 5, de)
def func2(x):
    print('call func')

if __name__ == "__main__":
    for i in range(100):
        func2(1)
        time.sleep(0.1)
