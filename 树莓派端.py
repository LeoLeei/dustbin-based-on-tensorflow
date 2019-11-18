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
      camera = cv2.VideoCapture(0) # ����0��ʾ��һ������ͷ������ͷ���趨
      index = 1
      path2 = '/home/pi/pre_image'     #����ͼƬ��λ��

      class ClientSocket(object):
          def __init__(self):
              # socket.AF_INET���ڷ������������֮�������ͨ��
              # socket.SOCK_STREAM�������TCP����ʽsocketͨ��
              self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
              self.client_socket.connect(host_port) #���ӷ�����
              self.encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]  #���ñ������
      # �ж���Ƶ�Ƿ��
      if (camera.isOpened()):
          print('Open')
      else:
          print('����ͷδ��')

      # ������,�鿴��Ƶsize
      size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
              int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
      print('size:'+repr(size))

      fps = 5  # ֡��
      pre_frame = None  # ����ȡ��Ƶ��ǰһ֡��Ϊ���������һ֡���бȽ�
      i = 0
      while index<12:
          start = time.time()
          grabbed, frame_lwpCV = camera.read() # ��ȡ��Ƶ��
          gray_lwpCV = cv2.cvtColor(frame_lwpCV, cv2.COLOR_BGR2GRAY) # ת�Ҷ�ͼ

          if not grabbed:
              break
          end = time.time()

          # �˶���ⲿ��
          seconds = end - start
          if seconds < 1.0 / fps:
              time.sleep(1.0 / fps - seconds)
          gray_lwpCV = cv2.resize(gray_lwpCV, (500, 500))
          # �ø�˹�˲�����ģ���������д����ԭ��ÿ���������Ƶ��������Ȼ�𶯡����ձ仯��������ͷ�����ԭ�����������������������ƽ����Ϊ�˱������˶��͸���ʱ�����������
          gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (21, 21), 0) 
    
          # ����ɶ�֡�ĻҶ�ת����ƽ���󣬾Ϳɼ����뱳��֡�Ĳ��죬���õ�һ�����ͼ��different map��������ҪӦ����ֵ���õ�һ���ڰ�ͼ�񣬲�ͨ��������������ͣ�dilate��ͼ�񣬴Ӷ��Կף�hole����ȱ�ݣ�imperfection�����й�һ������
          if pre_frame is None:
              pre_frame = gray_lwpCV
          else:
              img_delta = cv2.absdiff(pre_frame, gray_lwpCV)
              thresh = cv2.threshold(img_delta, 25, 255, cv2.THRESH_BINARY)[1]
              thresh = cv2.dilate(thresh, None, iterations=2)
              _,contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
              for c in contours:
                  if cv2.contourArea(c) < 2000: # �������ж�
                      continue
                  else:
                      print("��,��ʲô�����ڶ�0.0")
                      ##time.sleep(1);
                      ret ,frame = camera.read()
                      cv2.imwrite("%s/%d.jpeg" % ("/home/pi/pre_image", index),
                      cv2.resize(frame, (299, 299), interpolation=cv2.INTER_AREA))
                      print("%s: %d ��ͼƬ" % ("/home/pi/pre_image", index))
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
