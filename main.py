import requests as rq
import re
import os
import yaml
import time
urls = [input('请输入b站网址')]
header = {
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
             ' Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
'Cookie':'',
'Referer':''
}
# 以下两个参数表明要获取mp3还是mp4
get_mp3 = True
get_mp4 = True
# 如果在允许的情况下, 将音视频合并
hebing = True
# 合并完的情况下要不要删除原来的mp3和mp4
delete_origin = False
# 四种保存命名的方式, 在有合集的情况下
# --1第一种是建立合集文件夹, 文件直接用子标题命名.
# --2第二种是建立合集文件夹, 里面再建立子文件夹, 再保存result文件
# --3第三种是不用合集文件夹, 文件直接用子标题命名
# --4第四种是, 直接在当前文件夹保存result文件
way_to_save = 2
# 多下载模式和多下载的个数
multi_download = False
multi_sum = 1
multi_down_all = False
# 初始的文件夹名字, 要在最后加/
dir_name = './bilibili/'
wait_time = 0
# 如果是多下载模式, 那么就还有当前的页数
curindex = -1
xuanji = False
heji = False
data_a = 0
data_v = 0
def getdirname(filename):
    filename = re.sub('\?|\*|"|:','',filename)
    filename = re.sub('<|>|\||\:', '', filename)
    filename = re.sub('/|\'|%|&|!|;', '', filename)
    return filename


def getconfig():
    global get_mp3, get_mp4, hebing, delete_origin, way_to_save, multi_download, multi_sum, multi_down_all, dir_name, wait_time
    if os.path.exists('./config.yaml'):
        with open('./config.yaml','r',encoding='utf-8') as fp:
            data = yaml.load(fp,Loader=yaml.FullLoader)
        if 'get_mp3' in data:
            get_mp3 = data['get_mp3']
        if 'get_mp4' in data:
            get_mp4 = data['get_mp4']
        if 'hebing' in data:
            hebing = data['hebing']
        if 'delete_origin' in data:
            delete_origin = data['delete_origin']
        if 'way_to_save' in data:
            way_to_save = data['way_to_save']
        if 'multi_download' in data:
            multi_download = data['multi_download']
        if 'multi_sum' in data:
            multi_sum = data['multi_sum']
        if 'multi_down_all' in data:
            multi_down_all = data['multi_down_all']
        if 'dir_name' in data:
            dir_name = data['dir_name']
        if 'wait_time' in data:
            wait_time = data['wait_time']
        if 'cookie' in data:
            header['Cookie'] = data['cookie']
temp_res = rq.get(url=urls[0], headers=header).text
def set_name_and_url():
    global urls, dir_name, curindex, xuanji, heji
    # 合集选集判断主要是为了命名合适, 然后后面到底要不要解析链接就看之前的参数有没有设置多下载
    # 搜得到就是选集模式
    # "cur-page" 这个东西搜出来后面跟着的就是合集的当前集数
    if re.match('.*multi_page',temp_res, re.S):
        if way_to_save <=2:
            dir_name = re.match('.*window.__INITIAL_STATE__.+?"title":"(.+?)"', temp_res, re.S).group(1)
            dir_name = getdirname(dir_name)
            dir_name = './bilibili/' + dir_name + '/'
        if multi_download:
            temp = re.match('.*"cur-page".+?\((\d*)/(\d*)\)', temp_res, re.S)
            curindex = int(temp.group(1)) - 1
            temp_sum = int(temp.group(2))
            url = re.sub('\?.*', '', urls[0])
            bvid_list = list()
            for i in range(1,temp_sum+1):
                bvid_list.append(url+'?p='+str(i))
            urls = bvid_list
        xuanji = True
    # 这个搜得到就是合集模式
    elif re.match('.*"ugc_season"(.*?)"embedPlayer":',temp_res,re.S):
        part = re.match('.*"ugc_season"(.*?)"embedPlayer":', temp_res, re.S).group(1)
        if way_to_save<=2:
            dir_name = re.match('.*?"title":"(.*?)"', part, re.S).group(1)
            dir_name = getdirname(dir_name)
            dir_name = './bilibili/' + dir_name + '/'
        bvid_list = re.findall('"bvid":"(.*?)"', part, re.S)
        if multi_download:
            for i in range(len(bvid_list)):
                bvid_list[i] = 'https://www.bilibili.com/video/'+bvid_list[i]+'/'
            temp = re.match('.*"cur-page".+?\((\d*)/\d*\)', temp_res, re.S)
            curindex = int(temp.group(1)) - 1
            urls = bvid_list
        heji = True
