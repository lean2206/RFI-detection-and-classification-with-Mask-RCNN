#Todos los valores de frecuencia estan expresados en GHz

####################################
#Formato del archivo csv a procesar
#orig_data[][0] -> y1
#orig_data[][1] -> x1
#orig_data[][2] -> y2
#orig_data[][3] -> x2
#orig_data[][4] -> Class
#orig_data[][5] -> Score
###################################

import csv
import numpy as np
import psycopg2
import datatools as dt
import os
from getpass import getuser
from progress.bar import Bar, ChargingBar

COLDB = 8 #Columnas de la base de datos
DBNAME = "datarfi"
DBUSER = "postgres"
DBPASS = "123456"
JSON_PATH = "/home/ubuntu/server/config_params.json"

def ext_paths (query=0, pol=0, angle=0): #EXTRACTOR DE RUTAS 

	data = dt.params_ext(JSON_PATH)
	OS = data["os"]
	p = dt.params_ext(JSON_PATH, "paths")
	mf = dt.params_ext(JSON_PATH, "main_folders")
	s = dt.params_ext(JSON_PATH, "subpaths")
	dblogs = OS + getuser() + "/" + mf["server"] + mf["entorno"] + p["logs"]
	allfiles = os.listdir(dblogs)

	if allfiles == []: 
		print("[INFO]: No existen interferencias")
		exit()
	if query == 0:
		return (allfiles, dblogs)
	elif query == 1: 
		path = OS + getuser() + "/" + mf["server"] + mf["entorno"] + pol + "/" + str(angle) + "/" + s["proc_info"]
		return (path)
	else: 
		print ("[ERROR]: Ha ocurrido un error con la extracción de rutas.")
		exit()
	
def timestp (pol, angle, y1, y2): 

	path = ext_paths (1, pol, angle)
	file_name_temp = os.listdir (path) 
	if len(file_name_temp) != 1: 
		print ("[ERROR]: Existe más de un archivo en la carpeta " + path)
		exit()
	t = dt.params_ext (path + file_name_temp[0], "timestamps")
	t1 = t[y1]
	t2 = t[y2]

	return (t1,t2)

def getinfo (allfiles, dblogs):

	bar2 = ChargingBar('[INFO]: Almacenando la información de interferencias en la base de datos...', max=len(allfiles))
	for k in range (0, len(allfiles)):
		path = allfiles [k]
		npol = path.find("_")
		pol = path[0:npol]
		newpath = path[npol+1:]
		nangle = newpath.find("_")
		angle = newpath[0:nangle]
		num = int(newpath[nangle+1:newpath.find(".")])
		orig_data = np.genfromtxt(dblogs + path, delimiter=',', dtype=str) #Recordar casteo de enteros
		[rows, cols] = orig_data.shape
		db = np.empty((rows, COLDB), dtype=object)

		for i in range (0, rows): 
			db[i][0] = orig_data [i][4] 													    						#Class
			inicio = (num*553)-553 
			a = (inicio*0.00015) + 0.7
			#b = (inicio * 0.00015) + 0.7
			db[i][1] = pol																								#Polarization
			db[i][2] = int(angle)																						#Angle
			db[i][3] = float(a + ((((int(orig_data[i][3]) - int(orig_data[i][1]))/2)+int(orig_data[i][1]))*0.00015))    #Frecuencia central 
			db[i][4] = float(((int(orig_data[i][3]) - int(orig_data[i][1]))*0.00015)*1000)       								#Ancho de Banda
			(t1, t2) = timestp (pol, angle, orig_data[i][0], orig_data[i][2])
			db[i][5] = t1																								#T1
			db[i][6] = t2											    												#T2
			db[i][7] = float(orig_data[i][5])																			#Score
		
		connectAndWrite (db)
		bar2.next()
	bar2.finish()

def connectAndWrite (db):

	try:
		conn = psycopg2.connect(host="localhost",database=DBNAME, user=DBUSER, password=DBPASS)
		cur = conn.cursor()
	except:
		print("[ERROR]: No es posible conectarse a la base de datos")
		return False
	
	command = "INSERT INTO data(class, polarization, angle, fc, bw, t1, t2, score) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
	[r,c] = db.shape

	for i in range (0,r): 
		datos = (db[i][0], db[i][1], db[i][2], db[i][3], db[i][4], db[i][5], db[i][6], db[i][7])
		cur.execute(command, datos)

	conn.commit()
	conn.close()

if __name__ == "__main__":

	(allfiles, dblogs) = ext_paths()
	getinfo(allfiles, dblogs)

#Hablar de que la tabla de datos de la base de datos puede a llegar a ser excesiva en algun momento y existe la necesidad de eliminar sus registros 
