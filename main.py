import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage, QPalette,  QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
import cv2
from PyQt5 import QtCore
import sys
from PyQt5 import QtGui
from face import face_function
import numpy as np
from datetime import datetime 
import threading
import random


class MainWindow(QMainWindow):
        def __init__(self):
                super().__init__()
                self.setGeometry(100, 100, 800, 600)
                self.page_main = loadUi("./ui/mainui.ui")
                self.page_login = loadUi("./ui/login.ui")
                self.page_recong = loadUi("./ui/recong.ui")
                self.page_logup = loadUi("./ui/logup.ui")

                # 设置页面
                self.stacked_widget = QStackedWidget(self)
                self.setCentralWidget(self.stacked_widget)

                # 加载三个不同界面
                self.stacked_widget.addWidget(self.page_main)
                self.stacked_widget.addWidget(self.page_recong)
                self.stacked_widget.addWidget(self.page_login)
                self.stacked_widget.addWidget(self.page_logup)

                # 图片自适应
                self.page_login.label_image.setScaledContents(True)
                self.page_recong.label_down.setScaledContents(True)
                self.page_recong.label_image.setScaledContents(True)
                self.page_logup.label_image.setScaledContents(True)

                # 按钮事件绑定
                 # 主界面
                self.page_main.button_login.clicked.connect(self.button_login)
                self.page_main.button_logup.clicked.connect(self.button_logup)
                self.page_main.button_reconge.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

                # 登陆界面
                self.page_login.button_login.clicked.connect(self.button_login_login)
                self.page_login.button_back.clicked.connect(self.button_back)
                self.page_login.button_show.clicked.connect(self.change_show)

                # 注册界面
                self.page_logup.button_show.clicked.connect(self.change_show)
                self.page_logup.button_submit.clicked.connect(self.button_submit)
                self.page_logup.button_back.clicked.connect(self.button_back)

                # 识别界面
                self.page_recong.button_camera.clicked.connect(self.button_open_camera)
                self.page_recong.button_file.clicked.connect(self.button_file)
                self.page_recong.button_recognition.clicked.connect(self.button_recognition)
                self.page_recong.button_back.clicked.connect(self.button_back)

                self.ff = face_function()
                self.camera_image = None
                self.camera_image_Qimage = None
                self.down_img = None
                self.message = ""
                

                self.show_flag = 0      # 为0不现实特征，为1显示特征
                self.pass_flag = 0      # 为 0 不通过活体检测，为 1 以及通过活体检测
                self.time_flag = 0      # 超时辨识，大于10时，提示进入活体检测程序
                self.pass_ = 0          # 对比通过标志，大于2时通过
                self.user = 0           # 当前使用人标识，0 为检测失败 1为检测成功
                self.temp_action = []   # 临时储存用户动作  
                self.action = ["眨眼", "张嘴"]  # 活体检测时应该完成的动作

                self.user_old_endcoding = None  # 用户人类编码备份
                self.user_endcoding = None      # 用户人脸编码检测失败


        # 登陆界面默认事件
        def button_login(self):
                self.open_camera()
                self.stacked_widget.setCurrentIndex(2)
                self.timer.timeout.connect(self.show_original_face)
                self.user = 0

        # 登录定时器事件
        def show_original_face(self):
                self.take_picture()
                if not self.show_flag:
                        self.page_login.label_image.setPixmap(QPixmap.fromImage(self.camera_image_Qimage))
                else:
                       img = self.get_down_img()
                       self.page_login.label_image.setPixmap(QPixmap.fromImage(img))
                self.page_login.label_message.setText(self.message)

        # 登陆界面登录按钮事件
        def button_login_login(self):
                self.show_flag = 0
                self.page_login.label_message.setText("请按提示操作")
                if not self.pass_flag:
                        self.timer2 = QtCore.QTimer()
                        self.timer2.start(3000)
                        self.timer2.timeout.connect(self.timer_2)
                        self.pass_flag = 0
                        self.user = 1
                        thread_get_action = threading.Thread(target=self.thread_work)
                        thread_get_action.setDaemon(True)
                        thread_get_action.start()
                        self.timer_2()
                else:
                        self.get_name()

        # 活体检测定时器
        def timer_2(self):
                self.show_flag = 0
                action = random.choice(self.action)

                self.page_login.label_action.setText("请"+ action)
                print("pass_ = ", self.pass_)
                if action in self.temp_action:
                        self.pass_ += 1
                self.time_flag += 1
                self.temp_action = []
                if self.pass_ >= 2:
                       self.pass_flag = 1
                       self.timer2.stop()
                       self.pass_ = 0
                       self.time_flag = 0
                       self.page_login.label_action.setText("Pass,请重新点击登录")
                if self.time_flag >= 10:
                        self.timer2.stop()
                        self.pass_ = 0
                        self.time_flag = 0
                        self.page_login.label_action.setText("请重新登录")

        def get_name(self):
                self.ff.detect_face()
                if self.ff.name == -1:
                        self.page_login.label_action.setText("请返回注册")
                elif type(self.ff.name) == str:
                        self.page_login.label_action.setText("欢迎登录" + self.ff.name)

        def thread_work(self):
                
                while not self.pass_flag:
                        self.get_action()

        # 注册界面默认事件
        def button_logup(self):
                # print("进入 button_logup 函数 ") 
                self.stacked_widget.setCurrentIndex(3)
                self.open_camera()
                self.user = 0
                self.timer.timeout.connect(self.button_logup_timer)

        # 注册定时器事件
        def button_logup_timer(self):
                # print("进入 button_logup_timer 函数 ")                 
                self.take_picture()
                if not self.show_flag:
                        self.page_logup.label_image.setPixmap(QPixmap.fromImage(self.camera_image_Qimage))
                else:
                       img = self.get_down_img()
                       self.page_logup.label_image.setPixmap(QPixmap.fromImage(img))
                self.page_logup.label_message.setText(self.message)         

        # 注册界面提交按钮事件
        def button_submit(self):
                self.show_flag = 0
                self.page_logup.label_message.setText("请按提示操作")
                if not self.pass_flag:
                        self.timer3 = QtCore.QTimer()
                        self.timer3.start(3000)
                        self.timer3.timeout.connect(self.timer_3)
                        self.pass_flag = 0
                        self.user = 1
                        thread_get_action = threading.Thread(target=self.thread_work)
                        thread_get_action.start()
                        self.timer_3()
                else:
                       self.get_name_logup()        

        # 注册界面活体检测定时器
        def timer_3(self):
                self.show_flag = 0
                action = random.choice(self.action)

                self.page_logup.label_action.setText("请"+ action)
                
                if action in self.temp_action:
                        self.pass_ += 1

                self.time_flag += 1
                self.temp_action = []
                if self.pass_ >= 2:
                       self.pass_flag = 1
                       self.pass_ = 0
                       self.timer3.stop()
                       self.time_flag = 0
                       self.page_logup.label_action.setText("Pass,请重新点击注册")
                if self.time_flag >= 10:
                        self.timer3.stop()
                        self.pass_ = 0
                        self.time_flag = 0
                        self.page_logup.label_action.setText("请重新注册")

        def get_name_logup(self):
                self.ff.detect_face()
                print(self.ff.name)
                if self.ff.name == -1:
                        name = self.page_logup.lineEdit_name.text()
                        if len(name) < 1:
                                self.page_logup.label_action.setText("请输入用户名")
                                return
                        self.ff.name = name
                        self.ff.face_add()
                        self.ff.update_data()
                        self.page_logup.label_action.setText("注册成功")
                        
                else:
                        self.page_logup.label_action.setText("请返回登录")

        def button_back(self):
                # print("进入 button_back 函数 ") 
                self.stacked_widget.setCurrentIndex(0)
                self.stop_camera()
                self.user= 0
                self.pass_flag = 0
                self.temp_action = []
                self.message = ""
                self.show_flag = 0

        def get_action(self):
                self.ff.load_image(self.camera_image)
                if self.ff.face_check() == -1:
                        return
                a = self.ff.get_actions()
                print('a = ', a)
                if len(a) > 0:
                        self.temp_action.extend(a)
                if not self.check_one_people():
                        self.pass_flag = 0


        def button_open_camera(self):
                # print("进入 button_open_camera 函数 ") 
                self.open_camera()
                self.timer.timeout.connect(self.show_picture)


        def show_picture(self):
                self.take_picture()
                self.page_recong.label_image.setPixmap(QPixmap.fromImage(self.camera_image_Qimage))

        # 识别界面从文件读取按钮事件
        def button_file(self):
                # print("进入 button_file 函数 ") 
                self.stop_camera()
                self.timer.stop()
                options = (QFileDialog.Options()| QFileDialog.ReadOnly)
                self.fileName, _ = QFileDialog.getOpenFileName(self,"选择图片", "","Images (*.png *.xpm *.jpg *.bmp *.gif);;All Files (*)", options=options)
                img = self.deal_with_picture(cv2.imread(self.fileName))
                self.page_recong.label_image.setPixmap(QPixmap.fromImage(self.camera_image_Qimage))

        # 识别界面识别按钮事件
        def button_recognition(self):
                # print("进入 button_recognition 函数 ")
                self.ff.load_image(self.camera_image)
                
                if self.ff.face_check() == -1:
                       print("无人脸")
                       self.page_recong.label_down.setText("未检测到人脸")
                       return
                
                self.page_recong.label_down.setPixmap(QPixmap.fromImage(self.get_down_img()))

        # 检测是否中间换人

        def check_one_people(self):
                self.ff.get_face_locations()
                self.ff.get_face_encodings()
                self.user_endcoding = self.ff.face_encodings    
                if  self.user_old_endcoding:
                        distance = np.linalg.norm(np.array(self.user_old_endcoding) - np.array(self.user_endcoding))
                        if distance >= 0.5:
                                print("distance", distance)
                                self.message = "识别错误"
                                print("not one people")
                                self.user_old_endcoding = self.user_endcoding
                                self.save_picture()
                                return 0     
                self.message = "识别成功"
                self.user_old_endcoding = self.user_endcoding
                return 1
        
        # 存储照片
        def save_picture(self):
                now = datetime.now()
                timestamp = now.strftime('%Y%m%d_%H%M%S')
                filename = f'./temp_image/{timestamp}.jpg'
                cv2.imwrite(filename, self.camera_image)
        
        # 决定是否展示特征图
        def change_show(self):
                self.show_flag = ~self.show_flag

        # 获取一张照片
        def take_picture(self):
                flag,img = self.cap.read()
                if not flag:
                        print("摄像头拍照失败")
                        return
                self.deal_with_picture(img)
                
        def deal_with_picture(self, img):
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # 计算图片的宽高比
                height, width = img.shape[:2]
                aspect_ratio = width / height
                # 设置新的图片宽度
                new_width = 360
                # 根据新的宽度计算新的高度
                new_height = int(new_width / aspect_ratio)
                # 重新调整图片的大小
                img = cv2.resize(img, (new_width, new_height))
                self.camera_image = img
                # 将图片转换为 QImage 格式
                img = QtGui.QImage(img.data, new_width, new_height, QtGui.QImage.Format_RGB888)
                self.camera_image_Qimage =  img
        
        def get_down_img(self):
                self.ff.load_image(self.camera_image)
                message = self.ff.face_check()
                if message == -1:
                        self.message = "检测失败"
                        return self.camera_image_Qimage
                self.message = "检测成功"
                img = self.ff.down_image
                height, width, channel = img.shape
                bytesPerLine = 3 * width
                return QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        def open_camera(self):
                self.cap = cv2.VideoCapture(0)
                self.timer = QtCore.QTimer()
                self.timer.start(10)

        def stop_camera(self):
                # print("进入 stop_camera 函数 ") 
                self.timer.stop()
                self.cap.release()


if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(69,69,69))
        window.setPalette(palette)
        window.show()
        sys.exit(app.exec_())
