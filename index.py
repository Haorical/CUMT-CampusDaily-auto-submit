# -*- coding: utf-8 -*-
import sys
import requests
import json
import yaml
import oss2
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
from urllib3.exceptions import InsecureRequestWarning
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


# 读取yml配置
def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config1 = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config1)


# 全局配置
config = getYmlConfig(yaml_file='config.yml')


# 获取今日校园api
def getCpdailyApis(user):
    apis = {}
    user = user['user']
    schools = 'cumt'
    if 1 == 1:
        if 1 + 1 == 2:
            res = requests.get(url='https://mobile.campushoy.com/v6/config/guest/tenant/info?ids=cumt')
            data = res.json()['data'][0]
            idsUrl = data['idsUrl']
            ampUrl = data['ampUrl']
            if 'campusphere' in ampUrl or 'cpdaily' in ampUrl:
                parse = urlparse(ampUrl)
                host = parse.netloc
                res = requests.get(parse.scheme + '://' + host)
                parse = urlparse(res.url)
                apis[
                    'login-url'] = idsUrl + '/login?service=' + parse.scheme + r"%3A%2F%2F" + host + r'%2Fportal%2Flogin'
                apis['host'] = host
            ampUrl2 = data['ampUrl2']
            if 'campusphere' in ampUrl2 or 'cpdaily' in ampUrl2:
                parse = urlparse(ampUrl2)
                host = parse.netloc
                res = requests.get(parse.scheme + '://' + host)
                parse = urlparse(res.url)
                apis[
                    'login-url'] = idsUrl + '/login?service=' + parse.scheme + r"%3A%2F%2F" + host + r'%2Fportal%2Flogin'
                apis['host'] = host
    log(apis)
    return apis


# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()


# 登陆并返回session
def getSession(user, loginUrl):
    user = user['user']
    params = {
        'login_url': loginUrl,
        # 保证学工号和密码正确下面两项就不需要配置
        'needcaptcha_url': '',
        'captcha_url': '',
        'username': user['username'],
        'password': user['password']
    }

    cookies = {}
    # 借助上一个项目开放出来的登陆API，模拟登陆
    res = requests.post(config['login']['api'], params)
    cookieStr = str(res.json()['cookies'])
    log(cookieStr)
    if cookieStr == 'None':
        log(res.json())
        return None

    # 解析cookie
    for line in cookieStr.split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value
    session = requests.session()
    session.cookies = requests.utils.cookiejar_from_dict(cookies)
    return session


# 查询表单
def queryForm(session, apis):
    host = apis['host']
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 yiban/8.1.11 cpdaily/8.1.11 wisedu/8.1.11',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8'
    }
    queryCollectWidUrl = 'https://{host}/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'.format(host=host)
    params = {
        'pageSize': 6,
        'pageNumber': 1
    }
    res = session.post(queryCollectWidUrl, headers=headers,
                       data=json.dumps(params))
    if len(res.json()['datas']['rows']) < 1:
        return None

    collectWid = res.json()['datas']['rows'][0]['wid']
    formWid = res.json()['datas']['rows'][0]['formWid']

    detailCollector = 'https://{host}/wec-counselor-collector-apps/stu/collector/detailCollector'.format(
        host=host)
    res = session.post(url=detailCollector, headers=headers,
                       data=json.dumps({"collectorWid": collectWid}))
    schoolTaskWid = res.json()['datas']['collector']['schoolTaskWid']

    getFormFields = 'https://{host}/wec-counselor-collector-apps/stu/collector/getFormFields'.format(
        host=host)
    res = session.post(url=getFormFields, headers=headers, data=json.dumps(
        {"pageSize": 100, "pageNumber": 1, "formWid": formWid, "collectorWid": collectWid}))

    form = res.json()['datas']['rows']
    return {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}


# 填写form
def fillForm(session, form, host):
    sort = 1
    for formItem in form[:]:
        # 只处理必填项
        if formItem['isRequired'] == 1:
            default = config['cpdaily']['defaults'][sort - 1]['default']
            if formItem['title'] != default['title']:
                log('第%d个默认配置不正确，请检查' % sort)
                exit(-1)
            # 文本直接赋值
            if formItem['fieldType'] == 1 or formItem['fieldType'] == 5:
                formItem['value'] = default['value']
            # 单选框需要删掉多余的选项
            if formItem['fieldType'] == 2:
                # 填充默认值
                formItem['value'] = default['value']
                fieldItems = formItem['fieldItems']
                for i in range(0, len(fieldItems))[::-1]:
                    if fieldItems[i]['content'] != default['value']:
                        del fieldItems[i]
            # 多选需要分割默认选项值，并且删掉无用的其他选项
            if formItem['fieldType'] == 3:
                fieldItems = formItem['fieldItems']
                defaultValues = default['value'].split(',')
                for i in range(0, len(fieldItems))[::-1]:
                    flag = True
                    for j in range(0, len(defaultValues))[::-1]:
                        if fieldItems[i]['content'] == defaultValues[j]:
                            # 填充默认值
                            formItem['value'] += defaultValues[j] + ' '
                            flag = False
                    if flag:
                        del fieldItems[i]
            log('必填问题%d：' % sort + formItem['title'])
            log('答案%d：' % sort + formItem['value'])
            sort += 1
        else:
            form.remove(formItem)
    return form


