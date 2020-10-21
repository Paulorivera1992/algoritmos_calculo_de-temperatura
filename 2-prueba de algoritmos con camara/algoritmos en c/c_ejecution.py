import subprocess
from time import time
from pypylon import pylon

def save_image(ruta):
  img = pylon.PylonImage()
  tlf = pylon.TlFactory.GetInstance()
  cam = pylon.InstantCamera(tlf.CreateFirstDevice())
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
  cam.Close()
  
  

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
 

#funcion principal 
#f=open("Tf_rec_spect_temp.txt","w")
#f.write('fecha      hora     temperatura\n')
#f.close()
#while True:
for k in range(25):
  print('procesando nueva imagen'+str(k+1)+' \n')
  #nombre_archivo='imagenes_llama/prueba_Tf_rec_spect.tiff'
  nombre_archivo='imagenes_llama/Llama ('+str(k+1)+').tiff'
  
  #guarda las imagenes
  #start_time = time()
  #save_image(nombre_archivo)
  #captura_time = time() - start_time
  
  #calculo de temperatura directa
  start_time = time()
  Tf_direct(nombre_archivo)
  direct_time = time() - start_time
  
  #calculo de temperatura con rec spectral 
  start_time = time()
  Tf_rec_spect(nombre_archivo)
  spect_time = time() - start_time
  
  
  #print('la temperatura es',temperatura)
  #print('el tiempo es',procesamiento_time)
