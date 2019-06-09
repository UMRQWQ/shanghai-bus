# coding=utf-8
import json
import requests
from bs4 import BeautifulSoup
import time

sid_url = 'https://shanghaicity.openservice.kankanews.com/public/bus/get'
stop_url = 'https://shanghaicity.openservice.kankanews.com/public/bus/Getstop'

headers = {'User-Agent': 'MicroMessenger/7.0.1380(0x27000034) Process/tools NetType/WIFI Language/zh_CN'}

GO_COMPANY = 0
BACK_HOME = 1

def Get_Time() :
    hours =  time.strftime("%H", time.localtime())
    if  '7' < hours < '9' :
        return GO_COMPANY
    else:
        return BACK_HOME
class StopInfo(object):
    # 停站信息
    def __init__(self, stop_id, station_name, error=0, terminal='', stopdis=0, distance=0, time=0, **kwargs):
        self.stop_id = int(stop_id)  # 站台id
        self.station_name = station_name  # 站台名称
        self.error = int(error)  # 错误信息 -2=等待发车
        self.plate = terminal  # 车牌信息
        self.stop_dis = int(stopdis)  # 距离当前站台还有X站
        self.distance = int(distance)  # 距离当前站台还有X米
        self.time = int(time)  # 距离当前站台还有X秒

    def dumps(self):
        # 导出数据
        res = {'error': self.error, 'stop_id': self.stop_id, 'station_name': self.station_name, 'plate': self.plate,
               'stop_dis': self.stop_dis, 'distance': self.distance, 'time': self.time}
        return res

if __name__ == '__main__':
    stoptype = Get_Time()
    session =  requests.Session()
    stopid = '21.'
    sid_list = {}
    if stoptype == GO_COMPANY :
        stop_data = {'stoptype': stoptype, 'stopid':'15.', 'sid': 'b591d840a85e2507ed0412101d14d036'}
        sid_list[u'182路']  = stop_data
    else:
        stopid = '20.'
    stop_data = {'stoptype': stoptype, 'stopid':stopid, 'sid': 'fdb820cafb0f64e87be649128c1a8dea'}
    sid_list = {u'上川专线' : stop_data}

    while True:
        for idNum, stop_data in sid_list.items():
            session.post(sid_url,headers=headers, data={'idnum':idNum})
            stopInfo = session.post(stop_url, headers=headers, data=stop_data).json()
            stopInfo = stopInfo if isinstance(stopInfo, dict) else stopInfo[0]
            info = StopInfo(stop_id= '0', station_name="唐陆路创新西路", **stopInfo).dumps()
            if (info['error'] ==  -2) :
                print("未发车")
            else:
                print(info)
        time.sleep(30)

