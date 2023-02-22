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


class MainWindow(QMainWindow):
        def __init__(self):
                super().__init__()
                self.setGeometry(100, 100, 800, 600)
                self.page_main = loadUi("./ui/mainui.ui")
                self.page_login = loadUi("./ui/login.ui")
                self.page_recong = loadUi("./ui/recong.ui")
                self.page_logup = loadUi("./ui/logup.ui")
                
                self.ff = face_function()

                self.user = 0   # 当前使用人标识，0 为检测失败 1为检测成功
                self.cap_flag = 0   # 摄像头标识， 未打开摄像头为0,已经打开摄像头为1
                self.timer_flag = 0 # 计时器标识，未打开为0,已经打开为1
                self.show_flag = 0      # 为0不现实特征，为1显示特征
                self.pass_flag = 0      # 为 0 不通过活体检测，为 1 以及通过活体检测
                self.time_flag = 1      # 超时辨识，大于self.dead_time时，提示重新进入活体检测程序
                self.original_image = None      # 摄像头拍的或者从文件获取的且经过处理的非Qimage类型的图片
                self.message = None     # 应该展示在label__message中的字符串
                self.action = ["眨眼", "张嘴"]  # 活体检测时应该完成的动作
                self.temp_action = []         # 临时储存用户动作
                self.user_endcoding = None      # 用户人脸编码
                self.user_old_endcoding = 0     # 用户人类编码备份

                self.dead_time = 8              # 最多活体检测时间为 dead_time * 5秒
                self.pass_ = 2                  # self.pass_flag 大于此数值时，判定为通过，即应该完成的动作总数


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
        
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——

        # 登陆界面默认事件
        def button_login(self):
                # print("进入 button_login 函数 ") 
                self.stacked_widget.setCurrentIndex(2)
                self.open_camera()
                self.user = 0
                self.timer.timeout.connect(self.button_login_timer)
                self.page_login.label_message.setText(self.message)
                self.page_login.label_action.setText(self.message)
        


        # 登录定时器事件
        def button_login_timer(self):
                # print("button_login_timer 函数 ", self.user) 
                img_1 = self.take_picture()
                img_2 = self.get_down_img()
                if img_2 == -1:
                        self.message = "检测失败"
                        self.user = 0
                else:
                        self.user = 1
                        self.message = "检测成功"

                if self.show_flag:
                        self.page_login.label_image.setPixmap(QPixmap.fromImage(img_2))
                else:
                       self.page_login.label_image.setPixmap(QPixmap.fromImage(img_1))
                if self.user == 1:
                        self.get_action()
                self.page_login.label_message.setText(self.message) 
        
        # 登陆界面登录按钮事件  # 显示要求，判断是否为同一个人，获取名字。
        def button_login_login(self):
                if self.pass_flag == 0:
                        self.timer2 = QtCore.QTimer()
                        self.timer2.start(3000)
                        self.timer2.timeout.connect(self.timer_2)
                        self.pass_flag = 0
                        self.timer_2()
                        # action = self.action[self.pass_flag]
                        # self.pass_flag += 1
                        # self.page_login.label_action.setText("请"+action)
                else:
                       self.get_name()

        # 活体检测定时器             
        def timer_2(self):
                pass
                self.show_flag = 0
                index = self.pass_flag % len(self.action)
                action = self.action[index]
                
                self.page_login.label_action.setText("请"+ action)
                if self.check_one_people():
                        if action in self.temp_action:
                                self.pass_flag += 1

                self.time_flag += 1
                self.temp_action = []
                print("self.time_flag = ", self.time_flag)
                print("self.pass_flag = ", self.pass_flag)
                if self.pass_flag >= self.pass_:#__________________________________________________________________________________________________________
                       self.pass_flag = 1
                       self.timer2.stop()
                       self.page_login.label_action.setText("Pass,请重新点击登录")
                if self.time_flag >= self.dead_time:
                        self.timer2.stop()
                        self.pass_flag = 0
                        self.time_flag = 0
                        self.page_login.label_action.setText("请重新登录")
        # 通过检测后的函数
        def get_name(self):
                self.ff.detect_face()
                print("name = ", self.ff.name)
                if self.ff.name == -1:
                        self.page_login.label_action.setText("请返回注册")
                else:
                        self.page_login.label_action.setText("欢迎登录" + self.ff.name)
                      
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——

        # 注册界面默认事件
        def button_logup(self):
                # print("进入 button_logup 函数 ") 
                self.stacked_widget.setCurrentIndex(3)
                self.open_camera()
                self.user = 0
                self.timer.timeout.connect(self.button_logup_timer)
                self.page_logup.label_message.setText(self.message)
                self.page_logup.label_action.setText(self.message)
        
        # 注册定时器事件
        def button_logup_timer(self):
                # print("进入 button_logup_timer 函数 ")                 
                img_1 = self.take_picture()
                img_2 = self.get_down_img()
                if img_2 == -1:
                        self.message = "检测失败"
                        self.user = 0
                else:
                        self.user = 1
                        self.message = "检测成功"

                if self.show_flag:
                        self.page_logup.label_image.setPixmap(QPixmap.fromImage(img_2))
                else:
                       self.page_logup.label_image.setPixmap(QPixmap.fromImage(img_1))
                if self.user == 1:
                        self.get_action()
                self.page_logup.label_message.setText(self.message) 


        # 注册界面提交按钮事件
        def button_submit(self):
                if self.pass_flag == 0:
                        self.timer3 = QtCore.QTimer()
                        self.timer3.start(3000)
                        self.timer3.timeout.connect(self.timer_3)
                        self.pass_flag = 0
                        self.timer_3()
                        # action = self.action[self.pass_flag]
                        # self.pass_flag += 1
                        # print("action = ", action)
                        # self.page_logup.label_action.setText("请"+action)
                else:
                       self.get_name_logup()

        # 注册界面活体检测定时器
        def timer_3(self):
                
                self.show_flag = 0
                index = self.pass_flag % len(self.action)
                action = self.action[index]

                self.page_logup.label_action.setText("请"+ action)
                
                if self.check_one_people():
                        if action in self.temp_action:
                                self.pass_flag += 1

                self.time_flag += 1
                
                self.temp_action = []
                if self.pass_flag >= self.pass_:#__________________________________________________________________________________________________________
                       self.pass_flag = 1
                       self.timer3.stop()
                       self.page_logup.label_action.setText("Pass, 请重新点击提交")
                if self.time_flag >= self.dead_time:
                        self.timer3.stop()
                        self.pass_flag = 1
                        self.page_logup.label_action.setText("请重新注册")

        # 活体检测过后进行的姓名确认函数
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
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——

        # 识别界面中打开摄像头按钮事件
        def button_open_camera(self):
                # print("进入 button_open_camera 函数 ") 
                self.open_camera()
                self.timer.timeout.connect(lambda:self.page_recong.label_image.setPixmap(QPixmap.fromImage(self.take_picture())))

        # 识别界面从文件读取按钮事件
        def button_file(self):
                # print("进入 button_file 函数 ") 
                self.stop_camera()
                options = (QFileDialog.Options()| QFileDialog.ReadOnly)
                self.fileName, _ = QFileDialog.getOpenFileName(self,"选择图片", "","Images (*.png *.xpm *.jpg *.bmp *.gif);;All Files (*)", options=options)
                img = self.deal_with_picture(cv2.imread(self.fileName))
                self.page_recong.label_image.setPixmap(QPixmap.fromImage(img))

        # 识别界面识别按钮事件
        def button_recognition(self):
                # print("进入 button_recognition 函数 ")
                self.ff.load_image(self.original_image)
                
                if self.ff.face_check() == -1:
                       print("无人脸")
                       self.page_recong.label_down.setText("未检测到人脸")
                       return
                
                self.page_recong.label_down.setPixmap(QPixmap.fromImage(self.get_down_img()))

        # 所有界面返回按钮事件
        def button_back(self):
                # print("进入 button_back 函数 ") 
                self.stacked_widget.setCurrentIndex(0)
                self.stop_camera()
                self.user= 0
                self.timer_flag = 0
                self.pass_flag = 0
                self.temp_action = []
                self.real_people = 0
                self.message = ""
                self.show_flag = 0

    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
    # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——

        # 获取动作
        def get_action(self):
                self.ff.load_image(self.original_image)
                if self.ff.face_check() == -1:
                        return
                a = self.ff.compare_distance()
                if len(a) > 0:
                        self.temp_action.extend(a)

        # 切换是否显示人脸特征图
        def change_show(self):
               self.show_flag = self.show_flag ^ 1

        # 拍照函数 通过deal_with_picture 处理后返回 Qimage类型图片
        def take_picture(self):
                # print("进入 take_picture 函数 ") 
                if not self.cap_flag:
                    return
                flag,img = self.cap.read()
                if not flag:
                    print("摄像头打开失败")
                    return   
                img = self.deal_with_picture(img)
                return img

        # 图像处理函数 接受：一张普通图片  返回：Qimage类型图片
        def deal_with_picture(self,img):
                # print("进入 deal_with_picture 函数 ") 
                # 读入图片并转换为 RGB 格式
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
                self.original_image = img
                # 将图片转换为 QImage 格式
                img = QtGui.QImage(img.data, new_width, new_height, QtGui.QImage.Format_RGB888)
                return img

        #  开启摄像头，初始化计时器
        def open_camera(self):
                # print("进入 open_camera 函数 ") 
                if not self.cap_flag:
                    self.cap = cv2.VideoCapture(0)  # 摄像头
                    self.cap_flag = 1
                if not self.timer_flag:
                    self.timer = QtCore.QTimer()
                    self.timer_flag = 1
                    self.timer.start(10)

        # 关闭摄像头，停止计时器
        def stop_camera(self):
                # print("进入 stop_camera 函数 ") 
                if self.timer_flag == 1:
                    self.timer.stop()
                    self.timer_flag = 0
                if self.cap_flag:
                    self.cap.release()
                    self.cap_flag = 0

        # 获取 一张带有人脸标识的 Qimage 格式的图片
        def get_down_img(self):
                # print("进入 recognition 函数 ")
                self.ff.load_image(self.original_image)
                message = self.ff.face_check()
                
                if message == -1:
                    return -1
                self.user = 1
                self.ff.get_feature_map()
                img = cv2.imread("./temp_image/down.jpg")
                height, width, channel = img.shape
                bytesPerLine = 3 * width
                qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
                return qImg

        # 一些可能简化程序的check函数

        def check_one_people(self):
                self.ff.load_image(self.original_image)
                self.ff.get_face_locations()
                self.user_endcoding = self.ff.get_face_encodings()
                if not self.user_old_endcoding:
                        self.user_old_endcoding = self.user_endcoding
                else:
                        if self.user_endcoding != self.user_old_endcoding:
                                self.message = "识别错误"
                                return 0
                return 1
                

              
              
if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(69,69,69))
        window.setPalette(palette)
        window.show()
        sys.exit(app.exec_())
