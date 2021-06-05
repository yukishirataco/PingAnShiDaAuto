from typing import Type
import requests
import json
import time
import datetime
import re
from random import randint

# 这玩意获取学生基本信息的网址实际上是 https://app.upc.edu.cn/uc/api/oauth/index?redirect=http://stu.gac.upc.edu.cn:8089/xswc&appid
# =200200819124942787&state=2 剩下的前端根本不验证你的 Cookies
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'http://stu.gac.upc.edu.cn:8089',
    'Connection': 'keep-alive',
    'Referer': 'http://stu.gac.upc.edu.cn:8089/xswc&appid=200200819124942787&state=2',
}
base = datetime.datetime.today()
# 在填写之前，请先照着 https://app.upc.edu.cn/uc/api/oauth/index?redirect=http://stu.gac.upc.edu.cn:8089/xswc&appid
# =200200819124942787&state=2 的提示信息和源代码中的注释，完成下面的配置信息
data = {
    'stuXh': '1145141919',  # 学号
    'stuXm': '李田所',  # 姓名
    'stuXy': 'XXX学院',  # 学院
    'stuZy': '水泳',  # 专业
    'stuMz': '野兽族',  # 民族
    'stuBj': '',  # 班级
    # 如果你选择使用数字石大方式获取信息，可以不用填写上述内容
    'stuLxfs': '',  # 联系方式
    'stuJzdh': '',  # 家长电话
    'stuJtfs': '',  # 交通方式
    'stuStartTime': '',  # 外出时间，可以自动生成，留空即可
    'stuReason': '',  # 外出事由
    'stuWcdz': '',  # 外出地址（仅限青岛市）
    'stuJjlxr': '',  # 外出紧急联系人
    'stuJjlxrLxfs': ''  # 紧急联系人联系方式
    # 至于这个“本人承诺”，纯粹只是把验证放到前端去了
}


def getStudentInfo(uid, pwd):
    session = requests.session()
    usrdata = {
        'username': uid,
        'password': pwd
    }
    response = session.post('https://app.upc.edu.cn/uc/wap/login/check', headers=headers, data=usrdata)
    info = session.get(
        "https://app.upc.edu.cn/uc/api/oauth/index?redirect=http://stu.gac.upc.edu.cn:8089/xswc&appid=200200819124942787&state=2")
    code = re.findall(r"^\s+var\scode\s=\s.{33}.;$", info.text, re.M)[0].strip().split('"')[1]  # 不用必死4，看我怎么用正则扒人参数
    # 妈的，这个code是一次性的
    xs = requests.post("http://stu.gac.upc.edu.cn:8089/stuqj/getXsMess", headers=headers, data=dict(code=code)).json()
    return xs['data']


def AbsentReq(days):
    date_list = [base + datetime.timedelta(days=x) for x in range(days)]
    dates = [x.strftime("%Y-%m-%d") + ' 08:00:00' for x in date_list]
    now = None
    after = None
    for i in dates:
        data['stuStartTime'] = i
        now = time.time()
        response = requests.post('http://stu.gac.upc.edu.cn:8089/stuqj/addQjMess', headers=headers, data=data)
        if response.json()['resultStat'] == "success":
            print(
                '用时 {} s,请假时间为 {} 的请假已成功，返回为{}.'.format(time.time() - now, data['stuStartTime'], str(response.json())))
        else:
            print('用时 {} s,请假失败，返回为: {}'.format(time.time() - now, response.json()['mess'], str(response.json())))
    # 学校做了防快速请求，这里加一个随机延时。。。
    time.sleep(60+randint(5,10))
    # 返回值
    # 重复提交：{"resultStat":"error","mess":"您2021-03-16的请假信息已提交，请勿重复添加。","data":null,"othermess":null}
    # 成功提交：{"resultStat":"success","mess":"成功","data":1,"othermess":null}
    # 提交错误2：{"resultStat":"error","mess":"添加请假信息异常","data":"String index out of range: 10","othermess":null}


if __name__ == '__main__':
    import ctypes

    ctypes.windll.kernel32.SetConsoleTitleW("UPC一键请假")
    try:
        print("正在检测当前操作环境是否能够访问平安石大，用时可能较长，请稍作等待……")
        jwxt = requests.get("http://stu.gac.upc.edu.cn:8089",timeout=10) #直接访问一个外网没法访问的校内资源试试看
        if jwxt.status_code != 200:
            raise TypeError("请确保当前处于校园网环境下！")
    except Exception as e:
        print("发生错误:{}".format(e))
        print("请确保你当前的网络环境处于石大校园网中或者使用石大VPN！")
        quit(-1)
    else:
        print("您正处于石大校园网中！")
    print('')
    print("出发咯~丢~~~~")
    print("不要大力拍打或者滑动哦")
    print('')
    stu_id = ''
    while stu_id.isdigit and not stu_id:
        stu_id = input("请先输入你的学号: ")
        try:
            int(stu_id)
        except Exception as e:
            print("学号必须是数字!")
            stu_id = ''
            continue
    stu_pwd = ''
    while not stu_pwd:
        stu_pwd = input("请输入你的数字石大密码: ")
        if not stu_pwd:
            print("数字石大密码不得为空！")
            continue
    try:
        info = getStudentInfo(stu_id, stu_pwd)
    except Exception as e:
        print("获取学生信息失败，将会按照源代码中填写的内容进行请假。")
        print("在请假之前，请先确保你已经把正确的信息填入了源代码中，否则请假将无法完成!")
    else:
        data['StuXh'] = info['XH']
        data['StuXm'] = info['XM']
        data['stuXy'] = info['YXMC']
        data['stuBj'] = info['SZBJMC']
        data['stuMz'] = info['MZ']
        data['stuZy'] = info['ZYMC']
        print("获取学生信息成功！内容:{}".format(str(info)))
    days = input("请输入要请假的天数：")
    AbsentReq(int(days))
