#-*- coding:utf-8 -*-
import os
import re

from tkinter import *
from TkinterDnD2 import DND_FILES, TkinterDnD
import tkinter.ttk as ttk

from myfunc import *

class action:
    def __init__(self):
        # 메인 윈도우
        self.w_main = TkinterDnD.Tk()
        self.w_main.title('GUI')                  # 프로그램 타이틀
        self.w_main.geometry("1000x700+300+100")  # "GUI  윈도우 크기 + GUI 최초 실행 위치"
        self.w_main.minsize(1000, 700)             # GUI 윈도우 최소 사이즈
        # self.w_main.resizable(False, False)     # 사이즈 변경 불가

        # 메인 윈도우 내부에 그리드 생성 (3,1)
        Grid.rowconfigure(self.w_main, 0, weight=7)      # 행 세개 ( 행간 길이 비율 7:2:1 )
        Grid.rowconfigure(self.w_main, 1, weight=1)
        Grid.rowconfigure(self.w_main, 2, weight=1)
        Grid.columnconfigure(self.w_main, 0, weight=1)   # 열 하나

        # 탑 프레임
        self.f_top = Frame(self.w_main, width=900, height=500, relief="solid", bg = 'white')    # 탑프레임 : 메인 윈도우 안에, 배경색 = 흰색
        self.f_top.grid(row=0,column=0, sticky='nesw', padx=0, pady=0)  
        # 탑 프레임 내부에 그리드 생성 (1,2)
        Grid.rowconfigure(self.f_top, 0, weight=1)      # 행 하나
        Grid.columnconfigure(self.f_top, 0, weight=1)   # 열 두개
        Grid.columnconfigure(self.f_top, 1, weight=1) 
        ## 왼쪽 프레임
        self.f_left = Frame(self.f_top, width=1, height=500, relief="solid", bd =1, bg = 'lightyellow')   # 왼쪽 프레임 :  탑 프레임 안에, 테두리선 두께 = 1
        self.f_left.grid(row=0,column=0, sticky='nesw', padx=(10, 5), pady=0)                      # 첫 번째 열에 위치, 동서남북 확장, 왼쪽패딩=10, 오른쪽 패딩=5
        self.f_left.drop_target_register(DND_FILES)                                                       # 드레그앤 드롭
        self.f_left.dnd_bind('<<Drop>>', self.file_list)                                                  # 드롭될 경우 file_list 콜백
        ### 리스트박스 (변형전 파일 리스트)
        self.listb = Listbox(self.f_left, selectmode=EXTENDED, bg = 'lightyellow', width=1, height=30)  # 왼쪽 리스트박스
        self.scrbar = Scrollbar(self.f_left,orient='vertical')      # 왼쪽 스크롤
        self.file_path_list = []
        ### 드롭앤드랍 레이블
        self.l_dragndrop = Label(self.f_left, text="Drag & Drop", bg = 'lightyellow')   # 왼쪽 프레임 안에, 택스트 = 드레그엔드롭
        self.l_dragndrop.place(relx=.5, rely=.5, anchor="center")                       # 레이블 위치 중앙
        self.l_dragndrop.config(font=('Consolas',20))                                   # 레이블 폰트, 사이즈
        self.is_label_hidden=FALSE                                                      # 레이블 숨김 플래그 오프
        ## 오른쪽 프레임
        self.f_right= Frame(self.f_top, width=1, height=500, relief="solid", bd =1, bg = 'white')   # 오른쪽 프레임
        self.f_right.grid(row=0,column=1, sticky='nesw', padx=(5, 10), pady=0)                      # 두 번째 열에 위치, 동서남북 확장, 왼쪽패딩=5, 오른쪽 패딩=10
        ### 리스트박스 (변환된 결과 리스트)
        self.listb2 = Listbox(self.f_right, selectmode=EXTENDED, bg = 'lightyellow', width=1, height=30) # 오른쪽 리스트박스
        self.scrbar2 = Scrollbar(self.f_right,orient='vertical')                                         # 오른쪽 리스트박스 스크롤
        self.is_listb2_active = False
        self.matched_path_list = [] # 매칭된 파일 경로 리스트
        self.applied_path_list = [] # 변환된 파일 경로 리스트

        # 미드 프레임
        self.f_mid = Frame(self.w_main, width=900, height=100, relief="solid", bg = 'lightgreen')
        self.f_mid.grid(row=1,column=0, sticky='nesw', padx=0, pady=5)
        Grid.rowconfigure(self.f_mid, 0, weight=1)      # 행 하나
        Grid.columnconfigure(self.f_mid, 0, weight=95)  # 열 두개
        Grid.columnconfigure(self.f_mid, 1, weight=5)   
        ## 텍스트입력창 (정규표현식 입력)
        self.input_text = Entry(self.f_mid,width=100)
        self.textEntry = StringVar()
        self.textEntry.set("(?P<prefix>[a-zA-Z]{2,9})[-](?P<number>\d{3,6}).*?(?P<suffix>[A-J]?)$") # RTX-3090S
        self.input_text.config(textvariable = self.textEntry,justify='center')
        self.input_text.grid(row=0,column=0, padx=(10, 5), pady=(5, 5))
        # self.input_text.bind('<Button-1>', lambda: self.textEntry.set(""))
        ## 버튼 
        self.b_match   = Button(self.f_mid, text='Match',command=self.match_filter)
        self.b_match.grid(row=0,column=1, padx=(5, 10), pady=(5, 5))

        # 바텀 프레임
        self.f_bot = Frame(self.w_main, width=900, height=50, relief="solid", bg = 'white')
        self.f_bot.grid(row=2,column=0, sticky='nesw', padx=10, pady=5)  
        ## 버튼 
        self.b_apply = Button(self.f_bot, text='Apply',command=self.apply_files)
        self.b_rename    = Button(self.f_bot, text='Rename',command=self.rename_file)
        self.b_exit  = Button(self.f_bot, text='Exit',command=self.w_main.quit)
        self.b_default = Button(self.f_bot, text='Default',command=self.reset_listb)
        ## 버튼 위치
        self.b_apply['state'] = DISABLED
        self.b_rename['state'] = DISABLED
        self.b_exit.pack(side = "right", padx=10, pady=10)
        self.b_apply.pack(side = "right", padx=10, pady=10)
        self.b_rename.pack(side = "right", padx=10, pady=10)
        self.b_default.pack(side = "left", padx=10, pady=10)
        ##
        self.prog_var = DoubleVar()
        self.prog_bar = ttk.Progressbar(self.f_bot, maximum = 100, length = 200, variable=self.prog_var)
        # self.l_state   = Label( self.f_bot, text='ready', width=20)
        # self.l_state.pack(anchor='center', padx=10, pady=10)
        
        self.w_main.mainloop() # 실행

    # 드롭시 콜백하는 함수
    def file_list(self,event):
        # 드래그 엔 드롭으로 얻은 (파일 및 폴더의 경로 리스트)를 tmp_file_path_list에 저장.
        tmp_file_path_list = self.listb.tk.splitlist(event.data)

        # (파일 및 폴더의 경로 리스트)를 이용하여 (파일 경로 리스트)를 저장.
        for path in tmp_file_path_list:
            #파일일 경우
            if os.path.isfile(path):                   
                if not path in self.file_path_list:    #중복된 파일은 리스트에 추가하지 않는다.
                    self.file_path_list.append(path)   #경로 리스트에 파일 경로 추가.
                    self.listb.insert('end', path)     #왼쪽 리스트박스에 삽입
            #폴더일 경우
            elif os.path.isdir(path):
                for file_name_in_dir in os.listdir(path):               
                    new_file_path = path+'/'+file_name_in_dir #새로운 파일 주소 = 폴더주소/파일이름
                    if os.path.isfile(new_file_path):                   #폴더 내부의 파일만 로드한다.
                        if not new_file_path in self.file_path_list:    #중복된 파일은 리스트에 추가하지 않는다.
                            self.file_path_list.append(new_file_path)   #파일 이름만 떼어서
                            self.listb.insert('end', new_file_path)  #왼쪽 리스트박스에 삽입
                    else:
                        continue # 폴더 안의 폴더는 로드하지 않는다.
            else:                # 폴더도 파일도 아닌 경우
                continue         # 무시한다.

        # 드레그앤드롭 레이블을 숨기고 대신 그 위치에 리스트 박스를 위치시키고 스크롤을 붙여준다.
        if self.file_path_list != []:                                  # 리스트박스가 비어있지 않은 경우에만 실행된다.
            self.l_dragndrop.place_forget()                            # 드래그앤드롭 레이블을 숨긴다.
            self.listb.pack(side='left', expand = True, fill='both')   # 리스트박스를 위치시킨다.
            if not self.is_label_hidden:                                    # 왼쪽 리스트박스가 활성화된 경우 (드래그앤드롭 레이블이 비활성화 된 경우)
                self.scrbar.config(command=self.listb.yview)                # 왼쪽 리스트박스에 부착
                self.scrbar.pack(side='right',fill='y')                     # 왼쪽 스크롤 활성화
                self.listb.config(yscrollcommand=self.scrbar.set)           # 리스트박스-스크롤 연결
            self.is_label_hidden = TRUE                                # 드래그앤드롭 숨김 플레그 온

    # 리셋 버튼을 누를시 실행           
    def reset_listb(self):
        self.file_path_list = []    # 파일 경로 리스트 초기화
        self.matched_path_list = [] # 매칭된 경로 리스트 초기화
        self.applied_path_list = [] # 변환된 경로 리스트 초기화
        self.listb.delete(0,END)    # 왼쪽 리스트박스 원소 삭제
        self.listb2.delete(0,END)   # 오른쪽 리스트박스 원소 삭제
        self.scrbar.pack_forget()    # 왼쪽 스크롤바 숨김
        self.listb.pack_forget()     # 왼쪽 리스트박스 숨김
        self.scrbar2.pack_forget()   # 오른쪽 스크롤바 숨김
        self.listb2.pack_forget()    # 오른쪽 리스트박스 숨김
        self.prog_bar.pack_forget()
        self.prog_var.set(0)
        self.b_rename['state'] = DISABLED
        self.b_apply['state'] = DISABLED
        self.l_dragndrop.place(relx=.5, rely=.5, anchor="center") # 드래그앤드롭 레이블 재위치시킴
        self.is_label_hidden=FALSE                                # 드래그앤 드롭 숨김 플레그 오프
        self.is_listb2_active = False

    # 매치 버튼을 누를시 실행
    def match_filter(self):
        self.matched_path_list = []
        # 이 함수는 매칭할 파일 리스트가 있는 경우에만 실행.
        if self.file_path_list == []: return
        
        new_file_path_list = []
        # 파일 경로 리스트의 파일경로
        for file_path in self.file_path_list:
            file_dir,file_name = os.path.split(file_path)
            if file_dir[-1] =='/':
                file_dir = file_dir[:-1]
            file_base,file_ext = os.path.splitext(file_name)
            patrn = re.compile('.*?(?P<prefix>[a-zA-Z]{2,9})[-](?P<number>\d{3,6}).*?(?P<suffix>[A-P])?$')
            m = patrn.search(file_base)
            
            if m == None:
                continue
            else:
                new_file_path_list.append(file_path)
            prefix = m.group("prefix").upper()
            number = m.group("number")
            suffix = m.group("suffix")
            if suffix != None:
                # _4K 인 경우는 제외
                if suffix == 'K' and file_base[-2] == '4':
                    suffix = None
                new_file_base = prefix+'-'+number+suffix
            else:
                new_file_base = prefix+'-'+number
            new_file_name = new_file_base+file_ext
            new_file_path = file_dir+'/'+new_file_name
            self.matched_path_list.append(new_file_path)
        self.file_path_list = new_file_path_list
        # 이후는 matched 리스트가 있는 경우에만 실행된다.
        if self.matched_path_list == []: 
            self.reset_listb()
            return
        self.b_apply['state'] = NORMAL

        if not self.is_listb2_active:
            self.listb2.pack(side='left', expand = True, fill='both')                                              
            self.scrbar2.config(command=self.listb2.yview)                                                   
            self.scrbar2.pack(side='right',fill='y')
            self.listb2.config(yscrollcommand=self.scrbar2.set)
            self.is_listb2_active = True  

        # 왼쪽 리스트 박스
        self.listb.delete(0,END)
        for file_path in self.file_path_list:
            self.listb.insert('end', file_path)

        # # 오른쪽 리스트박스 
        self.listb2.delete(0,END)
        for new_file_path in self.matched_path_list:
            self.listb2.insert('end', new_file_path)

    # 적용 버튼을 누를시 실행
    def apply_files(self):
        if self.matched_path_list == []: return

        new_file_path_list = []
        new_matched_path_list = []
        for old_path, new_path in zip(self.file_path_list,self.matched_path_list):
            # 변환된 파일명이 기존 파일명과 같은 경우 다음 파일로
            if old_path == new_path: 
                continue

            if os.path.exists(new_path):
                # 대소문자만 다를경우 중복체크 할 필요없음
                if regularize_file_path(old_path)==new_path:
                    new_matched_path_list = self.matched_path_list
                    new_file_path_list = self.file_path_list
                    break
                
                # 중복파일일 경우
                count = 1
                new_file_dir, new_file_name = os.path.split(new_path)
                new_file_base, new_file_ext = os.path.splitext(new_file_name)
                if new_file_dir[-1] =='/':
                    new_file_dir = new_file_dir[:-1]
                while(os.path.exists(new_path)):
                    new_path = new_file_dir+'/'+new_file_base+f' ({count})'+new_file_ext
                    if old_path == new_path:
                        break
                    count += 1

            new_file_path_list.append(old_path)
            new_matched_path_list.append(new_path)

        if new_matched_path_list == []:
            self.file_path_list = []
            self.matched_path_list = []
            self.listb.delete(0,END)
            self.listb2.delete(0,END)
            return None
        self.file_path_list = new_file_path_list
        self.matched_path_list = new_matched_path_list
        # 왼쪽 리스트 박스
        self.listb.delete(0,END)
        for file_path in self.file_path_list:
            self.listb.insert('end', file_path)
        # 오른쪽 리스트박스 
        self.listb2.delete(0,END)
        for new_file_path in self.matched_path_list:
            self.listb2.insert('end', new_file_path)
        self.b_apply['state'] = DISABLED
        self.b_rename['state'] = NORMAL
        
    # 리네임 버튼을 누를시 실행
    def rename_file(self):
        if self.matched_path_list == []: return
        list_len = len(self.file_path_list)
        for index, old_path, new_path in zip(range(list_len),self.file_path_list,self.matched_path_list):
            if old_path==new_path:
                continue
            os.rename(old_path,new_path)
            self.prog_bar.pack(side = "right", padx=5, pady=10)
            self.prog_var.set((index+1)/list_len*100)
            if index%10 == 0:
                self.prog_bar.update
        self.reset_listb()

action()















    