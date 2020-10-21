#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time
from daemon import runner
import Funciones_Tf 

class App():
   def __init__(self):
      self.stdin_path      = '/dev/null'
      self.stdout_path     = '/dev/tty'
      self.stderr_path     = '/dev/tty'
      self.pidfile_path    =  '/var/run/test.pid'
      self.pidfile_timeout = 5

   def run(self):
      Funciones_Tf.crear_archivos_de_datos()
      ip="192.168.1.107"
      Funciones_Tf.comprobar_ip(ip,logger)
      servidor="opc.tcp://"+ip+":4840"  
      Funciones_Tf.cambiar_tipo(servidor,"sensor 10","Tf_direct",logger)
      Funciones_Tf.cambiar_tipo(servidor,"sensor 5","Tf_rec_spect",logger)
      Funciones_Tf.cambiar_nombre(servidor,"sensor 10","quemador1",logger)
      Funciones_Tf.cambiar_nombre(servidor,"sensor 5","quemador1",logger)
      while True:
         nombre_archivo='/home/ubuntu/rasberry/Algoritmos_C/imagenes_llama/Llama.tiff'
         estatus=Funciones_Tf.save_image(nombre_archivo,logger)
         logger.info('Procesando nueva imagen')
         Funciones_Tf.Tf(nombre_archivo,logger)
         Funciones_Tf.escribir_datos(servidor,'/home/ubuntu/rasberry/Algoritmos_C/archivos_temperatura/Tf_direct.txt',"sensor 10",estatus,logger)  
         Funciones_Tf.escribir_datos(servidor,'/home/ubuntu/rasberry/Algoritmos_C/archivos_temperatura/Tf_rec_spect.txt',"sensor 5",estatus,logger) 

if __name__ == '__main__':
   app = App()
   logger = logging.getLogger("TFlog")
   logger.setLevel(logging.DEBUG)
   formatter = logging.Formatter("%(levelname)s:%(asctime)s - %(message)s")
   handler = logging.FileHandler("/home/ubuntu/rasberry/Algoritmos_C/TF.log")
   handler.setFormatter(formatter)
   logger.addHandler(handler)
  
   serv = runner.DaemonRunner(app)
   serv.daemon_context.files_preserve=[handler.stream]
   serv.do_action()