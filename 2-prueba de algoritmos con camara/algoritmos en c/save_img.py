from pypylon import pylon
import platform


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
  
  # codigo para obtener la matriz RGB sin guardar la imagen
  #converter = pylon.ImageFormatConverter()
  #converter.OutputPixelFormat = pylon.PixelType_RGB8packed
  #converted = converter.Convert(result)
  #image_rgb = converted.GetArray()
  #print("el tamano de la matriz es", image_rgb.shape)
  
  #codigo para guardar la imagen
  img.AttachGrabResultBuffer(result)     
  img.Save(pylon.ImageFileFormat_Tiff, ruta)

  img.Release()
  cam.StopGrabbing()
  cam.Close()

filename = "imagenes_llama/saved_pypylon_img_1.tiff"
save_image(filename)