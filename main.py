# -*- codeing = utf-8 -*-
import json
import requests
from bs4 import BeautifulSoup
import functools   
from functools import lru_cache
import time
from gevent import pywsgi
from flask import Flask, request, render_template   


@lru_cache()
def get_defi_data(_ts):
    stablefish = 'https://stable.fish/rank?chain=10'
    result = []
    try:
        response = requests.get(stablefish)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('tr', class_="tb_borderbottom"):
            project,coin,fee,apy1,apy7,tvl,tvl_change1,tvl_change7,tip = 0,0,0,0,0,0,0,0,0
            for i in item.find_all('div', class_="d6"):
                project = i.font.text
                coin = i.div.font.text
                break
            for i in item.find_all('div', class_="tipblock"):
                tip=i.p.text
                break
            for i in item.find_all('td', class_='rttd_tvl br_pc'):
                fee = i.span.text
                break
            num = 0
            for i in item.find_all('td', class_="rttd_apy"):
                if num==0:
                    apy = i.div.div.p
                    num2 = 0
                    for j in apy.find_all("font"):
                        if num2==1:
                            apy1 = j.text
                        if num2==3:
                            apy7 = j.text
                        num2+=1
                if num==2:
                    tvl = i.span.text
                num+=1
            for i in item.find_all('td', class_="rttd_apy br_pc"):
                tvl_change = i.div.div.p
                num = 0
                for j in tvl_change.find_all("font"):
                    if num==1:
                        tvl_change1 = j.text
                    if num==3:
                        tvl_change7 = j.text
                    num+=1
            if project!=0:
                result.append({'project':project,'symbol':{"coin":coin,"tip":tip},"tvl":tvl,"gas_fee":fee,"24h":{"apy":apy1,"tvlchange":tvl_change1},"1week":{"apy":apy7,"tvlchange":tvl_change7}})
    except:
        return {"status":"error"}
    def cmp(x, y):
        a,b = 0,0
        if x['tvl'][-1]=='M':
            a = int(x['tvl'][1:-1]+"000000")
        else:
            a = int(x['tvl'][1:-1]+"000")
        if y['tvl'][-1]=='M':
            b = int(y['tvl'][1:-1]+"000000")
        else:
            b = int(y['tvl'][1:-1]+"000")
        if a > b:
            return -1
        if a < b:
            return 1
        return 0
    return {"data":sorted(result,key=functools.cmp_to_key(cmp)),"status":"ok"}

app = Flask(__name__)
 
@app.route("/get_defi_data",methods=["GET"])
def defi_data(): 
    return get_defi_data(int(int(time.time())/3600))

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=80)
    server = pywsgi.WSGIServer(('0.0.0.0', 5001), app)
    server.serve_forever()
