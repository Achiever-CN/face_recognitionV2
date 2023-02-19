import face_recognition
import pickle
import cv2
import numpy as np  
import math


class face_function():

        def __init__(self):
                print("face_function __init__")

                self.known_face_encodings, self.known_face_names = self.load_known_faces_and_names()
                self.face_locations = None
                self.landmarks_list = None
                self.distances = [0,0,0]
                self.old_distances = [5,5,5]
                self.action = ""
                self.image = None       # 一张经过裁减不带特征的图片
                self.down_image = None  # 一张经过裁减携带特征的图片
                self.face_encodings = None
                self.name = None

                self.eye_pass = 2       # 眨眼动作判定标准，值越大，动作幅度要求越大
                self.mouse_pass = 3   # 同上

        def load_image(self, image):
                self.image = image

        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——

        # 获取人脸位置
        def get_face_locations(self):
                self.face_locations =  face_recognition.face_locations(self.image)

        # 获取人脸特征点位置
        def get_face_landmarks_list(self):
                self.landmarks_list =  face_recognition.face_landmarks(self.image)

        # 获取人脸编码
        def get_face_encodings(self):
                self.face_encodings = face_recognition.face_encodings(self.image, self.face_locations)

        # 获取带有特征值的图像
        def get_feature_map(self):
                self.get_face_landmarks_list()
                self.draw_line()


        # 在图像上画线            
        def draw_line(self):
                for i in self.landmarks_list[0]:
                        list = self.landmarks_list[0][i]
                        point_begin = list[0]
                        for point_end in list[1:]:
                                cv2.line(self.down_image, point_begin, point_end, (0,0,255), 1)
                                point_begin = point_end
                cv2.imwrite("./temp_image/down.jpg", self.down_image)


        # 从文件加载人脸名称列表和人脸编码列表
        def load_known_faces_and_names(self):
        # Loading the data from the pickle file
                with open("known_faces_and_names.pickle", "rb") as handle:
                        data = pickle.load(handle)
                return data["faces"], data["names"]
        
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——

        # 识别图像，将带有标识的图像保存， 同时获取人脸特征点位置
        def face_check(self):
                self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
                self.get_face_locations()
                if not self.face_locations:
                        print("没有检测到人脸")
                        return -1
                self.down_image = self.image
                self.get_feature_map()
                return 1
        
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——

        # 将人脸名称列表和人脸编码列表储存起来
        def update_data(self):
                with open("known_faces_and_names.pickle", "wb") as handle:
                        pickle.dump({"faces": self.known_face_encodings, "names": self.known_face_names}, handle)
                self.known_face_encodings, self.known_face_names = self.load_known_faces_and_names()
                print("更新成功")
                print(self.known_face_names)
                        



        # 比对人脸
        def detect_face(self):
                print("进入 detect_face 函数 ")
                self.get_face_locations()
                self.get_face_encodings()
                # print("face_ecodings = ", self.face_encodings)
                for face_encoding in self.face_encodings:
                        
                        self.face_encoding = face_encoding
                        # See if the face is a match for the known face(s)
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        print(matches)
                        # If a match was found in known_face_encodings, just use the first one.
                        if True in matches:
                                first_match_index = matches.index(True)
                                name = self.known_face_names[first_match_index]

                        # Or instead, use the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                                name = self.known_face_names[best_match_index]
                                self.name = name
                        else:
                                self.name = -1

        # 添加人脸信息 接受： 名称 编码  返回： 无
        def face_add(self):
                # print("进入 face_add 函数 ")
                self.known_face_encodings.append(self.face_encoding)
                self.known_face_names.append(self.name)
                print("添加成功")


        def update_disatance(self):
                self.old_distances[0] = self.distances[0]
                self.old_distances[1] = self.distances[1]
                self.old_distances[2] = self.distances[2]
                self.distances[0] =  self.get_distanse(self.landmarks_list[0]["left_eye"][1], self.landmarks_list[0]["left_eye"][4]) 
                self.distances[1] = self.get_distanse(self.landmarks_list[0]["right_eye"][1], self.landmarks_list[0]["right_eye"][4])
                self.distances[2] = self.get_distanse(self.landmarks_list[0]["top_lip"][2], self.landmarks_list[0]["bottom_lip"][3])
                
 

        def compare_distance(self):
                self.update_disatance()
                self.action = []
                left_eye = abs(self.distances[0] - self.old_distances[0])
                right_eye = abs(self.distances[1] - self.old_distances[1])
                mouse = abs(self.distances[2] - self.old_distances[2])
                # 下方调节判定阈值
                if left_eye > self.eye_pass or right_eye > self.eye_pass:
                        self.action.extend(["眨眼"])
                if mouse > self.mouse_pass:
                        self.action.extend(["张嘴"])
                return self.action                    



        # 计算距离函数 接受：两个点坐标 返回：距离
        def get_distanse(self,point_1, point_2):
              return int(math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2))
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——
        # -——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——-——

# obama_image = face_recognition.load_image_file("./temp_image/obama.jpg")
# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# biden_image = face_recognition.load_image_file("./temp_image/biden.jpg")
# biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# known_face_encodings = [
#         obama_face_encoding,
#         biden_face_encoding
# ]
# known_face_names = [
#         "Barack Obama",
#         "Joe Biden"
# ]

# f = face_function()
# f.known_face_encodings = known_face_encodings
# f.known_face_names = known_face_names
# f.update_data()


"""
chin: 共  17 个 [(160, 133), (162, 144), (164, 155), (167, 165), (172, 175), (179, 183), (188, 189), (198, 194), (209, 194), (218, 192), (226, 186), (232, 178), (236, 168), (238, 157), (240, 146), (241, 135), (240, 124)]
left_eyebrow: 共  5 个 [(169, 126), (174, 120), (182, 118), (190, 118), (198, 121)]
right_eyebrow: 共  5 个 [(205, 120), (212, 115), (220, 113), (227, 114), (232, 119)]
nose_bridge: 共  4 个 [(203, 129), (204, 137), (205, 145), (206, 152)]
nose_tip: 共  5 个 [(197, 159), (202, 159), (207, 160), (211, 158), (215, 157)]
left_eye: 共  6 个 [(177, 134), (182, 132), (187, 132), (192, 134), (187, 135), (182, 135)]
right_eye: 共  6 个 [(213, 132), (217, 129), (222, 128), (226, 129), (223, 131), (218, 132)]
top_lip: 共  12 个 [(192, 173), (198, 170), (203, 167), (207, 168), (211, 166), (216, 168), (220, 170), (218, 170), (211, 170), (207, 171), (203, 171), (195, 173)]
bottom_lip: 共  12 个 [(220, 170), (217, 175), (212, 178), (208, 179), (204, 179), (198, 177), (192, 173), (195, 173), (203, 173), (207, 173), (211, 172), (218, 170)]
"""