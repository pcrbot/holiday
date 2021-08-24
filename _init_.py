import time
import json
import requests

from datetime import datetime
from copy import deepcopy
from os.path import dirname, join, exists
from hoshino import Service
from hoshino.typing import CQEvent

sv = Service('假期')

today = time.time()

curpath = dirname(__file__)
config = join(curpath, 'holiday.json')
if exists(config):
    with open(config) as fp:
        root = json.load(fp)

holiday = root['holiday']
holiday_cache = {}
holiday_cache = deepcopy(holiday)

def get_week_day(day):
    week_day_dict = {
        0 : '星期一',
        1 : '星期二',
        2 : '星期三',
        3 : '星期四',
        4 : '星期五',
        5 : '星期六',
        6 : '星期日',
    }
    return week_day_dict[day]

@sv.on_fullmatch("最近假期")
async def current_holiday(bot, ev: CQEvent):
    for data in holiday_cache:
        info = holiday_cache[data]
        timeArray = time.strptime(info['date'], "%Y-%m-%d")
        timeStamp = int(time.mktime(timeArray))
        if info['holiday'] == True and today < timeStamp:
            time_int = int((timeStamp - today)/86400)+ 1
            name = info['name']
            msg = f'最近的假期是{name},还有{time_int}天'
            await bot.send(ev, msg)
            return


@sv.on_fullmatch("剩余假期")
async def year_holiday(bot, ev: CQEvent):
    false_holiday = 0
    holiday = 0
    msg = '今年剩余的假期有:\n'
    for data in holiday_cache:
        info = holiday_cache[data]
        timeArray = time.strptime(info['date'], "%Y-%m-%d")
        timeStamp = time.mktime(timeArray)
        if info['holiday'] == True and today < timeStamp:
            day = datetime.strptime(info['date'], "%Y-%m-%d").weekday()
            if day == 5 or day == 6:
                false_holiday = false_holiday + 1
            time_int = int((timeStamp - today)/86400)+ 1
            name = info['name']
            date = info['date']
            msg = msg + f'{date}{name},还有{time_int}天' + '\n'
            holiday = holiday +1
        elif info['holiday'] == False and today < timeStamp:
            false_holiday = false_holiday + 1
    real_holiday = holiday - false_holiday
    msg = msg + f'共{holiday}天\n减去调休与周末后剩余假期为{real_holiday}天'
    await bot.send(ev, msg)


@sv.on_fullmatch("查看调休")
async def false_holiday(bot, ev: CQEvent):
    msg = '今年剩余的调休日为:\n'
    for data in holiday_cache:
        info = holiday_cache[data]
        timeArray = time.strptime(info['date'], "%Y-%m-%d")
        timeStamp = time.mktime(timeArray)
        if info['holiday'] == False and today < timeStamp:
            day = datetime.strptime(info['date'], "%Y-%m-%d").weekday()
            week = get_week_day(day)
            date = info['date']
            msg = msg + f'{date},{week}' + '\n'
    await bot.send(ev, msg)



#每天四点更新假期数据
@sv.scheduled_job('cron',hour='4')
async def today_holiday():
    url = 'http://timor.tech/api/holiday/year'
    r = requests.get(url)
    holiday = r.json()

    with open('holiday.json', 'w') as f:
        json.dump(holiday, f)