# 所以不能同时为真, 别乱玩就行
def getdownload():
    global get_mp3, get_mp4, urls, curindex, dir_name, xuanji, heji, data_a, data_v,multi_sum
    try:
        # 这是防止之前的参数乱调而设置的, 保持当前要下载的序号正确, 保持要下载的数量正确, 然后这个也可以作为下载全部的设置
        # 其实是可有可无的, 因为初始值是正确的没改动, 在这里加点就是多一重保险
        if not multi_download:
            curindex = 0
            multi_sum = 1
        elif multi_down_all:
            curindex = 0
            multi_sum = -1
        if not heji and not xuanji:
            curindex = 0
            multi_sum = 1
        for i in range(curindex,len(urls)):
            if i == curindex + multi_sum:
                break
            print(str(i + 1) + '-----------------------------------------------------')
            if multi_sum<0:
                print(str(len(urls)) + '-----------------------------------------------------')
            else:
                print(str(min(curindex + multi_sum, len(urls))) + '-----------------------------------------------------')
            url = urls[i]
            header['Referer'] = url
            text = rq.get(url=url,headers=header).text
            if get_mp3:
                url_a = re.match('.*"audio":.+?"baseUrl":"(.+?)"', text, re.S).group(1)
                print('音频链接', url_a)
                print('获取音频文件中...')
                res_a = rq.get(url=url_a, headers=header)
                if res_a.status_code == 403:
                    print('音频获取失败')
                    get_mp4 = False
                else:
                    data_a = rq.get(url=url_a, headers=header).content
                    print('获取音频成功')
            if get_mp4:
                url_v = re.match('.*"video":.+?"baseUrl":"(.+?)"',text, re.S).group(1)
                print('视频链接', url_v)
                print('获取视频文件中...')
                res_v = rq.get(url=url_v, headers=header)
                if res_v.status_code == 403:
                    print('视频获取失败')
                    get_mp4 = False
                else:
                    data_v = rq.get(url=url_v, headers=header).content
                    print('获取视频成功')
            if get_mp4 or get_mp3:
                final_dir_name = dir_name
                if way_to_save in [1,2,3]:
                    filename = ''
                    temp = re.match('.*title data-vue-meta.*?>(.+?)_哔哩哔哩_bilibili',text,re.S)
                    if temp:
                        filename = temp.group(1)
                    else:
                        filename = re.match('.*title data-vue-meta.*?>(.+?)</title>',text,re.S).group(1)
                    filename = getdirname(filename)
                    if way_to_save==2:
                        final_dir_name+=filename+'/'
                        filename = 'result'
                else:
                    filename = 'result'
                file1 = final_dir_name + filename + '.mp3'
                file2 = final_dir_name + filename + '.mp4'
                if get_mp3:
                    print(file1)
                    if not os.path.exists(file1):
                        if not os.path.exists(final_dir_name):
                            os.makedirs(final_dir_name)
                        print('保存音频文件中...')
                        with open(file1, 'wb') as fp:
                            fp.write(data_a)
                        print('保存音频成功')
                if get_mp4:
                    print(file2)
                    if not os.path.exists(file2):
                        if not os.path.exists(final_dir_name):
                            os.makedirs(final_dir_name)
                        print('保存视频文件中...')
                        with open(file2, 'wb') as fp:
                            fp.write(data_v)
                        print('保存视频成功')
                if get_mp3 and get_mp4 and hebing:
                    if not os.path.exists(final_dir_name + filename + '--.mp4'):
                        if not os.path.exists(final_dir_name):
                            os.makedirs(final_dir_name)
                    result = final_dir_name + filename + '--.mp4'
                    os.system(f"ffmpeg.exe -i \"{file1}\" -i \"{file2}\" -acodec copy -vcodec copy \"{result}\"")
                    print("音视频合并成功")
                    if delete_origin:
                        os.remove(file1)
                        os.remove(file2)
                        print('分文件删除成功')
            time.sleep(wait_time)
    except:
        print('发生错误')
getconfig()
set_name_and_url()
getdownload()
print('done')
input('按任意键退出')