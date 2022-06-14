import re
import time
import yaml
import rsa
import base64
import requests
from bs4 import BeautifulSoup


def loadconfig():
    f = open('./config.yml')
    data = f.read()
    conf = yaml.load(data, Loader=yaml.SafeLoader)
    return conf


def login(conf: dict) -> str:
    url = conf['url']['login']
    req = requests.get(url)
    data = req.text
    cookie = req.headers['Set-Cookie'].split(";")[0]
    soup = BeautifulSoup(data, features="html.parser")
    dl = soup.find("input", id="csrftoken")
    header = {
        "cookie": cookie
    }
    publickey = requests.get(
        url=conf['url']['publickey'], headers=header).json()
    b_modulus = base64.b64decode(publickey['modulus'])
    b_exponent = base64.b64decode(publickey['exponent'])
    mm_key = rsa.PublicKey(int.from_bytes(b_modulus, 'big'),
                           int.from_bytes(b_exponent, 'big'))
    mm = base64.b64encode(rsa.encrypt(
        bytes(conf['user']['password'], encoding='utf-8'), mm_key))
    postdata = {
        'csrftoken': dl['value'],
        'language': "zh_CN",
        'yhm': conf['user']['number'],
        'mm': mm.decode()
    }
    header = {
        "cookie": cookie,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    url += "?time=" + str(int(round(time.time() * 1000)))
    req = requests.post(url, data=postdata, headers=header,
                        allow_redirects=False)
    cookielist = req.headers['Set-Cookie'].split(" ")
    for v in cookielist:
        if re.match("JSESSIONID*", v):
            cookie = v
    return cookie


def pj(conf: str, cookie: str):
    url = conf['url']['menu'] + str(int(round(time.time() * 1000)))
    header = {
        "cookie": cookie
    }
    req = requests.get(url, headers=header, allow_redirects=False)
    url = conf['url']['pj']
    req = requests.get(url, headers=header, allow_redirects=False)
    data = {
        "_search": "false",
        "nd": int(round(time.time() * 1000)),
        "queryModel.showCount": 100,
        "queryModel.currentPage": 1,
        "queryModel.sortName": "",
        "queryModel.sortOrder": "asc",
        "time": 1
    }
    url = conf['url']['pjlist'] + str(conf['user']['number'])
    req = requests.post(url, data=data, headers=header, allow_redirects=False)
    for v in req.json()['items']:
        if v['tjztmc'] == "未评":
            url = conf['url']['pjdetail'] + str(conf['user']['number'])
            data = {
                "jxb_id": v['jxb_id'],
                "kch_id": v['kch_id'],
                "xsdm": v['xsdm'],
                "jgh_id": v['jgh_id'],
                "tjzt": -1,
                "pjmbmcb_id": "",
                "sfcjlrjs": 0
            }
            req = requests.post(url, data=data, headers=header)
            soup = BeautifulSoup(req.text, features="html.parser")
            for s in soup.select('div'):
                if s.has_attr('data-ztpjbl'):
                    ztpjbl = s.attrs['data-ztpjbl']
                if s.has_attr('data-jszdpjbl'):
                    jszdpjbl = s.attrs['data-jszdpjbl']
                if s.has_attr('data-xykzpjbl'):
                    xykzpjbl = s.attrs['data-xykzpjbl']
                if s.has_attr('data-jxb_id'):
                    jxb_id = s.attrs['data-jxb_id']
                if s.has_attr('data-kch_id'):
                    kch_id = s.attrs['data-kch_id']
                if s.has_attr('data-jgh_id'):
                    jgh_id = s.attrs['data-jgh_id']
                if s.has_attr('data-xsdm'):
                    xsdm = s.attrs['data-xsdm']
                if s.has_attr('data-pjmbmcb_id'):
                    pjmbmcb_id = s.attrs['data-pjmbmcb_id']
                if s.has_attr('data-pjdxdm'):
                    pjdxdm = s.attrs['data-pjdxdm']
                if s.has_attr('data-fxzgf'):
                    fxzgf = s.attrs['data-fxzgf']
                if s.has_attr('data-xspfb_id'):
                    xspfb_id = s.attrs['data-xspfb_id']
            for s in soup.select('table'):
                if s.has_attr('data-pjzbxm_id'):
                    pjzbxm_id = s.attrs['data-pjzbxm_id']

            a = soup.find_all("input", attrs={'data-sfzd': '1'})
            pfdjdmxmb_id = [""]*10
            for k in range(0, len(a)):
                pfdjdmxmb_id[k] = a[k]['data-pfdjdmxmb_id']
            
            i = 0
            pjzbxm_id = [""]*10
            pfdjdmb_id = [""]*10
            zsmbmcb_id = [""]*10
            for s in soup.select('tr'):
                if s.has_attr('data-pjzbxm_id'):
                    pjzbxm_id[i] = s.attrs['data-pjzbxm_id']
                    pfdjdmb_id[i] = s.attrs['data-pfdjdmb_id']
                    zsmbmcb_id[i] = s.attrs['data-zsmbmcb_id']
                    i += 1
                
            data = {
                "modelList[0].pjzt": 1,
                "tjzt": 1,
                "ztpjbl": ztpjbl,
                "jszdpjbl": jszdpjbl,
                "xykzpjbl": xykzpjbl,
                "jxb_id": jxb_id,
                "kch_id": kch_id,
                "jgh_id": jgh_id,
                "xsdm": xsdm,
                "modelList[0].pjmbmcb_id": pjmbmcb_id,
                "modelList[0].pjdxdm": pjdxdm,
                "modelList[0].xspjList[0].pjzbxm_id": pjzbxm_id,
                "modelList[0].fxzgf": fxzgf,
                "modelList[0].py": "",
                "modelList[0].xspfb_id": xspfb_id,
                "modelList[0].xspjList[0].childXspjList[0].pfdjdmxmb_id": pfdjdmxmb_id[0],
                "modelList[0].xspjList[0].childXspjList[0].pjzbxm_id": pjzbxm_id[0],
                "modelList[0].xspjList[0].childXspjList[0].pfdjdmb_id":pfdjdmb_id[0],
                "modelList[0].xspjList[0].childXspjList[0].zsmbmcb_id":zsmbmcb_id[0],
                "modelList[0].xspjList[0].childXspjList[1].pfdjdmxmb_id": pfdjdmxmb_id[1],
                "modelList[0].xspjList[0].childXspjList[1].pjzbxm_id":pjzbxm_id[1],
                "modelList[0].xspjList[0].childXspjList[1].pfdjdmb_id":pfdjdmb_id[1],
                "modelList[0].xspjList[0].childXspjList[1].zsmbmcb_id":zsmbmcb_id[1],
                "modelList[0].xspjList[0].childXspjList[2].pfdjdmxmb_id": pfdjdmxmb_id[2],
                "modelList[0].xspjList[0].childXspjList[2].pjzbxm_id":pjzbxm_id[2],
                "modelList[0].xspjList[0].childXspjList[2].pfdjdmb_id":pfdjdmb_id[2],
                "modelList[0].xspjList[0].childXspjList[2].zsmbmcb_id":zsmbmcb_id[2],
                "modelList[0].xspjList[0].childXspjList[3].pfdjdmxmb_id": pfdjdmxmb_id[3],
                "modelList[0].xspjList[0].childXspjList[3].pjzbxm_id":pjzbxm_id[3],
                "modelList[0].xspjList[0].childXspjList[3].pfdjdmb_id":pfdjdmb_id[3],
                "modelList[0].xspjList[0].childXspjList[3].zsmbmcb_id":zsmbmcb_id[3],
                "modelList[0].xspjList[0].childXspjList[4].pfdjdmxmb_id": pfdjdmxmb_id[4],
                "modelList[0].xspjList[0].childXspjList[4].pjzbxm_id":pjzbxm_id[4],
                "modelList[0].xspjList[0].childXspjList[4].pfdjdmb_id":pfdjdmb_id[4],
                "modelList[0].xspjList[0].childXspjList[4].zsmbmcb_id":zsmbmcb_id[4],
                "modelList[0].xspjList[0].childXspjList[5].pfdjdmxmb_id": pfdjdmxmb_id[5],
                "modelList[0].xspjList[0].childXspjList[5].pjzbxm_id":pjzbxm_id[5],
                "modelList[0].xspjList[0].childXspjList[5].pfdjdmb_id":pfdjdmb_id[5],
                "modelList[0].xspjList[0].childXspjList[5].zsmbmcb_id":zsmbmcb_id[5],
                "modelList[0].xspjList[0].childXspjList[6].pfdjdmxmb_id": pfdjdmxmb_id[6],
                "modelList[0].xspjList[0].childXspjList[6].pjzbxm_id":pjzbxm_id[6],
                "modelList[0].xspjList[0].childXspjList[6].pfdjdmb_id":pfdjdmb_id[6],
                "modelList[0].xspjList[0].childXspjList[6].zsmbmcb_id":zsmbmcb_id[6],
                "modelList[0].xspjList[0].childXspjList[7].pfdjdmxmb_id": pfdjdmxmb_id[7],
                "modelList[0].xspjList[0].childXspjList[7].pjzbxm_id":pjzbxm_id[7],
                "modelList[0].xspjList[0].childXspjList[7].pfdjdmb_id":pfdjdmb_id[7],
                "modelList[0].xspjList[0].childXspjList[7].zsmbmcb_id":zsmbmcb_id[7],
                "modelList[0].xspjList[0].childXspjList[8].pfdjdmxmb_id": pfdjdmxmb_id[8],
                "modelList[0].xspjList[0].childXspjList[8].pjzbxm_id":pjzbxm_id[8],
                "modelList[0].xspjList[0].childXspjList[8].pfdjdmb_id":pfdjdmb_id[8],
                "modelList[0].xspjList[0].childXspjList[8].zsmbmcb_id":zsmbmcb_id[8],
                "modelList[0].xspjList[0].childXspjList[9].pfdjdmxmb_id": pfdjdmxmb_id[9],
                "modelList[0].xspjList[0].childXspjList[9].pjzbxm_id":pjzbxm_id[9],
                "modelList[0].xspjList[0].childXspjList[9].pfdjdmb_id":pfdjdmb_id[9],
                "modelList[0].xspjList[0].childXspjList[9].zsmbmcb_id":zsmbmcb_id[9],
                }
            url = conf['url']['pjpost'] + str(conf['user']['number'])
            req = requests.post(url,data=data, headers=header)
def main():
    config = loadconfig()
    cookie = login(config)
    print("等待一分钟左右")
    pj(config, cookie)
    print("评价完成")


if __name__ == '__main__':
    main()
