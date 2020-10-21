import subprocess
from time import time
from pypylon import pylon
from opcua import Client
from opcua.client.ua_client import UaClient
from opcua import ua
import numpy as np 
from datetime import datetime
import socket
import logging


def save_image(ruta):
  img = pylon.PylonImage()
  tlf = pylon.TlFactory.GetInstance()
  try:
      cam = pylon.InstantCamera(tlf.CreateFirstDevice())     
      try:
          cam.Open()
          #configuracion de parametros de tamano
          cam.Width.SetValue(1920)
          cam.Height.SetValue(1200)
          cam.OffsetX=0 #debe ser multiplo de 2
          cam.OffsetY=0  #debe ser multiplo de 2
          #inicia captura de imagenes
          cam.StartGrabbing()
          result=cam.RetrieveResult(2000)
          #codigo para guardar la imagen
          img.AttachGrabResultBuffer(result)     
          img.Save(pylon.ImageFileFormat_Tiff, ruta)
          img.Release()
          cam.StopGrabbing()
          return True
      except: # excepcion en caso de que no se pueda generar la coneccion
          cam.Close()
          return False
      finally:#si finaliza la obtencion de la foto
          cam.Close()         
  except: #escepcion en caso de que la camara no este conectada
      logger.error("Error conectando la camara") 
      return False  

def Tf(ruta):
  try:
    completed = subprocess.run(['./calculo_Tf',ruta], check=True) 
  except subprocess.CalledProcessError as err:
      logger.error('Error en la ejecucion del algoritmo:', err)

def cambiar_nombre(server,nodo,nombre):
  client = Client(server)
  try:
      client.connect()#conecta el servidor
      var=client.get_node("ns=1;s="+nodo)#se obtiene el primer nodo
      variable2=var.get_children()
      tamano=np.size(variable2)
      if tamano==5:
        nombre=variable2[0].set_value(nombre)
      else:
        logger.warning("No se encuentra el nodo en el servidor opc")
      client.disconnect()
  except:
	    #desconeccion
      logger.error("No se puede conectar con el servidor opc")
      #client.disconnect()


def cambiar_tipo(server,nodo,tipo):
  client = Client(server)
  try:
      client.connect()
      #conecta el servidor
      var=client.get_node("ns=1;s="+nodo)#se obtiene el primer nodo
      variable2=var.get_children()
      tamano=np.size(variable2)
      if tamano==5:
        tipo=variable2[1].set_value(tipo)
        tiempo=variable2[2].get_value()
        val=variable2[3].get_value()
        status=variable2[4].get_value()
      else:
        logger.warning("No se encuentra el nodo en el servidor opc")
      client.disconnect()
  except:
	    #desconeccion
      logger.error("No se puede conectar con el servidor opc")
      #client.disconnect()

def cambiar_valor(server,nodo,tiemp,valor,estatus):
  client = Client(server)
  try:
      client.connect()#conecta el servidor
      var=client.get_node("ns=1;s="+nodo)#se obtiene el primer nodo
      variable2=var.get_children()
      tamano=np.size(variable2)
      datetime_object = datetime.strptime(tiemp, '%d/%m/%Y %H:%M:%S')
      if tamano>0:
        tiempo=variable2[2].set_value(datetime_object)
        val=variable2[3].set_value(valor)
        status=variable2[4].set_value(estatus)
      else:
        logger.warning("No se encuentra el nodo en el servidor opc")
      client.disconnect()
  
  except: 
      logger.error("No se puede conectar con el servidor opc")
      #client.disconnect()

def escribir_datos(server,archivo,nodo,status):
  f = open (archivo,'r')
  linea=f.readlines()[-1] 
  datos=linea.split()
  tiempo=datos[0]+' '+datos[1]
  valor=datos[2]
  cambiar_valor(server,nodo,tiempo,valor,status)
  f.close() 

def comprobar_ip(addr):
  try:
      #crea socket 
      socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      socket.setdefaulttimeout(1)
      result = socket_obj.connect_ex(("192.168.1.107",22)) #se escanea uno de los puertos estandar abiertos 22,80
      if(result):
        logger.error("El host/puerto no se encuentra disponible")
      else:
        logger.info("El host/puerto esta disponible")
      socket_obj.close()
  except:
      logger.error("Fallo el escaneo de ip/puertos")
      
def generar_logger():
  logger = logging.getLogger("TFlog")
  logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter("%(levelname)s:%(asctime)s - %(message)s")
  handler = logging.FileHandler("TF.log")
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  return logger

def crear_archivos_de_datos():
  f=open("archivos_temperatura/Tf_direct.txt","w")
  f.close()
  f=open("archivos_temperatura/Tf_rec_spect.txt","w")
  f.close()

#funcion principal
logger=generar_logger()
crear_archivos_de_datos()
ip="192.168.1.107"
comprobar_ip(ip)
servidor="opc.tcp://"+ip+":4840"       
cambiar_tipo(servidor,"sensor 10","Tf_direct")
cambiar_tipo(servidor,"sensor 5","Tf_rec_spect")
cambiar_nombre(servidor,"sensor 10","quemador1")
cambiar_nombre(servidor,"sensor 5","quemador1")
while True:
  logger.info('Procesando nueva imagen')
  nombre_archivo='imagenes_llama/Llama.tiff'
  
  #guarda las imagenes
  #start_time = time()
  estatus=save_image(nombre_archivo)
  #captura_time = time() - start_time
  
  #calculo de temperatura con rec spectral 
  #start_time = time()
  Tf(nombre_archivo)
  #Tf_time = time() - start_time
  #print('el tiempo de Tf es',Tf_time)
  
  escribir_datos(servidor,'archivos_temperatura/Tf_direct.txt',"sensor 10",estatus)  
  escribir_datos(servidor,'archivos_temperatura/Tf_rec_spect.txt',"sensor 5",estatus)  