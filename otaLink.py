#!/use/bin/env python 3.8.3
# Copyright © 2020 yanbuyu's Project
# Thanks aoao https://github.com/aoaoemoji/FiimeGetMIUI/blob/main/%E7%88%AC%E8%99%AB.py

import argparse, os, sys, requests, itertools, multiprocessing
from functools import partial
from bs4 import BeautifulSoup

def getOTALinkFromSite(model, version, lastest):
    newList = []
    url = "https://miui.511i.cn/?index=rom_list"
    headers = {'user-agent':'Mozilla/5.0 (Linux; U; Android 12; zh-cn; Mi 10 Build/SKQ1.220119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36'}
    data = {
    'dh':model,
    # lx参数: 0稳定版,1开发版内测,1b开发版公测
    'lx':version
    }
    requests.packages.urllib3.disable_warnings()#屏蔽warning信息
    try:
        response = requests.post(url, data = data, headers = headers)
    except requests.exceptions.ConnectionError:
        print(f"getOTALinkFromSite: Error, {url} connection error！")
        return(newList)
    if response.status_code != 200:
        print(f"getOTALinkFromSite: Error, {url} post error!")
        return(newList)
    soup = BeautifulSoup(response.content, 'html.parser')
    link_tables = soup.find_all(name = "a", text = "下载ROM")
    for link_table in link_tables:
        if 'href' in list(link_table.attrs.keys()):
            link = link_table.attrs['href']
            newList.append(link)
            print(link)
            if lastest == 'yes': break
    return(newList)

def extendList(List, appendList = True, appendOther = False):
    newList = []
    for lists in List:
        if isinstance(lists, list) and appendList:
            newList.extend(lists)
        elif appendOther:
            newList.append(lists)
    return(newList)

def getOTALinksFromSite(models, version, lastest):
    if version == 'beta':
        version = '1'
    elif version == 'dev':
        version = '1b'
    else:
        version = '0'
    newLists = []
    pool = multiprocessing.Pool(multiprocessing.cpu_count())##创建进程池
    func = partial(getOTALinkFromSite, version = version, lastest = lastest)##固定不变的参数
    lists = extendList(pool.map(func, models.split(",")))##向进程池传入函数及其参数，让map执行
    newLists.extend(lists)
    pool.close()##不再创建进程池
    pool.join()##加入进程池
    return(newLists)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '一键获取小米机型更新地址（若太长时间未获取到地址，则视为获取失败）')
    #type是要传入的参数的数据类型  help是该参数的提示信息
    parser.add_argument('--model', '-m', type = str, required = True, help = '机型代号 格式：umi, 多个：umi,cmi,lmi')
    parser.add_argument('--version', '-v', type = str, required = False, default = 'beta', help = 'ROM发版类型, 稳定版(stable)/开发版(dev)/内测版(beta)')
    parser.add_argument('--lastest', '-l', type = str, required = False, default = 'no', help = '是否获取最新版, 是(yes)/否(no)')

    args = parser.parse_args()
    getOTALinksFromSite(args.model, args.version, args.lastest)
