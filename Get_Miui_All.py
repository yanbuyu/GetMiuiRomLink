# -*- coding: utf-8 -*-
import re, sys, argparse, requests
from bs4 import BeautifulSoup
from functools import cmp_to_key

class MIUI_ROM:
    def __init__(self):
        self.region_map={'国行版': 'CN', '俄罗斯版 (俄版) (RU)': 'RU', '全球版': 'Global', '印度尼西亚版 (印尼版) (ID)': 'ID', '印度版 (IN)': 'IN', '欧洲版 (欧版) (EEA)': 'EEA', '土耳其版 (TR)': 'TR', '台湾版 (台版) (TW)': 'TW', '日本版 (日版) (JP)': 'JP', '新加坡版': 'SG'}
        self.model_link_table_dic=self.get_model_link_table()

    def get_model_link_table(self):

        link = 'https://xiaomirom.com/series/'
        response = requests.get(link)
        if not response.status_code == 200:
            raise RuntimeError(link+" "+"请求异常！")
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
                model_region_link_dic[self.region_map[region]]=a.attrs["href"]
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

    def get_rom_link(self,model_version_link):
        miui_rom_link ="https://bigota.d.miui.com/"
        response = requests.get(model_version_link)
        if not response.status_code == 200:
            raise RuntimeError(model_version_link+" "+"请求异常！")
            
        soup = BeautifulSoup(response.content,'html.parser')
        try:
            rom_div = soup.find_all(name='div',attrs={'class':'content mb-5 rom-body'})[0].contents
        except IndexError:
            rom_div = soup.find_all(name='div',attrs={'class':'content mb-5 featured-body'})[0].contents
        finally:
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
                        if self.contain_english(rom_version):
                            rom_link_dic["recovery"]["stable"].append(rom_link)
                        else:
                            rom_link_dic["recovery"]["beta"].append(rom_link)
                    else:
                        rom_link_dic["fastboot"].append(rom_link)
            return rom_link_dic
    
    def query_link(self,model_name,region,rom_cleases,rom_version=None):
        '''
            该函数用于查询miui rom链接
            参数解释：
                model_name:机型代号，如：小米10的代号就是umi
                region：机型地区，CN EEN IN 等等
                rom_cleases：rom类型  recovery或fastboot
                rom_version： 卡刷包（recovery）版本 beta 或 stable  注：线刷包无该选项
        '''
        if not model_name in self.model_link_table_dic.keys():
            print("Already have:")
            print(list(self.model_link_table_dic.keys()))
            print()
            print()
            raise KeyError("This model type was not found")

        if region in self.model_link_table_dic[model_name].keys():
            rom_link_dic=self.get_rom_link(self.model_link_table_dic[model_name][region])
        else:
            print("Already have:")
            print(list(self.model_link_table_dic[model_name].keys()))
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

        # rom_link_list.sort(key=lambda x: x.split("/")[3],reverse = True)
        rom_link_list.sort(key=cmp_to_key(self.f),reverse = True)

        return rom_link_list

    def query_link_print(self, device, region, cleases, version, lastest):
        if version == 'dev':
            getLinks = MIUI_ROM.query_link(self, device, region, cleases, 'stable')
        else:
            getLinks = MIUI_ROM.query_link(self, device, region, cleases, version)
        getNewLinks = []
        if version == 'dev':##从稳定版中分离开发版
            for getLink in getLinks:
                cuts = getLink.split('/')
                if cuts and cuts[3].endswith('.DEV'): getNewLinks.append(getLink)
        elif version == 'stable':
            for getLink in getLinks:
                cuts = getLink.split('/')
                if cuts and not cuts[3].endswith('.DEV'): getNewLinks.append(getLink)
        if version != 'beta': getLinks = getNewLinks
        if lastest == 'yes' and getLinks:
            return([getLinks[0]])
        return(getLinks)

    def f(self,a,b):
        return self.version_comparetor(a.split("/")[3],b.split("/")[3])

    def version_comparetor(self,a, b):
        if len(a)==0: return 0
        if a.split(".")[0] == b.split(".")[0]:
            return self.version_comparetor('.'.join(a.split(".")[1:]), '.'.join(b.split(".")[1:]))
        if not self.contain_english(a.split(".")[0]):
            if int(a.split(".")[0]) > int(b.split(".")[0]):
                return 1
            elif int(a.split(".")[0]) < int(b.split(".")[0]):
                return -1
        else:
            if a.split(".")[0] > b.split(".")[0]:
                return 1
            elif a.split(".")[0] < b.split(".")[0]:
                return -1

    def contain_english(self,string):
        return bool(re.search('[A-Z]', string))





if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = '一键获取小米机型更新地址')
    #type是要传入的参数的数据类型  help是该参数的提示信息
    parser.add_argument('--device', '-d', type = str, required = True, help = '机型代号, 填写对应机型的代号, 如小米10的代号为umi')
    parser.add_argument('--region', '-r', type = str, required = False, default = 'CN', help = '地区代号, 请输入地区代号')
    parser.add_argument('--cleases', '-c', type = str, required = False, default = 'recovery', help = 'ROM包类型, 卡刷包(recovery)/线刷包(fastboot), 绝大部分开发版机型无线刷包')
    parser.add_argument('--version', '-v', type = str, required = False, default = 'beta', help = 'ROM发版类型, 稳定版(stable)/开发版(dev)/内测版(beta)')
    parser.add_argument('--lastest', '-l', type = str, required = False, default = 'no', help = '是否获取最新版, 是(yes)/否(no)')

    args = parser.parse_args()
    getLinks = MIUI_ROM().query_link_print(args.device, args.region, args.cleases, args.version, args.lastest)
    [print(link) for link in getLinks]
