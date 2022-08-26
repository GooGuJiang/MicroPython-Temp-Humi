import network
import time
#import dht
import machine
import sys
import urequests
import ujson
from machine import Timer
import ntptime
from sht3x import SHT3x_Sensor

gu_bool = True

upload_temp = Timer(1)
SSID = ""# WIFI 名称
PASSWORD = "" # WIFI密码
APIURL = "http://{0}" # API上报地址
UPLOADAPI = APIURL.format("/upload")
PINGAPI = APIURL.format("/ping")


def do_connect():
    import network
    import time
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PASSWORD)

    start = time.ticks_ms()  # get millisecond counter
    while not wlan.isconnected():
        time.sleep(1)  # sleep for 1 second
        if time.ticks_ms() - start > 20000:
            print("connect timeout!")
            return False

    if wlan.isconnected():
        print('network config:', wlan.ifconfig())


def nub_add_z(nub):
    nub = str(nub)
    if len(nub) == 1:
        nub = f"0{nub}"
        return str(nub)
    else:
        return str(nub)

'''
def getHT(now_time): # 适用于 DH11/22 传感器的代码
    d = dht.DHT11(machine.Pin(2))
    d.measure()
    t = str(d.temperature())
    h = str(d.humidity())
    data = {
        "temp": t,
        "humi": h,
        "time": {
            "year": now_time[0],
            "month": nub_add_z(now_time[1]),
            "day": nub_add_z(now_time[2]),
            "hour": nub_add_z(now_time[4]),
            "minute": nub_add_z(now_time[5]),
            "sec": now_time[6]
        }
    }
    return data
'''

def getHT(now_time):
    sht3x_sensor = SHT3x_Sensor(freq=100000, sdapin=5, sclpin=4)
    measure_data = sht3x_sensor.read_temp_humd()
    # measure_data = [22.9759, 73.8277]
    # The default decimal place is 4 digits
    temp = str(round(measure_data[0],1))
    humd = str(round(measure_data[1],1))
    data = {
        "temp": temp,
        "humi": humd,
        "time": {
            "year": now_time[0],
            "month": nub_add_z(now_time[1]),
            "day": nub_add_z(now_time[2]),
            "hour": nub_add_z(now_time[4]),
            "minute": nub_add_z(now_time[5]),
            "sec": now_time[6]
        }
    }
    return data

def set_time():
    global gu_bool
    try:
        ntptime.NTP_DELTA = 3155644800  # UTC+8偏移时间（秒）
        ntptime.host = "ntp.ntsc.ac.cn"  # ntp服务器
        ntptime.settime()
        gu_bool = False
    except:
        gu_bool = True


def now_time():
    rtc = machine.RTC()
    return rtc.datetime()


def uploadHT(data):
    header = {'content-type': 'application/json', 'authorization': 'xxx'} #注意，这个地方要与服务端中 /upload 路由下 if request.headers.get('Authorization') == "xxx": 对应 不然无法上报数据
    b = {
        "name": "gu_esp8266",
        "data": data
    }
    post_out = urequests.post(UPLOADAPI, headers=header, data=ujson.dumps(b)).text
    if ujson.loads(post_out)["code"] == 200:
        return True
    else:
        return False


def upload_post(e):
    uploadHT(getHT(now_time()))


def ping():
    try:
        if urequests.get(PINGAPI).text == "pong":
            return True
        else:
            return False
    except:
        return False


def main():
    if do_connect() == False:
        print("WiFi cannot connect")
        sys.exit()
    if ping() == False:
        print("Server cannot connect")
        sys.exit()
    while gu_bool:
        set_time()
    print(now_time())
    upload_post(now_time())
    upload_temp.init(period=1000 * 60, mode=Timer.PERIODIC, callback=upload_post)


if __name__ == "__main__":
    main()