# 提交表单
def submitForm(formWid, address, collectWid, schoolTaskWid, form, session, host):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 okhttp/3.12.4',
        'CpdailyStandAlone': '0',
        'extension': '1',
        'Cpdaily-Extension': 'eZbW2qLZT0G0VbYqnj5mz5UCyZiuS+Mht0ro4VCSTgTancCpi4ru3IpfZibLN2Q4JR3dl7wYTXnTi5dzfAwbYcs5FB4VPqOTrcYNVjoRY9h9J7sxA1MWIWZxiEC7iuzXwAeEjrGmnHnX3P7mprZW66fbhNsIrM938cVo6aK7fgdQx6vGY7OVJBS+kqwk/xE2ipLqV0ro4QNZ9u/6G9MUbyd7QghLIM9PIRJTrd6TzoYPFBHqDHIY57dHHUBUC8RzfvreU/2o5sY=',
        'Content-Type': 'application/json; charset=utf-8',
        # 请注意这个应该和配置文件中的host保持一致
        'Host': host,
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    # 默认正常的提交参数json
    params = {"formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
              "form": form, "uaIsCpadaily":True}
    # print(params)
    submitForm = 'https://{host}/wec-counselor-collector-apps/stu/collector/submitForm'.format(host=host)
    r = session.post(url=submitForm, headers=headers, data=json.dumps(params))
    msg = r.json()['message']
    return msg


title_text = '今日校园打卡成功通知'


# server酱通知
def sendServerChan(msg):
    log('正在发送Server酱。。。')
    res = requests.post(url='https://sc.ftqq.com/{0}.send'.format(config['Info']['ServerChan']),
                        data={'text': title_text, 'desp': getTimeStr() + "\n" + str(msg)})
    code = res.json()['errmsg']
    if code == 'success':
        log('发送Server酱通知成功。。。')
    else:
        log('发送Server酱通知失败。。。')
        log('Server酱返回结果' + code)


# 综合提交
def InfoSubmit(msg):
    if config['Info']['ServerChan']:
        sendServerChan(msg)


def main_handler(event, context):
    try:
        for user in config['users']:
            log('当前用户：' + str(user['user']['username']))
            apis = getCpdailyApis(user)
            log('脚本开始执行。。。')
            log('开始模拟登陆。。。')
            session = getSession(user, apis['login-url'])
            if session is not None:
                log('模拟登陆成功。。。')
                log('正在查询最新待填写问卷。。。')
                params = queryForm(session, apis)
                if str(params) == 'None':
                    log('获取最新待填写问卷失败，可能是辅导员还没有发布。。。')
                    InfoSubmit('没有新问卷')
                    exit(-1)
                log('查询最新待填写问卷成功。。。')
                log('正在自动填写问卷。。。')
                form = fillForm(session, params['form'], apis['host'])
                log('填写问卷成功。。。')
                log('正在自动提交。。。')
                msg = submitForm(params['formWid'], user['user']['address'], params['collectWid'],
                                 params['schoolTaskWid'], form, session, apis['host'])
                if msg == 'SUCCESS':
                    log('自动提交成功！')
                    InfoSubmit('自动提交成功！', user['user']['email'])
                elif msg == '该收集已填写无需再次填写':
                    log('今日已提交！')
                    # InfoSubmit('今日已提交！', user['user']['email'])
                    InfoSubmit('今日已提交！')
                else:
                    log('自动提交失败。。。')
                    log('错误是' + msg)
                    InfoSubmit('自动提交失败！错误是' + msg, user['user']['email'])
                    exit(-1)
            else:
                log('模拟登陆失败。。。')
                log('原因可能是学号或密码错误，请检查配置后，重启脚本。。。')
                exit(-1)
    except Exception as e:
        InfoSubmit("出现问题了！" + str(e))
        raise e
    else:
        return 'success'


# 配合Windows计划任务等使用
if __name__ == '__main__':
    print(main_handler({}, {}))
