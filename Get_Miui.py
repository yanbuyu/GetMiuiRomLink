# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import sys

region_map={'国行版': 'CN', '俄罗斯版 (俄版) (RU)': 'RU', '全球版': 'Global', '印度尼西亚版 (印尼版) (ID)': 'ID', '印度版 (IN)': 'IN', '欧洲版 (欧版) (EEA)': 'EEA', '土耳其版 (TR)': 'TR', '台湾版 (台版) (TW)': 'TW', '日本版 (日版) (JP)': 'JP', '新加坡版': 'SG'}

def contain_english(string):
    return bool(re.search('[A-Z]', string))

def get_model_link_table():

    link = 'https://xiaomirom.com/series/'
    response = requests.get(link)
    soup=BeautifulSoup(response.content,'html.parser')
    link_table = soup.find_all(name='dl',attrs={'class':'row series__dl'})[0].contents
    model_link_table_dic = {}
    model_name_pattern = re.compile(r"[(](.*)[)]")
    for i in range(0,len(link_table),2):
        model_name = re.findall(model_name_pattern,link_table[i].a.contents[0])[0]
        a_tags = link_table[i+1].find_all(name='a')
        model_region_link_dic = {}
        for a in a_tags:
            region = a.contents[0]
            model_region_link_dic[region_map[region]]=a.attrs["href"]
        model_link_table_dic[model_name] = model_region_link_dic


    '''
        the dictionary like this:
        {
            <model_name>:{
                <region>:<link>
            }
        }

    '''
    return model_link_table_dic

def get_rom_link(model_version_link):
    miui_rom_link ="https://bigota.d.miui.com/"
    response = requests.get(model_version_link)
    soup = BeautifulSoup(response.content,'html.parser')
    rom_div = soup.find_all(name='div',attrs={'class':'content mb-5 rom-body'})[0].contents
    # rom_div.find_all
    pattern = re.compile(r'<p>(.*?)<a(.*?)>下载</a></p>')
    rom_link_dic={"recovery":{"stable":[],"beta":[]}, "fastboot":[]}
    for tag in rom_div:
        rom_name = re.findall(pattern,str(tag))
        if not rom_name == []:
            rom_name = rom_name[0][0][:-3]
            rom_version = rom_name.split("_")[2]
            rom_link = miui_rom_link+rom_version+"/"+rom_name
            # print(rom_name.split(".")[-1])
            if rom_name.split(".")[-1] == "zip":
                if contain_english(rom_version):
                    rom_link_dic["recovery"]["stable"].append(rom_link)
                else:
                    rom_link_dic["recovery"]["beta"].append(rom_link)
            else:
                rom_link_dic["fastboot"].append(rom_link)
    return rom_link_dic

def query_rom_link(model_name,region,rom_cleases,rom_version=None):
    '''
        该函数用于查询miui rom链接
        参数解释：
            model_name:机型代号，如：小米10的代号就是umi
            region：机型地区，CN EEN IN 等等
            rom_cleases：rom类型  recovery或fastboot
            rom_version： 卡刷包（recovery）版本 beta 或 stable  注：线刷包无该选项
    '''
    model_link_table_dic=get_model_link_table()
    if region in model_link_table_dic[model_name].keys():
        rom_link_dic=get_rom_link(model_link_table_dic[model_name][region])
    else:
        print("Already have:")
        print(list(model_link_table_dic[model_name].keys()))
        print()
        print()
        raise KeyError("This region type was not found")

    if rom_cleases in rom_link_dic.keys():
            rom_link_list=rom_link_dic[rom_cleases]
    else:
        print("Already have:")
        print(list(rom_link_dic.keys()))
        print()
        print()
        raise KeyError("This rom classes was not found")

    if rom_cleases == "recovery":
        if rom_version in rom_link_dic[rom_cleases].keys():
            rom_link_list=rom_link_dic[rom_cleases][rom_version]
        else:
            print("Already have:")
            print(list(rom_link_dic[rom_cleases].keys()))
            print()
            print()
            raise KeyError("This rom version was not found")    

    rom_link_list.sort(key=lambda x: x.split("_")[2],reverse = True)

    return rom_link_list



if __name__ == '__main__':
    
    try:
        DEVICE_CODE = str(sys.argv[1])
    except IndexError:
        print('\nUsage: Get_Miui.py <DEVICE_CODE>\n')
        print('    <DEVICE_CODE>: Device\'s Code eg.umi\n')
        try:
            input = raw_input
        except NameError: pass
        input('Press ENTER to exit...')
        sys.exit()


    print(query_rom_link(DEVICE_CODE, "CN", "recovery", "beta")[0])
    
