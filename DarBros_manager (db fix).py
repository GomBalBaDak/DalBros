import os
import re
import time
import math
import pandas as pd
from PIL import Image as Ig
from PIL import ImageTk

from tkinter import *
from TkinterDnD2 import DND_FILES, TkinterDnD
import tkinter.ttk as ttk

from myfunc import *


class ClickLabel(Label):
    def __init__(self, master, **kw):
        Label.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.bind("<Button-1>", self.on_click)

    def on_click(self, e):
        self.config(bg='blue')

class action:
    def __init__(self):
        # 메인 윈도우
        self.w_main = TkinterDnD.Tk()
        self.w_main.iconbitmap(r'C:\Users\darau\Desktop\Python Projects\WebCrawl\DarBros64.ico')
        self.w_main.title('GUI')                  # 프로그램 타이틀
        self.w_main.geometry("1200x800+300+100")  # "GUI  윈도우 크기 + GUI 최초 실행 위치"
        self.w_main.minsize(1100, 800)            # GUI 윈도우 최소 사이즈
        # self.w_main.resizable(False, False)     # 사이즈 변경 불가
        
        # 메뉴
        self.menu_bar = Menu(self.w_main)
        ## 파일 메뉴
        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="파일", menu=self.menu_file)
        self.menu_file.add_command(label="파일 가져오기", command=None)
        self.menu_file.add_command(label="폴더 가져오기", command=None)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="종료하기", command=self.save_n_exit)
        ## 편집 메뉴
        self.menu_edit = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="편집", menu=self.menu_edit)
        self.menu_edit.add_command(label="메타데이터 모두 삭제", command=self.clear_data_csv)
        self.menu_edit.add_command(label="메타데이터 찾기", command=self.find_meta_data)
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="ㅌㅌ", command=self.w_main.quit)
        self.w_main.config(menu=self.menu_bar)
        ## 보기 메뉴
        self.menu_edit = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="보기", menu=self.menu_edit)
        self.menu_edit.add_command(label="그리드 뷰", command=self.show_grid_view)
        self.menu_edit.add_command(label="테이블 뷰", command=self.show_table_view)
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="ㅌㅌ", command=self.w_main.quit)
        self.w_main.config(menu=self.menu_bar)
        ## 종료 버튼
        self.w_main.protocol("WM_DELETE_WINDOW", self.save_n_exit) # 종료버튼 리매핑


        # 탑 프레임
        self.f_top = Frame(self.w_main, width=1, height=60, relief="solid", bg = 'lightgray')    
        self.f_top.pack(side='top',fill='x',pady=(0,1))
        self.top_btn = Button(self.f_top, text = 'asdf',height=3,width=10)
        self.top_btn.pack(anchor='w',fill='y',padx=5, pady=1)

        # 바텀 프레임
        self.f_bot = Frame(self.w_main, width=1, height=30, relief="solid", bg = 'lightgray')   
        self.f_bot.pack(side='bottom',fill='x',pady=(1,0))  
        self.bot_label = Label(self.f_bot,text = 'bot label')
        self.bot_label.pack(anchor='center')
        
        # 미드 프레임
        self.f_mid = Frame(self.w_main, width=1, height=1, relief="solid")   
        self.f_mid.pack(expand=True, fill='both')
        ## 왼쪽 프레임
        self.f_left = Frame(self.f_mid, width=150, height=1, relief="solid", bg = 'lightblue')   
        self.f_left.pack(side='left',fill='y',padx=(0,1))
        ## 오른쪽 프레임
        self.f_right = Frame(self.f_mid, relief="solid", bg = 'white')   
        self.f_right.pack(expand=True, fill='both', padx=(0,1))
        self.f_right.drop_target_register(DND_FILES)        # 드레그앤 드롭
        self.f_right.dnd_bind('<<Drop>>', self.file_list)   # 드롭될 경우 file_list 콜백
        ### 리스트 테이블
        self.is_active_gridview = False
        self.is_active_tableview = False
        self.treeview=ttk.Treeview(self.f_right, columns=["PID","CID",'SUFFIX',"PATH"], displaycolumns=["PID","CID",'SUFFIX',"PATH"])
        self.treeview.bind("<Double-1>", self.on_tree_double_clicked)
        self.treeview.bind('<Delete>', self.delete_selected_item_in_table)
        self.treeview.pack(expand=True, fill='both')
        ### 스크롤바
        self.scrbar = Scrollbar(self.treeview,orient='vertical')
        self.scrbar.config(command=self.treeview.yview)                # 왼쪽 리스트박스에 부착
        self.scrbar.pack(side='right',fill='y',padx=1,pady=1)          # 왼쪽 스크롤 활성화
        self.treeview.config(yscrollcommand=self.scrbar.set)           # 리스트박스-스크롤 연결

        # 데이터베이스
        ## 데이터 리스트 딕셔너리
        self.data_dict = {'PID': [],
                'CID': [],
                'Suffix': [],
                'Path': [],
                'img_path':[]}
        self.data_df = pd.DataFrame(self.data_dict)
        ## 각 데이터 리스트
        self.file_path_list = self.data_dict['PID']        # 파일 경로 (Unique)
        self.file_PID_list = self.data_dict['CID']         # Product ID
        self.file_CID_list =self.data_dict['Path']         # Content ID
        self.file_suffix_list = self.data_dict['Suffix']   # 접미사
        self.img_path_list = self.data_dict['img_path']    # 파일 이미지 경로
        self.file_actor_name_list = []                     # 파일 배우 리스트

        # 테이블뷰 설정
        self.treeview.column("#0", width=30, anchor="center",stretch=False, minwidth=30)
        self.treeview.heading("#0", text='IDX')
        self.treeview.column("#1", width=80, anchor="center",stretch=False, minwidth=80)
        self.treeview.heading("PID", text="Product ID", anchor="center")
        self.treeview.column("#2", width=80, anchor="center",stretch=False, minwidth=80)
        self.treeview.heading("CID", text="Content ID", anchor="center")
        self.treeview.column("#3", width=50, anchor="center",stretch=False, minwidth=50)
        self.treeview.heading("SUFFIX", text="SUFFIX", anchor="center")
        self.treeview.column("#4", width=70, minwidth=70)
        self.treeview.heading("PATH", text="File Path")
        self.w_main.update_idletasks()
        self.is_active_gridview= False
        self.is_active_tableview= False    

        # self.clear_data_csv()    
        self.data_load_from_csv_path(r'./metadata.csv')
        self.show_table_view()
    
        self.w_main.mainloop() 
        # 초기화


    # 드래그앤드롭시 실행
    def file_list(self,event):
        # 드래그 엔 드롭으로 얻은 (파일 및 폴더의 경로 리스트)를 저장.
        tmp_file_path_list = self.f_right.tk.splitlist(event.data)
        
        # 데이터 전처리
        # 드롭된 비디오 파일 경로 리스트 저장
        video_file_path_list = []
        ## 데이터 전처리 진행바 설정
        self.open_progress_window()
        self.prog_window.update_idletasks()
        self.prog_var.set(0)
        prog_var_max = len(tmp_file_path_list)
        ## 비디오 파일만 필터링
        for path in tmp_file_path_list:
            # 파일일경우
            if os.path.isfile(path): 
                if get_type_of_file_from_full_path(path) != 'video':
                    continue     
                video_file_path_list.append(path)
            # 폴더일경우
            elif os.path.isdir(path):
                prog_var_max = len(os.listdir(path))
                self.prog_var.set(0)
                self.prog_bar.config(maximum=prog_var_max)    
                for file_name_in_dir in os.listdir(path):
                    prog_var = self.prog_var.get()
                    self.prog_var.set(prog_var+1)
                    if prog_var%10 ==0:
                        self.prog_bar.update_idletasks()                 
                    new_file_path = path+'/'+file_name_in_dir #새로운 파일 주소 = 폴더주소/파일이름
                    #폴더 내부의 파일만 로드한다.
                    if not os.path.isfile(new_file_path):                 
                        continue
                    # 비디오 파일만
                    if get_type_of_file_from_full_path(new_file_path) != 'video':
                        continue   
                    video_file_path_list.append(new_file_path)

        # 데이터 처리 진행바 설정
        prog_var_max = len(video_file_path_list)
        self.prog_bar.config(maximum=prog_var_max)    
        self.prog_var.set(0)

        # 드롭된 비디오 파일 경로 리스트를 이용하여 전체 파일 경로 리스트를 저장.
        if video_file_path_list == []:
            return
        self.prog_window.title('Inserting Data ...')

        for path in video_file_path_list:
            # 중복된 파일은 리스트에 추가하지 않는다. 
            if path in self.file_path_list:
                prog_var = self.prog_var.get()
                self.prog_var.set(prog_var+1)
                # print(path,'중복!')
                continue

            self.file_path_list.insert(0,path)   # 경로 리스트에 파일 경로 추가.
            dir_path, file_name = os.path.split(path)
            file_base, file_ext = os.path.splitext(file_name)

            # 최상위 폴더 경로일 경우 (eg. D://) /문자 하나를 지워준다.
            if dir_path[-1] =='/':
                dir_path = dir_path[:-1]

            # Regex를 써서 PID를 찾는다.
            patrn = re.compile('.*?(?P<prefix>[a-zA-Z]{2,9})[-](?P<number>\d{2,6}).*?(?P<suffix>[A-P])?$')
            m = patrn.search(file_base)
            if m != None: 
                prefix = m.group('prefix').upper()
                number = m.group('number')
                PID = prefix+'-'+number
                img_path = dir_path+'/'+PID+'.jpg'
                # CID = get_CID_from_PID(PID)
                CID = ''
                # 접미사가 없는 경우
                if m.group('suffix') == None:
                    suffix = ''
                # 접미사가 있는 경우
                else:
                    suffix = m.group('suffix')
                    # HOME-1234 4K 인 경우는 제외
                    # ASDF-134K ?
                    if suffix == 'K' and file_base[-2] == '4':
                        suffix = ''
            else:
                PID = ''
                CID = ''
                suffix = ''
                img_path = ''

            if os.path.exists(img_path):
                self.img_path_list.insert(0,img_path)
                # print(img_path)
            else:
                self.img_path_list.insert(0,'') 
            self.file_PID_list.insert(0,PID)
            self.file_CID_list.insert(0,CID)
            self.file_suffix_list.insert(0,suffix)

            # 표에 데이터 삽입
            tabledata = PID,CID,suffix,path,img_path
            self.treeview.insert('', 0, values=tabledata)
            # 진행바 업데이트
            prog_var = self.prog_var.get()
            self.prog_var.set(prog_var+1)
            if prog_var%10 ==0:
                self.prog_bar.update_idletasks() 
        
        if self.prog_var.get() == prog_var_max:
            self.prog_window.attributes('-topmost', False)
            self.prog_window.destroy() 

        # 메타데이터를 만들어서 파일에 저장.
        self.save_meta_to_csv()

        if self.is_active_tableview:
            self.show_table_view()
        elif self.is_active_gridview:
            self.show_grid_view()

    # 파일 - 종료
    def save_n_exit(self):
        self.save_meta_to_csv()
        self.w_main.quit()
        # 데이터 베이스 저장후 종료

    # 편집 - 메타데이터 모두 삭제
    def clear_data_csv(self):
        self.file_path_list.clear()
        self.file_PID_list.clear()
        self.file_CID_list.clear()
        self.file_suffix_list.clear()
        self.img_path_list.clear()
        self.data_dict.clear()
        self.file_path_list.clear()
        data = {'PID': [],
        'CID': [],
        'Suffix': [],
        'Path': [],
        'img_path': []}
        data_df = pd.DataFrame(data)
        data_df.to_csv(r'./metadata.csv',index = False)
        self.data_load_from_csv_path(r'./metadata.csv')
        # 데이터 초기화

    # 테이블뷰 - 항목 더블클릭
    def on_tree_double_clicked(self,event):
        item = self.treeview.selection()[0]
        print(self.treeview.item(item, 'values')[3])
        os.system(self.treeview.item(item, 'values')[3])
        # 해당 파일 실행

    # 테이블뷰 - delete 키
    def delete_selected_item_in_table(self,event):
        selected_items = self.treeview.selection()
        for item in selected_items:
            item_path = self.treeview.item(item)['values'][3]
            if item_path in self.file_path_list:
                index = self.file_path_list.index(item_path)
                self.file_path_list.pop(index)
                self.file_PID_list.pop(index)
                self.file_CID_list.pop(index)
                self.file_suffix_list.pop(index)
                self.img_path_list.pop(index)
                print('deleted!',len(self.file_path_list))
            self.treeview.delete(item)
        # 테이블뷰에서 선택한 파일정보 데이터 베이스에서 삭제

    def delete_selected_item_in_grid(self,event):
        if not self.is_active_gridview:
            return
        selected_items = self.selected_label_list
        for item in selected_items:
            item_path = item['text']
            # print(item_path)
            if item_path in self.file_path_list:
                index = self.file_path_list.index(item_path)
                print(index)
                self.file_path_list.pop(index)
                self.file_PID_list.pop(index)
                self.file_CID_list.pop(index)
                self.file_suffix_list.pop(index)
                self.img_path_list.pop(index)
                # self.btn_list[index].grid_forget()
        self.update_grid()
        # 테이블뷰에서 선택한 파일정보 데이터 베이스에서 삭제

    def show_table_view(self):
        if self.is_active_tableview:
            return
        if self.is_active_gridview:
            self.canvas_photo.pack_forget()
            self.scrbar_photo.pack_forget()
        
        self.is_active_gridview= False
        self.is_active_tableview= True    

        self.treeview.pack(expand=True, fill='both')
        # 데이터 처리 진행바 설정
        self.open_progress_window()
        # prog_var_max = len(self.file_path_list)
        prog_var_max = min(50, len(self.file_path_list))
        self.prog_bar.config(maximum=prog_var_max)    
        self.prog_var.set(0)

        # 파일 경로 리스트를 이용하여 전체 파일 경로 리스트를 저장.
        if self.file_path_list == []:
            return

        self.table_list = self.file_path_list[0:prog_var_max]
        self.clear_table()
        self.prog_window.title('Inserting Data ...')
        for index, path in enumerate(self.table_list):
            if str(path) == 'nan':
                path = '-'
            if str(self.file_PID_list[index]) == 'nan':
                PID = '-'
            else:
                PID = self.file_PID_list[index]
            if str(self.file_CID_list[index]) == 'nan':
                CID = '-'
            else:
                CID = self.file_CID_list[index]
                # print(type(CID))
            if str(self.file_suffix_list[index]) == 'nan':
                suffix = '-'
            else:
                suffix = self.file_suffix_list[index]
            if str(self.img_path_list[index]) == 'nan':
                img_path = '-'
            else:
                img_path = self.img_path_list[index]

            # 표에 데이터 삽입
            tabledata = PID,CID,suffix,path,img_path
            self.treeview.insert('', 'end', values=tabledata)
            # 진행바 업데이트
            prog_var = self.prog_var.get()
            self.prog_var.set(prog_var+1)
            if index%10 == 0:
                self.prog_bar.update_idletasks()  

        if self.prog_var.get() == prog_var_max:
            self.prog_window.attributes('-topmost', False)
            self.prog_window.destroy() 
        # 테이블뷰 모드로 전환

    def show_grid_view(self):
        if self.is_active_tableview:    # 테이블뷰에서 실행되는 경우
            self.treeview.pack_forget() # 테이블뷰 종료
        if self.is_active_gridview:     # 이미 그리드뷰인 경우
            return
        if not self.img_path_list:      
            return
        prog_var_max = min(50, len(self.file_path_list))
        if prog_var_max == 0:
            return
        self.treeview.pack_forget() # 테이블뷰 종료

        # 데이터 처리 진행바 설정
        self.open_progress_window()
        self.prog_bar.config(maximum=prog_var_max)    
        self.prog_var.set(0)

        self.is_active_tableview=False    
        self.is_active_gridview=True
        # self.f_photo = Frame(self.f_right, width=1, height=1)
        # self.f_photo.pack(expand=True, fill='both')
        # self.img_frame_list = []
        self.selected_label_list = []
        self.img_list = []
        # self.labl_list = []
        # 이미지 전처리
        for img_path in self.img_path_list[:prog_var_max]:
            # print(type(img_path),img_path)
            if img_path == '' or str(img_path) == 'nan':
                image = Ig.open('DarBros64.png')
            else:
                image = Ig.open(img_path)
            # 이미지 사이즈 조절
            # xsize,ysize = 800,538
            # xsize,ysize = 400,269
            xsize,ysize = 200,134
            image = image.resize((xsize,ysize))
            photo = ImageTk.PhotoImage(image)
            self.img_list.append(photo)
        # 포토 프레임
    
        # 포토 캔버스
        self.canvas_photo = Canvas(self.f_right,bg='blue',scrollregion=(0,0,10000,10000))
        self.canvas_photo.bind_all('<KeyPress-Delete>', self.delete_selected_item_in_grid)
        # self.canvas_photo.config(scrollregion = self.canvas_photo.bbox("all"))
        self.scrbar_photo = Scrollbar(self.f_right,orient='vertical')      # 스크롤

        self.canvas_photo.config(yscrollcommand=self.scrbar_photo.set)           # 리스트박스-스크롤 연결  
        self.scrbar_photo.config(command=self.canvas_photo.yview)                # 왼쪽 리스트박스에 부착

        self.canvas_photo.pack(side='left',expand=True,fill='both')
        self.scrbar_photo.pack(side='right',fill='y',padx=1,pady=1)                     # 왼쪽 스크롤 활성화

        # for img in self.img_list:
        #     label = Label(self.canvas_photo,image=img, bd=1)
        #     self.labl_list.append(label)

        # 이미지 자리잡기
        # count = 0
        # padx,pady  = 2,2
        # marginx, marginy = 5,5
        # for labl in self.labl_list:
        #     # print(xsize*(count%3),ysize*(count//3),xsize,ysize)
        #     labl.place(x=marginx+(padx+xsize)*(count%5),y=marginy+(pady+ysize)*(count//5),width=xsize,height=ysize)
        #     count+=1

        #     prog_var = self.prog_var.get()
        #     self.prog_var.set(prog_var+1)
        #     if count%10 == 0:
        #         self.prog_bar.update_idletasks()
        # padx,pady  = 2,2
        # marginx, marginy = 5,5
        # self.frame_table = [[Frame(self.f_right,width=xsize,height=ysize,bg='yellow')for row in range(row_size-1)] for column in range(column_size-1)]
        # for r in range(row_size-1):
        #     for c in range(column_size-1):
        #         (self.frame_table[r][c]).grid(row=r, column=c)
        
        row_size, column_size = 6, 5
        # self.frame_table = [[Frame(self.canvas_photo,bg='yellow',bd=1,width=300,height=200)for row in range(row_size)] for column in range(column_size)]
        row_size = math.ceil(prog_var_max/column_size)
        print(row_size, column_size)
        # self.btn_matrix = [[ (row,column) for column in range(column_size)] for row in range(row_size)]
        self.btn_list = []
        count = 0
        for r in range(row_size):
            for c in range(column_size):
                # frame = self.frame_table[r][c]
                # frame.grid(row=r, column=c,sticky='news')
                count += 1
                img_index = column_size*r+c%column_size
                img_path = self.file_path_list[img_index]
                btn = Label(self.canvas_photo,text=img_path,width=xsize,height=ysize,bd=5, relief=RIDGE,image=self.img_list[img_index])
                # print(self.img_list[column_size*r+c%column_size])
                # btn.config(command=self.on_label_clicked)
                btn.bind("<Button-1>",self.on_label_clicked)
                btn.bind("<Shift-1>",self.on_label_shift_clicked)
                btn.bind("<Double-1>",self.on_label_double_clicked)
                # self.btn_matrix[r][c] = btn
                self.btn_list.append(btn)
                btn.grid(row=r,column=c)
                prog_var = self.prog_var.get()
                self.prog_var.set(prog_var+1)
                self.prog_bar.update_idletasks()
                if count == prog_var_max:
                    break
                # btn.grid(row=r, column=c)
                # btn_list.append(btn)      
                # Button(self.canvas_photo, text='R%s/C%s'%(r,c),borderwidth=1,width=50,height=10 ).grid(row=r,column=c)

        if self.prog_var.get() >= prog_var_max:
            self.prog_window.attributes('-topmost', False)
            self.prog_window.destroy() 
        # 그리드뷰 모드로 전환

    def on_label_clicked(self,event):
        # 이미 선택한 레이블이 존재할 경우
        if self.selected_label_list != []:
            # 선택되어있던 레이블을 초기화
            for label in self.selected_label_list:
                label.config(bg = 'lightgray')
            self.selected_label_list = []
        # 지금 레이블만 선택
        widget = event.widget
        self.selected_label_list.append(widget)
        self.last_clicked_label = widget
        widget.config(bg='red')
        # 레이블 Click 시 선택 활성화

    def on_label_shift_clicked(self,event):
        # 이미 선택한 레이블이 존재하지 않을 경우
        if self.selected_label_list == []:
            widget = event.widget
            self.selected_label_list.append(widget)
            self.last_clicked_label = widget
            widget.config(bg='red')
            return
        
        clicked_widget = event.widget
        clicked_btn_index = self.btn_list.index(clicked_widget)

        last_clicked_btn_index = self.btn_list.index(self.last_clicked_label)
        if last_clicked_btn_index < clicked_btn_index:
            smaller_index,larger_index = last_clicked_btn_index,clicked_btn_index
        else:
            smaller_index,larger_index = clicked_btn_index,last_clicked_btn_index
            
        for btn in self.btn_list[smaller_index:larger_index+1]:
            if btn in self.selected_label_list:
                continue
            self.selected_label_list.append(btn)
            btn.config(bg='red')
        # 레이블 Shift+Click 시 실행 (ClickLabel)

    def on_label_double_clicked(self,event):
        item = event.widget
        print(item['text'])
        os.system(item['text'])
        # os.system(self.treeview.item(item, 'values')[3])

    def save_meta_to_csv(self):
        self.data_dict = {'PID': self.file_PID_list,
                'CID': self.file_CID_list,
                'Suffix': self.file_suffix_list,
                'Path': self.file_path_list,
                'img_path':self.img_path_list}
        self.data_df = pd.DataFrame(self.data_dict)
        self.data_df.to_csv(r'./metadata.csv',index = False)
        # 데이터 베이스를 csv파일에 저장.

    def open_progress_window(self):
        self.prog_window = Toplevel(self.w_main,bg='gray')
        self.prog_window.lift(self.w_main)
        self.prog_window.attributes('-topmost', True)
        self.prog_window.overrideredirect(True)
    
        self.prog_window.title('Preprocessing Data ...')
        # sets the geometry of toplevel
        wm_width, wm_height = self.w_main.winfo_x(),self.w_main.winfo_y()
        prog_bar_position = (wm_width+300 , wm_height+200)
        self.prog_window.geometry(f"500x50+{prog_bar_position[0]}+{prog_bar_position[1]}")

        self.prog_label = Label(self.prog_window,text='Progress: ', bg ='gray',padx=30)
        self.prog_label.pack(side='left')
        self.prog_var = DoubleVar()
        self.prog_bar = ttk.Progressbar(self.prog_window, maximum=100, length = 400, variable= self.prog_var)
        self.prog_bar.pack(expand=True,padx=(0,30))
        # 진행바 오픈

    def data_load_from_csv_path(self,path):
        # 데이터 로드
        data_csv = pd.read_csv(path)
        print(data_csv.shape[0])
        if data_csv.shape[0] == 0:
            for i in self.treeview.get_children():
                self.treeview.delete(i)
            # self.w_main.update_idletasks()
            return
        self.img_path_list = data_csv['img_path'].tolist()
        self.file_path_list = data_csv['Path'].tolist()
        self.file_PID_list = data_csv['PID'].tolist()
        self.file_CID_list = data_csv['CID'].tolist()
        self.file_suffix_list = data_csv['Suffix'].tolist()
        # 데이터를 csv파일에서 읽어와서 데이터베이스 초기화
    
    def find_meta_data(self):
        self.open_progress_window()
        prog_var_max = len(self.treeview.selection())
        self.prog_bar.config(maximum=prog_var_max)    
        self.prog_var.set(0)
        for item in self.treeview.selection():
            PID, CID, suffix, file_path, img_path = self.treeview.item(item)['values']
            prog_var = self.prog_var.get()
            self.prog_var.set(prog_var+1)

            if not file_path in self.file_path_list:
                continue
            index = self.file_path_list.index(file_path)

            if PID == '' or str(PID)=='nan':
                continue

            if CID == ''or CID=='-' or str(CID)=='nan':
                try:
                    url = f'https://jav.land/en/id_search.php?keys={PID}'
                    req = requests.get(url)
                    soup = BeautifulSoup(req.content,"html.parser")
                    source = soup.find("td", attrs = {"width":"80%"})
                    patrn = re.compile('^<td width="80%">(?P<CID>.{3,})<\/td>$')
                    m = patrn.search(str(source))
                    if m==None:
                        print('CID not found')
                        CID = ''
                    else:
                        CID = m.group('CID')
                        self.file_CID_list[index] = CID 
                        
                    source = soup.find_all("span", attrs = {"class":"star"})
                    actor_name_list = []

                    if source == []:
                        print('Actor not found: ',f'{CID}')
                        actor_name_list = ['']
                    else:
                        patrn = re.compile('^(<span class="star">.*?)>(?P<actor_name>.{3,})(<\/a><\/span>)$')
                        print(source)
                        for actor_parse in source:
                            m = patrn.search(str(actor_parse))
                            print(actor_parse)
                            if m==None:
                                print('Actor not found: ',f'{CID}')
                                actor_name_list = ['']
                                break
                            else:
                                actor_name = m.group('actor_name')
                                print(actor_name)
                                actor_name_list.append(actor_name)

                    self.file_actor_name_list.append(actor_name_list)
                    print(self.file_actor_name_list)
                except:
                    print('CID not found')
                    # continue

            if img_path == '' or img_path=='-' or str(img_path)=='nan':
                try:
                    url = f'https://pics.dmm.co.jp/digital/video/{CID}/{CID}pl.jpg'
                    dir_path, _ = os.path.split(file_path)
                    img_path = dir_path + '/' + PID +'.jpg'
                    self.img_path_list[index] = img_path
                    with open(img_path, "wb") as file:
                        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
                        response = requests.get(url, headers = headers)
                        file.write(response.content)
                except:
                    print('Cover image not found')
            
            tabledata = PID,CID,suffix,file_path,img_path
            self.treeview.item(item, values=tabledata)
            self.treeview.update()
            
            if self.prog_var.get() == prog_var_max:
                self.prog_window.attributes('-topmost', False)
                self.prog_window.destroy() 
        # 선택된 항목 메타데이터 검색
                
    def update_table(self):
        if not self.is_active_tableview:
            return
        
        for i in self.treeview.get_children():
                self.treeview.delete(i)

        if self.file_path_list == []:
            return

        # 데이터 처리 진행바 설정
        self.open_progress_window()
        # prog_var_max = len(self.file_path_list)
        prog_var_max = min(50, len(self.file_path_list))
        self.prog_bar.config(maximum=prog_var_max)    
        self.prog_var.set(0)

        # 파일 경로 리스트를 이용하여 전체 파일 경로 리스트를 저장.
        for index, path in zip(range(prog_var_max), self.file_path_list[0:prog_var_max]):
            if str(path) == 'nan':
                path = '-'
            if str(self.file_PID_list[index]) == 'nan':
                PID = '-'
            else:
                PID = self.file_PID_list[index]
            if str(self.file_CID_list[index]) == 'nan':
                CID = '-'
            else:
                CID = self.file_CID_list[index]
                # print(type(CID))
            if str(self.file_suffix_list[index]) == 'nan':
                suffix = '-'
            else:
                suffix = self.file_suffix_list[index]
            if str(self.img_path_list[index]) == 'nan':
                img_path = '-'
            else:
                img_path = self.img_path_list[index]

            # 표에 데이터 삽입
            tabledata = PID,CID,suffix,path,img_path
            self.treeview.insert('', 'end', values=tabledata)
            # 진행바 업데이트
            prog_var = self.prog_var.get()
            self.prog_var.set(prog_var+1)
            if index%10 == 0:
                self.prog_bar.update_idletasks()  

        if self.prog_var.get() == prog_var_max:
            self.prog_window.attributes('-topmost', False)
            self.prog_window.destroy() 

    def update_grid(self):
        if not self.is_active_gridview:
            return
        if not self.img_path_list:      
            return
        prog_var_max = min(50, len(self.file_path_list))
        if prog_var_max == 0:
            return

        # 데이터 처리 진행바 설정
        self.open_progress_window()
        self.prog_bar.config(maximum=prog_var_max)    
        self.prog_var.set(0)

        self.is_active_tableview=False    
        self.is_active_gridview=True

        self.selected_label_list = []
        self.img_list = []
        self.clear_img_in_grid()
        
        # 이미지 전처리
        for img_path in self.img_path_list[:prog_var_max]:
            # print(type(img_path),img_path)
            if img_path == '' or str(img_path) == 'nan':
                image = Ig.open('DarBros64.png')
            else:
                image = Ig.open(img_path)
            # 이미지 사이즈 조절
            xsize,ysize = 800,538
            # xsize,ysize = 320,212
            # xsize,ysize = 160,106
            image = image.resize((xsize,ysize))
            photo = ImageTk.PhotoImage(image)
            self.img_list.append(photo)

        column_size = 5
        row_size = math.ceil(prog_var_max/column_size)
        self.btn_list = []

        count = 0
        for r in range(row_size):
            for c in range(column_size):
                count += 1
                img_index = column_size*r+c%column_size
                img_path = self.file_path_list[img_index]
                btn = Label(self.canvas_photo,text=img_path,width=xsize,height=ysize,bd=5, relief=RIDGE,image=self.img_list[img_index])
                btn.bind("<Button-1>",self.on_label_clicked)
                btn.bind("<Shift-1>",self.on_label_shift_clicked)
                self.btn_list.append(btn)
                btn.grid(row=r,column=c)
                prog_var = self.prog_var.get()
                self.prog_var.set(prog_var+1)
                self.prog_bar.update_idletasks()
                if count == prog_var_max:
                    break

        if self.prog_var.get() >= prog_var_max:
            self.prog_window.attributes('-topmost', False)
            self.prog_window.destroy() 
        # 그리드뷰 업데이트
        
    def clear_table(self):
        for item in self.table_list:
            self.treeview.delete(*self.treeview.get_children())

    def clear_img_in_grid(self):
        for item in self.btn_list:
            item.grid_forget()






action()


# pyinstaller --onefile --noconsole --add-binary "C:\Users\darau\AppData\Local\Programs\Python\Python39\tcl\tkdnd2.8;tkdnd2.8" DarBros_manager.py












    