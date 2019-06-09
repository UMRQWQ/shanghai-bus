# coding=utf-8
import json
import requests
from bs4 import BeautifulSoup
import time
import os              

sid_url = 'https://shanghaicity.openservice.kankanews.com/public/bus/get'
stop_url = 'https://shanghaicity.openservice.kankanews.com/public/bus/Getstop'

headers = {'User-Agent': 'MicroMessenger/7.0.1380(0x27000034) Process/tools NetType/WIFI Language/zh_CN'}

GO_COMPANY = 0
BACK_HOME = 1
SID_182 = 'b591d840a85e2507ed0412101d14d036'
SID_SC = 'fdb820cafb0f64e87be649128c1a8dea'
GO_COMPANY_182_STATION_ID = '15.'
GO_COMPANY_SC_STATION_ID = '21.'
BACK_HOME_SC_STATION_ID = '20.'


def Get_Time() :
    hours =  time.strftime("%H", time.localtime())
    global prompt_info 
    if  '7' <= hours <= '9' :
        prompt_info = u'从家步行到公交车站约 3 分钟'
        return GO_COMPANY
    elif '18' <= hours <= '22':
        prompt_info = u'从公司步行到公交车站约 10 分钟'
        return BACK_HOME
    else :
        return None

def get_siedList(stoptype):
    sid_list = {}
    if stoptype == None:
        pass
    elif stoptype == GO_COMPANY :
        stop_data = {'stoptype': stoptype, 'stopid':GO_COMPANY_182_STATION_ID, 'sid': SID_182}
        sid_list[u'182路']  = stop_data 
        stop_data = {'stoptype': stoptype, 'stopid':GO_COMPANY_SC_STATION_ID, 'sid': SID_SC}
        sid_list[u'上川专线'] =  stop_data
    else :
        stop_data = {'stoptype': stoptype, 'stopid':BACK_HOME_SC_STATION_ID, 'sid': SID_SC}
        sid_list[u'上川专线'] =  stop_data
    return sid_list

class StopInfo(object):
    # 停站信息
    def __init__(self, id_num, stop_id, station_name, error=0, terminal='', stopdis=0, distance=0, time=0, **kwargs):
        self.id_num = id_num # 路线名
        self.stop_id = int(stop_id)  # 站台id
        self.station_name = station_name  # 站台名称
        self.error = int(error)  # 错误信息 -2=等待发车
        self.plate = terminal  # 车牌信息
        self.stop_dis = int(stopdis)  # 距离当前站台还有X站
        self.distance = int(distance)  # 距离当前站台还有X米
        self.time = int(time)  # 距离当前站台还有X秒

    def dumps(self):
        # 导出数据
        res = {'error': self.error, 'id_num' : self.id_num, 'stop_id': self.stop_id, 'station_name': self.station_name, 'plate': self.plate,
               'stop_dis': self.stop_dis, 'distance': self.distance, 'time': self.time}
        return res

if __name__ == '__main__':
    stoptype = Get_Time()
    if stoptype == None:
        pass
    else: 
        sid_list = get_siedList(stoptype)
        session =  requests.Session()
        station_name = "新金桥路申江路" if stoptype == 'GO_COMPANY' else "唐陆路创新西路"
        while True:
            for idNum, stop_data in sid_list.items():
                session.post(sid_url,headers=headers, data={'idnum':idNum})
                stopInfo = session.post(stop_url, headers=headers, data=stop_data).json()
                stopInfo = stopInfo if isinstance(stopInfo, dict) else stopInfo[0]
                info = StopInfo(id_num = idNum, stop_id= '0', station_name= station_name, **stopInfo).dumps()
                os.system('cls') 
                if (info['error'] ==  -2) :
                    print("未发车")
                else:
                    master_info = '当前时间： ' + time.strftime("%H:%M:%S", time.localtime()) + '  ' + prompt_info + '\r\n' + info['id_num'] + ':  距离本站 ' + str(info['stop_dis']) + '站,  剩余时间: ' + str(info['time']//60) + '分钟'
                    print(master_info)
            time.sleep(15)

