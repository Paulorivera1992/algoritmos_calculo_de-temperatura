import subprocess
from time import time
from pypylon import pylon
from opcua import Client
from opcua.client.ua_client import UaClient
from opcua import ua
import numpy as np 
from datetime import datetime

#status=False

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
      print("error de coneccion") 
      return False  
  
  

def Tf_direct(ruta):
  try:
    completed = subprocess.run(['./Tf_direct',ruta], check=True) 
  except subprocess.CalledProcessError as err:
      print('ERROR:', err)

def Tf_rec_spect(ruta):
  try:
    completed = subprocess.run(['./Tf_rec_spect',ruta], check=True) 
  except subprocess.CalledProcessError as err:
      print('ERROR:', err)

def Tf(ruta):
  try:
    completed = subprocess.run(['./calculo_Tf',ruta], check=True) 
  except subprocess.CalledProcessError as err:
      print('ERROR:', err)

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
        print("el nodo que busca no se encuentra")
      client.disconnect()
  except:
	    #desconeccion
      print("no se puede conectar al servidor")
      #client.disconnect()


def cambiar_tipo(server,nodo,tipo):
  client = Client(server)
  try:
      client.connect()#conecta el servidor
      var=client.get_node("ns=1;s="+nodo)#se obtiene el primer nodo
      variable2=var.get_children()
      tamano=np.size(variable2)
      if tamano==5:
        tipo=variable2[1].set_value(tipo)
        tiempo=variable2[2].get_value()
        val=variable2[3].get_value()
        status=variable2[4].get_value()
      else:
        print("el nodo que busca no se encuentra")
      client.disconnect()
  except:
	    #desconeccion
      print("no se puede conectar al servidor")
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
        print("el nodo que busca no se encuentra")
      client.disconnect()
  
  except: 
      print("no se puede conectar al servidor")
      #client.disconnect()

def escribir_datos(server,archivo,nodo,status):
  f = open (archivo,'r')
  linea=f.readlines()[-1] 
  datos=linea.split()
  tiempo=datos[0]+' '+datos[1]
  valor=datos[2]
  cambiar_valor(server,nodo,tiempo,valor,status)
  f.close() 

#funcion principal 
f=open("archivos_temperatura/Tf_direct.txt","w")
f.close()
f=open("archivos_temperatura/Tf_rec_spect.txt","w")
f.close()

servidor="opc.tcp://192.168.1.112:4840"
cambiar_tipo(servidor,"sensor 10","Tf_direct")
cambiar_tipo(servidor,"sensor 5","Tf_rec_spect")
cambiar_nombre(servidor,"sensor 10","quemador1")
cambiar_nombre(servidor,"sensor 5","quemador1")
while True:
#for k in range(10):
  print('procesando nueva imagen \n')
  #nombre_archivo='imagenes_llama/prueba_Tf_rec_spect.tiff'
  nombre_archivo='imagenes_llama/Llama.tiff'
  
  #guarda las imagenes
  #start_time = time()
  estatus=save_image(nombre_archivo)
  #captura_time = time() - start_time
  
  #calculo de temperatura directa
  #start_time = time()
  #Tf_direct(nombre_archivo)
  #direct_time = time() - start_time
  #print('el tiempo de Tf direct es',direct_time)
  
  #calculo de temperatura con rec spectral 
  #start_time = time()
  #Tf_rec_spect(nombre_archivo)
  #spect_time = time() - start_time
  #print('el tiempo de Tf spect es',spect_time)
 
 #calculo de temperatura con rec spectral 
  #start_time = time()
  Tf(nombre_archivo)
  #Tf_time = time() - start_time
  #print('el tiempo de Tf es',Tf_time)
  
  escribir_datos(servidor,'archivos_temperatura/Tf_direct.txt',"sensor 10",estatus)  
  escribir_datos(servidor,'archivos_temperatura/Tf_rec_spect.txt',"sensor 5",estatus)  