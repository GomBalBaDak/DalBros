import requests
from bs4 import BeautifulSoup
import mimetypes

import os
import re

    
# (파일의 경로)를 입력 받아 
# 해당 파일의 (파일 유형)을 리턴 (ex: 'photo')
def get_type_of_file_from_full_path(full_path):
    # 해당 경로가 파일 경로가 아닌 경우 None 리턴
    if not os.path.isfile(full_path):
        return None
    
    mime_type = mimetypes.guess_type(full_path)[0] # ('maintype/subtype',encoding)
    # 파일 유형을 찾지 못한 경우 None 리턴
    if mime_type == None:
        return None

    # 정규표현식을 써서 파일의 유형을 확인한다.
    patrn = re.compile('^(?P<maintype>.+)\/(?P<subtype>.+)$')
    m = patrn.search(mime_type)
    # 패턴 매칭이 안된 경우 None 리턴
    if m.group('maintype') == None:
        return None
    # 파일의 유형은 maintype이 말해준다.
    file_type = m.group('maintype')
    return file_type

# (폴더 경로)를 입력 받아
# 해당 폴더 아래의 모든 비디오 파일을 검색.
# 검색된 모든 비디오 파일들의 경로를 리턴
def get_video_path_list_from_dir_path(dir_path,video_path_list=[]):
    if not os.path.isdir(dir_path):
        return None
    # 폴더 내부의 모든 파일 및 경로를 따라가며
    for path in os.listdir(dir_path):
        # 경로가 파일 경로인 경우
        if os.path.isfile(path):
            # 파일이 비디오 유형인 경우
            if get_type_of_file_from_full_path(path) == 'video':
                video_path_list.append(path)
        # 경로가 폴더 경로인 경우
        elif os.path.isdir(path):
            get_video_path_list_from_dir_path(path,video_path_list)
    # 폴더 내부의 
    return video_path_list            

# 파일의 이름을 입력받아
# 정규화된 파일 이름을 리턴.
def regularize_file_name(file_name):
    # 정규표현식 매칭
    file_base, file_ext = os.path.splitext(file_name) # (file_base, .file_ext)
    patrn = re.compile('.*?(?P<prefix>[a-zA-Z]{2,9})[-](?P<number>\d{3,6}).*?(?P<suffix>[A-P])?$')
    m = patrn.search(file_base)
    if m == None: return None

    # 새 파일 이름을 정의
    prefix = m.group('prefix').upper()
    number = m.group('number')
    # 접미사가 없는 경우
    if m.group('suffix') == None:
        new_file_base = prefix+'-'+number
        new_file_name = new_file_base+file_ext
    # 접미사가 있는 경우
    else:
        suffix = m.group('suffix')
        new_file_base = prefix+'-'+number+suffix
        new_file_name = new_file_base+file_ext
    return new_file_name

# 파일의 경로를 입력받아
# 정규화된 파일 경로를 리턴.
def regularize_file_path(file_path):
    if not os.path.exists(file_path): return
    if not os.path.isfile(file_path): return

    dir_path, file_name = os.path.split(file_path)
    # 최상위 폴더 경로일 경우 (eg. D://) /문자 하나를 지워준다.
    if dir_path[-1] =='/':
        dir_path = dir_path[:-1]

    new_file_name = regularize_file_name(file_name)
    
    # 새 파일 경로 정의
    new_file_path = dir_path+'/'+new_file_name
    return new_file_path


# Product_ID를 입력 받아서 CID를 리턴
def get_CID_from_PID(PID):
    url = f'https://jav.land/en/id_search.php?keys={PID}'
    req = requests.get(url)
    soup = BeautifulSoup(req.content,"html.parser")
    CID_source = soup.find("td", attrs = {"width":"80%"})
    patrn = re.compile('^<td width="80%">(?P<CID>.{3,})<\/td>$')
    m = patrn.search(str(CID_source))
    if m!= None:
        return m.group('CID')
    else: 
        return None
















