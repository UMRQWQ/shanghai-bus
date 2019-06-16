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


curr_station_stop_list = {'go_company_182': GO_COMPANY_182_STATION_ID, 'go_company_sc' : GO_COMPANY_SC_STATION_ID, 'back_home_sc': BACK_HOME_SC_STATION_ID}

def Get_Time() :
    hours =  time.strftime("%H", time.localtime())
    prompt_info = ' ' 
    if  '7' <= hours <= '9' :
        prompt_info = u'从家步行到公交车站约 3 分钟'
        go_type =  GO_COMPANY
    elif '18' <= hours <= '22':
        prompt_info = u'从公司步行到公交车站约 10 分钟'
        go_type = BACK_HOME
    else :
        go_type =  None
    return go_type, prompt_info

def get_siedList(stoptype, station_stop_list):
    sid_list = {}
    if stoptype == None:
        pass
    elif stoptype == GO_COMPANY :
        stop_data = {'stoptype': stoptype, 'stopid':station_stop_list['go_company_182'], 'sid': SID_182}
        sid_list[u'182路']  = stop_data 
        stop_data = {'stoptype': stoptype, 'stopid':station_stop_list['go_company_sc'], 'sid': SID_SC}
        sid_list[u'上川专线'] =  stop_data
    else :
        stop_data = {'stoptype': stoptype, 'stopid':station_stop_list['back_home_sc'], 'sid': SID_SC}
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
        self.next_bus_dis = 0 # 下一趟车 距离当前站台还有X站
        self.next_bus_time = 0  # 下一趟车 距离当前站台还有X秒

    def dumps(self):
        # 导出数据
        res = {'error': self.error, 'id_num' : self.id_num, 'stop_id': self.stop_id, 'station_name': self.station_name, 'plate': self.plate,
               'stop_dis': self.stop_dis, 'distance': self.distance, 'time': self.time, 'next_bus_dis' : self.next_bus_dis, 'next_bus_time': self.next_bus_time}
        return res
    def merger(self, next_bus_info):
        self.next_bus_dis = self.stop_dis + next_bus_info.stop_dis
        self.next_bus_time = self.time + next_bus_info.time
        return self


def Get_station_info(session, id_num, station_name, stop_data) :
    session.post(sid_url,headers=headers, data={'id_num':id_num})
    stopInfo = session.post(stop_url, headers=headers, data=stop_data).json()
    stopInfo = stopInfo if isinstance(stopInfo, dict) else stopInfo[0]
    info = StopInfo(id_num = id_num, stop_id= '0', station_name= station_name, **stopInfo)
    return info


def Get_curretn_station_info(session, stoptype, station_stop_list = curr_station_stop_list) :
    stationInfo = []
    sid_list = get_siedList(stoptype, station_stop_list)
    station_name = "新金桥路申江路" if stoptype == 'GO_COMPANY' else "唐陆路创新西路"
    for id_num, stop_data in sid_list.items():
        curr_station_info = Get_station_info(session, id_num, station_name, stop_data)
        if curr_station_info.error == -2:
            info = curr_station_info.dumps()
        else :
            next_bus_stop_id = int(stop_data['stopid'].split('.')[0]) - curr_station_info.stop_dis
            stop_data['stopid'] = '{0}.'.format(next_bus_stop_id) 
            next_bus_info = Get_station_info(session, id_num, station_name, stop_data)
            info = curr_station_info.merger(next_bus_info).dumps()
        stationInfo.append(info)
    return stationInfo

if __name__ == '__main__':
    stoptype, prompt_info = Get_Time()
    if stoptype == None:
        pass
    else: 
        session =  requests.Session()
        while True:
            curretn_station_info = Get_curretn_station_info(session, stoptype)
            for info in curretn_station_info:
                os.system('cls') 
                if (info['error'] ==  -2) :
                    master_info = '当前时间： ' +  time.strftime("%H:%M:%S", time.localtime()) + '  ' + prompt_info + '\r\n' + \
                        info['id_num'] + ':  未发车'
                else:
                    master_info = '当前时间： ' +  time.strftime("%H:%M:%S", time.localtime()) + '  ' + prompt_info + '\r\n' + \
                        info['id_num'] + ':  距离本站 ' + str(info['stop_dis']) + '站,  剩余时间: ' + str(info['time']//60) + '分钟' + "\r\n"\
                        '  下趟车:  距离本站： ' +  str(info['next_bus_dis']) +  '站,  剩余时间: ' +  str(info['next_bus_time']//60) + '分钟'
                print(master_info)
            time.sleep(15)

