import datetime
import requests
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QTimer
from onvif import ONVIFCamera
import sys
import json
import cv2
from ui import Ui_Form

sys.path.insert(0, 'D:\\Programs\\env')


class UI(QWidget, Ui_Form):
    def __init__(self):
        super(UI, self).__init__()
        # 显示的初始化
        self.frame = None
        self.setupUi(self)
        # 摄像头开关的初始化
        self.camera_timer = None
        self.camera = None
        # 摄像头上下左右的初始化
        self.ptz = None
        self.profile_token = None
        self.init_onvif()
        # 摄像头分析
        self.file_name = None

    # 摄像头开关实现
    # 注:异常抛出的处理是必要的,因为我的程序没有边界处理,所以到达边界后超出范围会抛出异常
    # 写完初始化与一个方向的控制剩下的部分复制黏贴
    def show_camera(self):
        if self.camera == None:
            self.camera = cv2.VideoCapture('rtsp://admin:@172.16.20.13:554/stream1')
        ret, self.frame = self.camera.read()
        if ret:
            h, w, _ = self.frame.shape
            self.video.setPixmap(QPixmap.fromImage(QImage(self.frame.data, w, h, QImage.Format_BGR888)))
        # 开启摄像头

    def camera_control_on(self):
        if self.camera == None:
            self.camera = cv2.VideoCapture('rtsp://admin:@172.16.20.13:554/stream1')
        self.camera_timer = QTimer(self, timeout=self.show_camera)
        self.camera_timer.start(60)
        # 关闭摄像头

    def camera_control_off(self):
        if self.camera.isOpened():
            self.camera.release()
            self.camera = None
            self.video.clear()
            self.camera_timer.stop()

    # 摄像头上下左右实现
    def init_onvif(self):
        # 摄像头的连接
        cam = ONVIFCamera('172.16.20.13', 80, 'admin', 'admin')
        self.ptz = cam.create_ptz_service()
        # 配置文件的获取
        media = cam.create_media_service()
        self.profile_token = media.GetProfiles()[0].token
        # 摄像头左移

    def left_move(self):
        if self.ptz:
            try:
                self.ptz.RelativeMove({
                    'ProfileToken': self.profile_token,
                    'Translation': {
                        'PanTilt': {'x': -0.1, 'y': 0}}
                })
            except Exception as e:
                print("到达左极限")

        # 摄像头右移

    def right_move(self):
        if self.ptz:
            try:
                self.ptz.RelativeMove({
                    'ProfileToken': self.profile_token,
                    'Translation': {
                        'PanTilt': {'x': 0.1, 'y': 0}}})
            except Exception as e:
                print("到达右极限")

        # 摄像头上移

    def up_move(self):
        if self.ptz:
            try:
                self.ptz.RelativeMove({
                    'ProfileToken': self.profile_token,
                    'Translation': {
                        'PanTilt': {'x': 0, 'y': -0.1}}})
            except Exception as e:
                print("到达上极限")

        # 摄像头下移

    def down_move(self):
        if self.ptz:
            try:
                self.ptz.RelativeMove({
                    'ProfileToken': self.profile_token,
                    'Translation': {
                        'PanTilt': {'x': 0, 'y': 0.1}}})
            except Exception as e:
                print("到达下极限")

    # 摄像头拍照实现
    def screens_shot(self):
        self.file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'.jpg'
        cv2.imwrite(self.file_name, self.frame)
        print(f"已截取图片：{self.file_name}")
    
    # AI模型分析实现
    def screen_detect(self):
        import torch
        yolo = torch.hub.load(path="./yolov5-master",
                              model='yolov5s.pt',
                              source='local'
                                )
        result = yolo(f"C:/sers/Newland/Desktop/摄像头上下左右/{self.file_name}")
        result.save()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    run = UI()
    run.show()
    sys.exit(app.exec_())
