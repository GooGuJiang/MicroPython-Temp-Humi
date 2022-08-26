from time import time, mktime, strptime
from flask import Flask, jsonify, render_template, request, send_from_directory
import gusql
from flask_cors import * #用于测试 后期会删除
from flask_caching import Cache

config = {  # 配置缓存
    "DEBUG": False,  # some Flask specific configs
    "CACHE_TYPE": "RedisCache",  # Flask-Caching related configs
    "CACHE_REDIS_HOST": "192.168.1.1", #配置 redis 地址
    "CACHE_REDIS_PORT": 6379,
    "CACHE_REDIS_DB": 5,
    "CACHE_DEFAULT_TIMEOUT": 300
}

# config = {
#    "DEBUG": False,          # some Flask specific configs
#    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
#    "CACHE_DEFAULT_TIMEOUT": 300
# }

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


@app.route('/')  # index
@cache.cached(300)
def index():
    return "看什么看没写((("


@app.route("/upload", methods=['POST', 'GET'])
def get_sptest_info():
    '''
    #try:
        if request.method == 'POST':
            if request.headers.get('Authorization') == "gu_esp_dh":
                json_data: dict = request.json
                time_json = json_data['data']['time']  # 用于暂存其中time的值
                timestamp: int = mktime(strptime(f"{time_json['year']}/{time_json['month']}/"
                                                 f"{time_json['day']} {time_json['hour']}:{time_json['minute']}:{time_json['sec']}",
                                                 "%Y/%m/%d %H:%M:%S"))
                time_date = f"{time_json['year']}{time_json['month']}{time_json['day']}"
                print(time_date)
                json_data["data"]["time"]['timestamp'] = timestamp
                json_data["data"]["time"]["date"] = time_date
                if not gusql.input_dh_data(json_data):
                    return jsonify({"code": 400})
                return jsonify({"code": 200})
            else:
                return jsonify({"code": 400})
    #except Exception as err:
    #    print(err)
    #    return jsonify({"code": 500})
    '''

    if request.method == 'POST':
        if request.headers.get('Authorization') == "xxx":  #注意，这个地方要与客户端中 header = {...'authorization': 'xxx'} 对应 不然无法上报数据
            json_data: dict = request.json
            time_json = json_data['data']['time']  # 用于暂存其中time的值
            timestamp: int = mktime(strptime(f"{time_json['year']}/{time_json['month']}/"
                                             f"{time_json['day']} {time_json['hour']}:{time_json['minute']}:{time_json['sec']}",
                                             "%Y/%m/%d %H:%M:%S"))
            time_date = f"{time_json['year']}{time_json['month']}{time_json['day']}"
            json_data["data"]["time"]['timestamp'] = timestamp
            json_data["data"]["time"]["date"] = time_date
            #print(json_data)
            if not gusql.input_dh_data(json_data):
                return jsonify({"code": 400})
            return jsonify({"code": 200})
        else:
            return jsonify({"code": 400})


@app.route('/ping')  # Ping 存活测试
def ping():
    return "pong"


@app.route('/api/tempmois/current')  # 获取最新的温湿度数据
@cross_origin()
@cache.cached(5)
def get_now():
    gu_get_sql = gusql.get_now_dh()
    if gu_get_sql == False:
        return jsonify({"code": 500})
    json_out = {
        "code": 200,
        "data": {
            "temp": gu_get_sql[2],
            "humi": gu_get_sql[3],
            "date": gu_get_sql[1]
        }
    }
    return jsonify(json_out)


@app.route('/api/tempmois/all', methods=['POST'])
@cross_origin()
@cache.cached(1)  # 缓存 1s
def get_dh_list():
    if request.method == 'POST':
        json_data: dict = request.json
        date_nub = json_data["date"]
        if date_nub != None:
            if gusql.sc_table(f"gu{date_nub}") == False:
                return jsonify({"code": 500, "msg": "No data for this date"})
        get_tmp = gusql.get_all_dh(date_nub)
        if get_tmp == False:
            return jsonify({"code": 500})
        out_json = {
            "code": 200,
            "data": get_tmp
        }
        return jsonify(out_json)
    else:
        return jsonify({"code": 400})

@app.route('/api/table/all')
@cross_origin()
@cache.cached(10)  # 缓存 10s
def get_all_table():
    get_tmp = gusql.get_all_date_table()
    if get_tmp == False:
        return jsonify({"code": 500})

    out_json = {
        "code": 200,
        "data": get_tmp
    }
    return jsonify(out_json)


def get_des_data(start: int, end: int):
    all_data = gusql.get_all_date_table()
    des_data = []
    for i in all_data:
        if i['data']['time']['timestamp'] >= start and i['data']['time']['timestamp'] <= end:
            des_data.append(i)
    return des_data


@app.route("/upload/date", methods=['POST', 'GET'])
def get_post():
    try:
        if request.method == 'POST':
            json_data = request.json
            print(json_data)
            # if gusql.input_dh_data(json_data) == False:
            #    return jsonify({"code":400})
            return jsonify({"code": 200})
        else:
            return jsonify({"code": 400, "msg": "Please use POST"})
    except Exception as err:
        print(err)
        return jsonify({"code": 500})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="7001")
