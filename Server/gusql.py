import sqlite3
import time
import os
from time import time, mktime, strptime

db_file = "./data.db"


def one_loader():
    gu_con = sqlite3.connect(db_file)
    gu_cur = gu_con.cursor()
    gu_sql = f"CREATE TABLE IF NOT EXISTS dtable(id INTEGER PRIMARY KEY AUTOINCREMENT,date TEXT,startimestamp TEXT,endtimestamp TEXT)"
    gu_cur.execute(gu_sql)
    gu_con.commit()
    # 关闭游标
    gu_cur.close()
    # 断开数据库连接
    gu_con.close()

if not os.path.exists(db_file):  # 初始化
    one_loader()


def create_table(data_in_json: dict):
    try:
        time_json = data_in_json["data"]["time"]
        gu_con = sqlite3.connect("data.db")
        gu_cur = gu_con.cursor()
        gu_out_data = None
        get_sql = gu_con.execute(f"select * from dtable where date = 'gu{str(time_json['date'])}'")
        for data in get_sql:
            gu_out_data = data

        # 这里不会为None
        if gu_out_data is None:
            '''
                        is_exist = None
            is_exist_sql = gu_con.execute(f"select * from dtable where date = 'gu{str(int(time_json['date']) - 1)}'")
            for data in is_exist_sql:
                is_exist = data
            if is_exist is not None:
                gu_cur.execute(f"UPDATE 'dtabel' SET endtimestamp='{str(int(time_json['timestamp']) - 1)}'")
            '''



            timestamp: int = mktime(strptime(f"{time_json['year']}/{time_json['month']}/"
                                             f"{time_json['day']} {time_json['hour']}:{time_json['minute']}:{time_json['sec']}",
                                             "%Y/%m/%d %H:%M:%S"))
            gu_cur.execute("INSERT INTO dtable values(?,?,?,?)", (
                None,
                f"gu{time_json['date']}",
                timestamp,
                timestamp))
            gu_cur.execute(
                f"CREATE TABLE IF NOT EXISTS 'gu{str(time_json['date'])}' (id INTEGER PRIMARY KEY AUTOINCREMENT,date TEXT,temp TEXT,humi TEXT,timestamp TEXT)")
            gu_con.commit()
            # 关闭游标
            gu_cur.close()
            # 断开数据库连接
            gu_con.close()
            return True
        else:
            # 关闭游标
            gu_cur.close()
            # 断开数据库连接
            gu_con.close()
            return False
    except Exception as err:
        # 关闭游标
        gu_cur.close()
        # 断开数据库连接
        gu_con.close()
        print(err)
        return False


def write_data(data_in_json: dict):
    try:
        data_json = data_in_json["data"]
        time_json = data_json["time"]
        gu_con = sqlite3.connect(db_file)
        gu_cur = gu_con.cursor()
        gu_cur.execute(f"INSERT INTO 'gu{time_json['date']}' values(?,?,?,?,?)", (
            None,
            f"{time_json['year']}/{time_json['month']}/{time_json['day']} {time_json['hour']}:{time_json['minute']}",
            data_json["temp"],
            data_json["humi"],
            time_json['timestamp']))
        #print(time_json['timestamp'], time_json['date'])
        gu_cur.execute(f"UPDATE dtable SET endtimestamp=? WHERE date=?", (time_json['timestamp'], f"gu{time_json['date']}"))
        gu_con.commit()
        # 关闭游标
        gu_cur.close()
        # 断开数据库连接
        gu_con.close()
        return True
    except Exception as errr:
        # 关闭游标
        gu_cur.close()
        # 断开数据库连接
        gu_con.close()
        print(errr)
        return False


def input_dh_data(in_json: dict):  # 写入温湿度+时间到数据库
    '''
    try:
        create_table(in_json)
        write_data(in_json)
        return True
    except Exception as erx:
        print(erx)
        return False
    '''
    create_table(in_json)
    write_data(in_json)
    return True



def get_new_table():  # 获取最新的表名
    try:
        gu_con = sqlite3.connect(db_file)
        gu_cur = gu_con.cursor()
        gu_cur.execute("select * from dtable")
        return gu_cur.fetchall()[-1][1]
    except Exception as err:
        # 关闭游标
        gu_cur.close()
        # 断开数据库连接
        gu_con.close()
        print(err)
        return False


def get_now_dh():
    try:
        gu_con = sqlite3.connect(db_file)
        gu_cur = gu_con.cursor()
        gu_cur.execute(f"select * from {get_new_table()}")
        return gu_cur.fetchall()[-1]
    except Exception as err:
        # 关闭游标
        gu_cur.close()
        # 断开数据库连接
        gu_con.close()
        print(err)
        return False


#
def get_all_dh(date=None) -> list:
    try:
        out_list = []
        gu_con = sqlite3.connect(db_file)
        gu_cur = gu_con.cursor()
        if date == None:
            date = get_new_table()
            gu_cur.execute(f"select * from {date}")
        else:
            date = f"gu{date}"
            try:
                gu_cur.execute(f"select * from {date}")
            except:
                return False

        gu_list_tmp = gu_cur.fetchall()
        for gu_lis in range(len(gu_list_tmp)):
            out_json = {
                "id": gu_list_tmp[gu_lis][0],
                "temp": gu_list_tmp[gu_lis][2],
                "humi": gu_list_tmp[gu_lis][3],
                "date": gu_list_tmp[gu_lis][1],
                "timestamp": gu_list_tmp[gu_lis][4],
            }
            out_list.append(out_json)

        return out_list
    except Exception as err:
    #    # 关闭游标
        gu_cur.close()
    #    # 断开数据库连接
        gu_con.close()
        print(err)
        return False


def get_all_date_table():
    try:
        out_list = []
        gu_con = sqlite3.connect(db_file)
        gu_cur = gu_con.cursor()
        gu_cur.execute(f"select * from dtable")
        out_tmp = gu_cur.fetchall()
        for gu_lst in range(len(out_tmp)):
            out_json = {
                "id": out_tmp[gu_lst][0],
                "table_name": out_tmp[gu_lst][1],
                "table_date": out_tmp[gu_lst][1][2:],
                "startStamp": out_tmp[gu_lst][2],
                "endStamp": out_tmp[gu_lst][3]
            }

            out_list.append(out_json)
        return out_list
    except Exception as err:
        print(err)
        return False


def sc_table(table_id):
    try:
        gu_con = sqlite3.connect(db_file)
        gu_out_data = None
        get_sql = gu_con.execute("select * from dtable where date = '{0}'".format(f"{table_id}"))
        for data in get_sql:
            gu_out_data = data

        if gu_out_data is None:
            gu_con.close()
            return False
        else:
            gu_con.close()
            return True
    except Exception as grr:
        print(grr)
        gu_con.close()
        return False