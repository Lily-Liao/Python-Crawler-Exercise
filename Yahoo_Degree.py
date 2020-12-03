# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 14:24:22 2020

@author: user
"""


import time
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import datetime
from datetime import timedelta
#台灣
#URL="https://tw.news.yahoo.com/weather/"
#台北
#URL="https://tw.news.yahoo.com/weather/%E5%8F%B0%E7%81%A3/%E8%87%BA%E5%8C%97%E5%B8%82/%E8%87%BA%E5%8C%97%E5%B8%82-2306179"
#桃園
URL="https://tw.news.yahoo.com/weather/%E5%8F%B0%E7%81%A3/%E6%A1%83%E5%9C%92%E5%B8%82/%E6%A1%83%E5%9C%92%E5%B8%82-91982232"
#台南
#URL="https://tw.news.yahoo.com/weather/%E5%8F%B0%E7%81%A3/%E5%8F%B0%E5%8D%97%E5%B8%82/%E5%8F%B0%E5%8D%97%E5%B8%82-2306182"

def get_resource(url):
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               "AppleWebKit/537.36 (KHTML, like Gecko)"
               "Chrome/63.0.3239.132 Safari/537.36"}
    return requests.get(url, headers=headers, cookies={"over18":"1"})

def parse_html(r):
    if r.status_code == requests.codes.ok:
        r.encoding = "utf8"
        soup = BeautifulSoup(r.text, "lxml")        
    else:
        print("HTTP請求錯誤..." + url)
        soup = None
    
    return soup    

def lineNotifyMessage(token, msg):
    headers = {
          "Authorization": "Bearer " + token, 
          "Content-Type" : "application/x-www-form-urlencoded"
      }
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code

if __name__ == '__main__':
    url = URL 
    #print(url)
    soup=parse_html(get_resource(url))
    content=soup.find("div",class_="accordion Ov(h) Trsdu(.42s) daily")
    row=content.find_all("div",class_="BdB Bds(d) Bdbc(#fff.12) Fz(1.2em) Py(2px) O(0) Pos(r) forecast-item")
    report=[]
    for item in row:
        day=item.find("div",class_="D(ib) Va(m) W(1/4)").text
        rain=item.find("span",class_="D(ib) Mstart(1/3)")
        pre_rain=rain.find("img")['alt'].split(" ")#pre_rain[1]
        high_degree=item.find("span",class_="high D(ib) Miw(32px)").text
        low_degree=item.find("span",class_="low Pstart(10px) C(#a5d6ff) D(ib) Miw(32px)").text
        report.append({
            "Week":day,
            "Rain Chance":pre_rain[1],
            "High Degree":high_degree,
            "Low_Degree":low_degree
            })
    week=[]
    high=[]
    low=[]
    rain=[]
    date=[]
    today = datetime.date.today().strftime('%Y/%m/%d')
    date.append(today)
    for i in range(1,10):
        now=datetime.date.today()
        aday=timedelta(days=i)
        tomorrow = (now + aday).strftime('%Y/%m/%d')
        date.append(tomorrow)
    #DSprint(date)
    for i in report:
        week.append(i['Week'])
        high.append(int(i['High Degree'].split('°')[0]))
        low.append(int(i['Low_Degree'].split('°')[0]))
        rain.append(int(i['Rain Chance'].split('%')[0]))
    delta=[high[i]-low[i] for i in range(0,len(high))]
    max_deg=max(delta)

    d=("%s %s溫差變化最大，請大家注意身體不要感冒!!"%(date[delta.index(max_deg)],week[delta.index(max_deg)]))   
    line_content="桃園天氣小提醒\n"+"溫馨小提示1~~"+"\n"+d+"\n\n"+"溫馨小提示2~~"+"\n"
    #提醒降雨機率高的日子
    remind=[week[j] for j in range(0,len(rain)) if rain[j]>=30]
    date1=[date[m] for m in range(0,len(rain)) if rain[m]>=30]
    
    for i in range(0,len(remind)):
        e="%s %s降雨機率有3成以上，最好帶把傘!!" %(date1[i],remind[i])
        line_content=line_content+e+"\n"
        
    print(line_content)
    
    pattern = {'星期五':'Friday', '星期六':'Saturday','星期日':'Sunday',
               '星期一':'Monday','星期二':'Tuesday','星期三':'Wednesday',
               '星期四':'Thursday'}
    week1 = [pattern[x] if x in pattern else x for x in week]
    
    
    index=np.arange(len(week))
    #---------高低溫折線圖--------
    
    plt.figure(figsize=(20,18))
    plt.plot(index,high, "r-o",label="High Degree")
    texts = [f'{i}°C' for i in high]
    for x_, y_, text in zip(index,high, texts):
        plt.text(x_, y_, text, fontsize=14)
    
    plt.plot(index,low, "b-o",label="Low Degree")
    texts1 = [f'{i}°C' for i in low]
    for x_, y_, text in zip(index,low, texts1):
        plt.text(x_, y_, text, fontsize=14)
        
    plt.plot(index,delta,"g-^",label="Delta Degree")
    texts2 = [f'{i}°C' for i in delta]
    for x_, y_, text in zip(index,delta, texts2):
        plt.text(x_, y_, text, fontsize=14)
        
    plt.xticks(index,week1)
    plt.legend(loc='best')
    plt.xlabel("week",fontsize="20")
    plt.ylabel("Temperature (°C)",fontsize="20")
    plt.title("Temperature in the 10 days Of Taoyuans",fontsize="20")
    plt.savefig("degree.png")
    #--------降雨量---------------
    texts = [f'{i}%' for i in rain]
    plt.figure(figsize=(20,18))
    plt.bar(index,rain,label="Rain Chance")
    for x_, y_, text in zip(index,rain, texts):
        plt.text(x_, y_, text, fontsize=14)
    plt.legend(loc='best')
    plt.xticks(index,week1)
    plt.xlabel("week",fontsize="20")
    plt.ylabel("Rain Chance",fontsize="20")
    plt.title("Rain Chance in the 10 days Of Taoyuan",fontsize="20")
    plt.savefig("rain.png")
 ################################################################       
    plt.show()


    token = 'your token'
    lineNotifyMessage(token, line_content)

    
    
    