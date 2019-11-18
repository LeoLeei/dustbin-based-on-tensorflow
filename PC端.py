#-*-coding:GBK -*- 
# coding: utf-8
import tensorflow as tf
import numpy as np
import re
#from PIL import Image
import matplotlib.pyplot as plt
import serial
import socket
import os
import sys
import struct
import cv2

serialPort = "COM12"  # ����
baudRate = 9600
ser = serial.Serial(serialPort, baudRate, timeout=0.5)
print("�������ã�����=%s ��������=%d" % (serialPort, baudRate))
path2 = 'C:/tensorflow/pre_image/'

cycle=1

while cycle<=1:
	
     def socket_service():
         try:
             s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
             s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
             s.bind(('', 6666))
             s.listen(10)
         except socket.error as msg:
             print(msg)
             sys.exit(1)
 
         print("Wait")
 
         while True:
             sock, addr = s.accept()
             deal_data(sock, addr)
             break
         s.close()
 
 
     def deal_data(sock, addr):
         print("Accept connection from {0}".format(addr))
 
         while True:
             fileinfo_size = struct.calcsize('128sl')
             buf = sock.recv(fileinfo_size)
             if buf:
                 filename, filesize = struct.unpack('128sl', buf)
                 fn = filename.decode().strip('\x00')
                 new_filename = os.path.join('./',fn)
 
                 recvd_size = 0
                 fp = open(new_filename, 'wb')
 
                 while not recvd_size == filesize:
                     if filesize - recvd_size > 1024:
                         data = sock.recv(1024)
                         recvd_size += len(data)
                     else:
                         data = sock.recv(1024)
                         recvd_size = filesize
                     fp.write(data)
                 fp.close()
             sock.close()
             break

     if __name__ == '__main__':
         socket_service()
     lines = tf.gfile.GFile('C:/tensorflow/output_labels.txt').readlines() 

     uid_to_human = {}

         #һ��һ�ж�ȡ����

     for uid,line in enumerate(lines) :

         #ȥ�����з�

         line=line.strip('\n')

         uid_to_human[uid] = line

 
     def id_to_string(node_id):

         if node_id not in uid_to_human:

              return ''

         return uid_to_human[node_id]

 

     with tf.gfile.FastGFile('C:/tensorflow/output_graph.pb', 'rb') as f:

         graph_def = tf.GraphDef()

         graph_def.ParseFromString(f.read())

         tf.import_graph_def(graph_def, name='')

     with tf.Session() as sess:

         softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

    #����Ŀ¼
         for root,dirs,files in os.walk('C:/tensorflow/pre_image/'):

              for file in files:

                 #����ͼƬ

                 if not file.endswith('.jpeg') or file.startswith('.'):

                     continue

                 image_data = tf.gfile.FastGFile(os.path.join(root,file), 'rb').read()

                 predictions = sess.run(softmax_tensor,{'DecodeJpeg/contents:0': image_data})#ͼƬ��ʽ��jpg��ʽ

                 predictions = np.squeeze(predictions)#�ѽ��תΪ1ά����

 

                 #��ӡͼƬ·��������

                 image_path = os.path.join(root,file)

                 print(image_path)

                 #��ʾͼƬ

#                  img=Image.open(image_path)

#                  plt.imshow(img)

#                  plt.axis('off')

#                  plt.show()

 

                      #����

                 top_k = predictions.argsort()[::-1]

                 print(top_k)

                 for node_id in top_k:     

                     #��ȡ��������

                     human_string = id_to_string(node_id)

                #��ȡ�÷�������Ŷ�

                     score = predictions[node_id]

                     print('%s (score = %.5f)' % (human_string, score))

                     print()

                     if top_k[0]== 0:
				
                           demo0=b"0"#��0ת��ΪASCII�뷽�㷢��
                     
                           ser.write(demo0)#ser.write�����򴮿���д������	
                     if top_k[0]== 1:
				
                           demo1=b"1"#ͬ��
                
                           ser.write(demo1)
                
                     if top_k[0]== 2:
	
	                       demo2=b"2"#ͬ��
	            
	                       ser.write(demo2)
	            
                     if top_k[0]== 3:
				
                          demo3=b"3"
				
                          ser.write(demo3)
 
                     break
                
# When everything done, release the capture
     for root, dirs, files in os.walk(path2):
              for name in files:
                    if name.endswith(".jpeg"):         
                           os.remove(os.path.join(root, name))
                           print("Delete File: " + os.path.join(root, name))
     cv2.destroyAllWindows()


