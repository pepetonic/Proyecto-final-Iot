#CONFIGURACIONES
#import RPi.GPIO as GPIO #importamos la libreria GPIO
#Para instalar gpiozero(libreria para poder utilizar el MCP3008):
#from gpiozero import MCP3008
import requests
import mysql.connector
import json
import hashlib
import time
import threading
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from random import randrange





#def configuracionInicial():
#  GPIO.setmode(GPIO.BCM)   # configuramos los GPIO con la disposicion BCM
#  GPIO.setup(17, GPIO.OUT) # GPIO 17 sera de salida 
  
  
#Simula los valores que se obtienen de la fotorresistencia
def simularFotorresistencia():
  #fotoresistencia = MCP3008(channel=0) ## valor real de la fotoresistencia
  valorLuz = random.randint(200,950)
  print ("Valor de la Fotorrsistencia: "+str(valorLuz))
  return valorLuz

#Consulta a la BD interna del Raspberry  
def consultaBD():
  try:
    query = "SELECT * FROM raspberry"	
    mycursor.execute(query)
    result = mycursor.fetchall()
    return result
  except:
    print("Error en la consulta")

#Peticion para conocer los valores de encendido y el modo del sistema
def peticionServe(idR):
  url='http://192.168.0.22/ServidorWebRasp/index.php/?idr='+str(idR)
  print (url)
  resp = requests.get(url)
  myJson = resp.json()  
  resp.close()
  return myJson

#peticion para modificar el modo del sistema
def peticionServeModificar(idR):   
  url='http://192.168.0.22/ServidorWebRasp/modificar.php/'
  data = {'idr': idR, 'estado': 0}
  resp = requests.post(url, data = data) 
  resp.close()
   
#funcion para encender el foco de forma 'MANUAL'
def encenderFoco(valor):
  if valor==1:
    print ("Foco encendido")
    #GPIO.output(17, 1)         # Hace el GPIO 17 de salida con 5VCC (HIGH)
  else:
    print ("Foco apagado")
    #GPIO.output(17, 0) 	# corta el flujo de 5VCC, apaga la bombilla

#funcion para encender el foco de forma 'AUTOMATICA'
def encenderFocoAutomatico(valorFoto):
  print ("Nivel de luminosidad: "+str(valorFoto))
  if valorFoto > 600:
    print ("Foco Encendido")
    #GPIO.output(17, 1)
  else:
    print ("Foco Apagado")
    #GPIO.output(17, 0)

#funcion para encender el foco en un lapso de tiempo  
def encenderFocoTiempo(minutos):
  #GPIO.output(17, 1)
  print("Foco encendido")
  time.sleep(minutos)
  print("Foco apagado")  
  peticionServeModificar(1)
  #GPIO.output(17, 0)
  
  
#funcion main del sistema
def main():
  #Configuracion de los puertos GPIO
  #configuracionInicial()
  
  #Consulta BD interna de la Raspberry
  datos = consultaBD()
  i = 0
  for i in datos:
    idR=i[0]
    nombre=i[1]
    firma=i[2]
    hora=i[6]
  certificado = hashlib.md5((firma+str(hora)).encode('utf-8'))
  certificado = certificado.hexdigest()
  mysqldb.close()

  #Peticion al server
  myJson = peticionServe(idR)
  #Valores de la respuesta
  idRecibido = myJson['id']
  encendido = myJson['valor']
  certificadoR = myJson['certificado']
  modo = myJson['modo']
  minutos = myJson['minutos']
  
  #Comparar certificados de las firmas electronicas
  if certificado==certificadoR :
    print ("Certificados iguales")
    #Comparar el modo de ejecucion
    if modo=="MANUAL":
      print("Prender manual")
      encenderFoco(int(encendido))
    elif modo=="AUTOMATICO":
      valorFoto = simularFotorresistencia()
      encenderFocoAutomatico(valorFoto)
    elif modo=="TIEMPO":
      encenderFocoTiempo(int(minutos))
  else:
    print ("Certificados diferentes")

#Hilo principal del sistema
indice = 0
while (indice < 10000):
  #Conexion a la BD
  mysqldb=mysql.connector.connect(host="localhost",user="root",password="",database="raspberryInfo")
  mycursor=mysqldb.cursor()
  t1 = threading.Thread(name = "hilo", target=main)
  t1.start()
  t1.join()
  time.sleep(1)
  print ("Segundos en ejecucion: "+str(indice))
  indice = indice +1 
