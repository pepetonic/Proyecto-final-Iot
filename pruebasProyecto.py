#import RPi.GPIO as GPIO
#to use Raspberry Pi board pin numbers
#GPIO.setup(11, GPIO.IN)
#GPIO.setup(12, GPIO.OUT)
#input from pin 11
#input_value = GPIO.input(11)
#output to pin 12
#GPIO.output(12, GPIO.HIGH)
#Firma
#32c0dadb04b99100175afb7be923eef2b0bd0a34db25b25cf23f2565302fb746f6bfe450bdd8852dcec62f33bcf9ace8ffb524770f906e5f916da8021a63db37

import requests
import mysql.connector
import json
import hashlib

#Obtener datos de la BD
mysqldb=mysql.connector.connect(host="localhost",user="root",password="",database="raspberryInfo")
mycursor=mysqldb.cursor()

#Variables Globales
idR=0
nombre=""
firma=""
hora=""
certificado=""

try:
	query = "SELECT * FROM raspberry"	
	#print (query)
	mycursor.execute(query)
	result = mycursor.fetchall()
	for i in result:
		idR=i[0]
		nombre=i[1]
		firma=i[2]
		hora=i[6]
	certificado = hashlib.md5((firma+str(hora)).encode('utf-8'))
	certificado = certificado.hexdigest()
except:
	print("Error en la consulta")

mysqldb.close()

#peticion al servidor
url='http://192.168.0.22/ServidorWebRasp/index.php/?idr='+str(idR)
resp = requests.get(url)
myJson = resp.json()
#Valores de la respuesta
idRecibido = myJson['id']
encendido = myJson['valor']
certificadoR = myJson['certificado']
#Comparar certificados de las firmas electronicas

if certificado==certificadoR :
	print ("iguales")
else:
	print ("Diernetes")
