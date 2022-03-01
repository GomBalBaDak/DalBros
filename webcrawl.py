import requests
from bs4 import BeautifulSoup

import urllib.request
import os

def save_img(url_list):
    for count, url in zip(range(len(url_list)), url_list):
        dir_path = r'C:\Users\darau\Downloads\crawled_img'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        filename = f'\{count}.jpg'
        fullpath = dir_path + filename
        urllib.request.urlretrieve(url, fullpath)

def save_img_from_url(url,file_name):
    dir_path = r'C:\Users\darau\Downloads\crawled_img'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_name = f'\{file_name}.jpg'
    full_path = dir_path + file_name
    urllib.request.urlretrieve(url, full_path)

import re

def get_reg_name(prod_name):
    url = f'https://jav.land/en/id_search.php?keys={prod_name}'
    req = requests.get(url)
    soup = BeautifulSoup(req.content,"html.parser")
    reg_name_source = soup.find("td", attrs = {"width":"80%"})
    patrn = re.compile('^<td width="80%">(?P<reg_name>[a-zA-Z0-9]{2,})<\/td>$')
    m = patrn.search(str(reg_name_source))
    if m!= None:
        return m.group("reg_name")
    else:
        return None

def get_img_url(prod_name):
    reg_prod_name = get_reg_name(prod_name)
    return f'https://pics.vpdmm.cc/digital/video/{reg_prod_name}/{reg_prod_name}pl.jpg'

def get_imgs_from_prod_name_list(prod_name_list):
    for prod_name in prod_name_list:
        img_url= get_img_url(prod_name)
        save_img_from_url(img_url,prod_name)

def get_prod_name_from_path(full_path):
    file_name = os.path.split(full_path)[1] # (dir_path, file_name)
    prod_name = os.path.splitext(file_name)[0] # (prod_name, .file_ext)
    return prod_name

import mimetypes
import re

def get_type_of_file(full_path):
    mime_type = mimetypes.guess_type(full_path)[0] # 결과는 튜플 ('maintype/subtype',encoding) 의 형태

    # 정규표현식을 써서 maintype만 뽑아서 파일의 유형을 확인한다.
    patrn = re.compile('^(?P<maintype>.+)\/(?P<subtype>.+)$')
    m = patrn.search(mime_type)
    file_type = m.group('maintype')
    return file_type


def find_all_video(dir_path,video_file_dict={}):
    for path in os.listdir(dir_path):
        # 파일인 경우
        if os.path.isfile(path):
            if get_type_of_file(path) == 'video':
                dir_path, file_name = os.path.split(path)
                product_id = os.path.splitext(file_name)[0]
                product_id = get_prod_name_from_path(path).upper()
                content_id = get_reg_name(product_id)

                subtitle_smi_path = os.path.join(dir_path,product_id+'.smi')
                subtitle_srt_path = os.path.join(dir_path,product_id+'.srt')

                is_substitle_exist = False
                subtitle_path = None
                if os.path.exists(subtitle_smi_path):
                    is_substitle_exist = True
                    subtitle_path = os.path.join(dir_path,product_id+'.smi')
                if os.path.exists(subtitle_srt_path):
                    is_substitle_exist = True
                    subtitle_path = os.path.join(dir_path,product_id+'.srt')

                video_file_dict[product_id] = (file_name,content_id,path,is_substitle_exist,subtitle_path)
        # 폴더인 경우
        elif os.path.isdir(path):
            find_all_video(path,video_file_dict)
    
    return video_file_dict

get_prod_name_from_path(r'D:\NAS_Data3\[download]\JAV\ABW-135.mp4')