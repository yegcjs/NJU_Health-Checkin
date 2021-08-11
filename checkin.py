import json
import re
import time
import urllib
import requests
import execjs
from bs4 import BeautifulSoup
from collections import namedtuple
import schedule

encrypt_js_script = "encrypt.js"
agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Mobile Safari/537.36"
urls = {
    "login": "https://authserver.nju.edu.cn/authserver/login?service=http%3A%2F%2Fehallapp.nju.edu.cn%2Fxgfw%2Fsys%2Fyqfxmrjkdkappnju%2Fapply%2FgetApplyInfoList.do",
    "health_history": "http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/getApplyInfoList.do",
    "check_in": "http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do"
}

def encrypt(password, encrypt_salt):
    with open(encrypt_js_script, 'r') as f: 
        script = ''.join(f.readlines())
    context = execjs.compile(script)
    return context.call('encryptAES', password, encrypt_salt)

def login(session, username, password):
    r = session.get(urls['login'])
    soup = BeautifulSoup(r.text, 'lxml')
    input_boxes = soup.find_all('input')
    
    input_info = {}
    for i in input_boxes:
        name, value = i.get('name'), i.get('value')
        if name not in ["username", "password", "captchaResponse", None]:
            input_info[name] = value 
    
    pattern = re.compile(r"var pwdDefaultEncryptSalt = (.*?);", re.MULTILINE | re.DOTALL)
    encrypt_script = str(soup.find("script", text=pattern))
    pwdDefaultEncryptSalt = re.search('pwdDefaultEncryptSalt = "(.*?)";', encrypt_script).group(1)
    headers = {
        'User-Agent': agent,
        'Origin': "https://authserver.nju.edu.cn",
        'Referer': urls['login'],
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'username': username,
        'password': encrypt(password, pwdDefaultEncryptSalt),
        'captchaResponse': '',
        'lt': input_info["lt"],
        'dllt': input_info["dllt"],
        'execution': input_info["execution"],
        '_eventId': input_info["_eventId"],
        'rmShown': input_info["rmShown"]        
    }
    session.post(urls['login'], data=urllib.parse.urlencode(data), headers=headers)
    

def check_login(session, location):
    r = session.get(urls['health_history'])
    try:
        history = json.loads(r.text)
        assert history['code'] == '0'
    except:
        assert 0, "Fail to login"

    print("Log in Successfully")
    wid = history['data'][0]['WID']
    if location == 'default':
        location = history['data'][1]['CURR_LOCATION']
    return wid, location


def checkin(session, checkin_info):
    info_t = namedtuple('Checkin_Info', 
        ['WID', 'CURR_LOCATION', 'IS_TWZC', 'IS_HAS_JKQK', 'JRSKMYS', 'JZRJRSKMYS']
    )
    info = info_t._make(checkin_info)
    checkin_url = urls['check_in']+'?'
    for key, value in info._asdict().items():
        checkin_url += f'{key}={value}&'
    checkin_url = checkin_url[:-1]  # drop last &

    r = session.get(checkin_url)
    result = json.loads(r.text)

    t = time.localtime(time.time())
    if result['code'] == '0' and result['msg'] == '成功':
        print(f"打卡成功, {t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")
    else: 
        print(f"打卡失败, {t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")



def main():
    with open("config.json", "r", encoding='utf-8') as f:
        info = json.load(f)
    
    session = requests.Session()
    session.cookies = requests.cookies.RequestsCookieJar()
    session.headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Mobile Safari/537.36"

    assert 'student_id' in info, "Expected infomation `student_id` not found. Check config.json"
    assert "password" in info, "Expected infomation `password` not found. Check config.json"

    login(session, username=info['student_id'], password=info['password'])
    wid, location = check_login(session, info['location'])
    try:
        health_status = (
            wid,                            # WID
            location,                       # 地点
            info['body_temp_ok'],           # 体温正常
            info['health_status'],          # 健康状况
            info['my_health_code_color'],   # 本人苏康码颜色
            info['fam_mem_health_code_color']   # 家人苏康码颜色
        )
        checkin(session, health_status)
    except:
        assert 0, "You are not providing enough infomation to check in. Check config.json"
    
    return True


if __name__ == '__main__':
    main()
    # keep check in every day
    schedule.every().day.at("00:01").do(main)
    while True:
        schedule.run_pending()
        time.sleep(3600)