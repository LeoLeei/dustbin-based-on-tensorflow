#-*-coding:GBK -*- 
# coding: utf-8
import os
import time
import socket
import cv2
import numpy as np
import sys
import struct

cycle=1
while cycle<=1:
      host_port = ('192.168.43.14',8080)
      camera = cv2.VideoCapture(0) # 参数0表示第一个摄像头，摄像头的设定
      index = 1
      path2 = '/home/pi/pre_image'     #保存图片的位置

      class ClientSocket(object):
          def __init__(self):
              # socket.AF_INET用于服务器与服务器之间的网络通信
              # socket.SOCK_STREAM代表基于TCP的流式socket通信
              self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
              self.client_socket.connect(host_port) #链接服务器
              self.encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]  #设置编码参数
      # 判断视频是否打开
      if (camera.isOpened()):
          print('Open')
      else:
          print('摄像头未打开')

      # 测试用,查看视频size
      size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
              int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
      print('size:'+repr(size))

      fps = 5  # 帧率
      pre_frame = None  # 总是取视频流前一帧做为背景相对下一帧进行比较
      i = 0
      while index<12:
          start = time.time()
          grabbed, frame_lwpCV = camera.read() # 读取视频流
          gray_lwpCV = cv2.cvtColor(frame_lwpCV, cv2.COLOR_BGR2GRAY) # 转灰度图

          if not grabbed:
              break
          end = time.time()

          # 运动检测部分
          seconds = end - start
          if seconds < 1.0 / fps:
              time.sleep(1.0 / fps - seconds)
          gray_lwpCV = cv2.resize(gray_lwpCV, (500, 500))
          # 用高斯滤波进行模糊处理，进行处理的原因：每个输入的视频都会因自然震动、光照变化或者摄像头本身等原因而产生噪声。对噪声进行平滑是为了避免在运动和跟踪时将其检测出来。
          gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (21, 21), 0) 
    
          # 在完成对帧的灰度转换和平滑后，就可计算与背景帧的差异，并得到一个差分图（different map）。还需要应用阈值来得到一幅黑白图像，并通过下面代码来膨胀（dilate）图像，从而对孔（hole）和缺陷（imperfection）进行归一化处理
          if pre_frame is None:
              pre_frame = gray_lwpCV
          else:
              img_delta = cv2.absdiff(pre_frame, gray_lwpCV)
              thresh = cv2.threshold(img_delta, 25, 255, cv2.THRESH_BINARY)[1]
              thresh = cv2.dilate(thresh, None, iterations=2)
              _,contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
              for c in contours:
                  if cv2.contourArea(c) < 2000: # 设置敏感度
                      continue
                  else:
                      print("咦,有什么东西在动0.0")
                      ##time.sleep(1);
                      ret ,frame = camera.read()
                      cv2.imwrite("%s/%d.jpeg" % ("/home/pi/pre_image", index),
                      cv2.resize(frame, (299, 299), interpolation=cv2.INTER_AREA))
                      print("%s: %d 张图片" % ("/home/pi/pre_image", index))
                      index += 1
                      pre_frame = gray_lwpCV
      indexs=index-1
      Str=str(indexs)+".jpeg"
      j = 1
      while j < index-1:
          new = "/"+str(j)+".jpeg"
          os.remove(path2 + new)        
          print("Delete File: " + path2 + new)
          j += 1
    
      def sock_client():
          try:
              s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              s.connect(('192.168.43.14', 6666))
          except socket.error as msg:
              print(msg)
              print(sys.exit(1))
 
          while True:
              #filepath = input('input the file: ')
              ##os.system("fswebcam -S 10 14.jpeg")
              time.sleep(1)
              filepath = '/home/pi/pre_image/'+Str
              fhead = struct.pack(b'128sl', bytes(os.path.basename(filepath).encode('utf-8')), os.stat(filepath).st_size)
              s.send(fhead)
              print('client filepath: {0}'.format(filepath))
  
              fp = open(filepath, 'rb')
              while 1:
                  data = fp.read(1024)
                  if not data:
                      print('{0} file send over...'.format(filepath))
                      break
                  s.send(data)
              s.close()
              break
 
 
      if __name__ == '__main__':
          sock_client()

      # When everything done, release the capture
      for root, dirs, files in os.walk(path2):
               for name in files:
                     if name.endswith(".jpeg"):         
                            os.remove(os.path.join(root, name))
                            print("Delete File: " + os.path.join(root, name))
      camera.release()
      cv2.destroyAllWindows()
      time.sleep(88)
