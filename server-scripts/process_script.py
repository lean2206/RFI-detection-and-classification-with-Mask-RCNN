import csv
import numpy as np
import cv2
import getpass
import datatools as dt
import math
import os
import json
from progress.bar import Bar, ChargingBar

USERNAME = getpass.getuser() + "/"
MAXIMO = 20
JSON_PATH = "/home/ubuntu/server/config_params.json"
FREQ_NAME = "frecuencias.csv"
BASE_FILE_NAME = "base.csv"
mins = np.zeros((100, 1), np.float32) # Arreglo que contendrá los mínimos de un .csv
NFILES = 12 # Numero de archivos que son procesados. Para nuestra aplicacion son 12 archivos por día. Este valor puede cambiar.


def all_paths():

	data = dt.params_ext(JSON_PATH)
	OS = data["os"]

	mf = dt.params_ext(JSON_PATH, "main_folders")
	ENV = mf["entorno"]
	SERVER = mf["server"]
	EBASE = mf["base"]
	
	p = dt.params_ext(JSON_PATH, "paths")
	HOR = p["horizontal"]
	VER = p["vertical"]

	s = dt.params_ext(JSON_PATH, "subpaths")
	DATA_PATH = s["proc_data"]  # Archivos listos para convertirse en imagenes
	BASE_PATH = OS + USERNAME + SERVER + EBASE # Ruta de todos los archivos relacionados con el espectro base
	INFO = s["proc_info"]
	PARTS = int(data["windows"])
	TEMP_PATH = OS + USERNAME + SERVER + ENV + p["temp"]
	RFIW_PATH = s["rfi_win"]
	IMG_PROC = s["img"]
	FREQ = OS + USERNAME + SERVER + mf["frecuencias"] + FREQ_NAME

	mk = dt.params_ext(JSON_PATH, "mask")
	mask_keys = list(mk.keys())
	mask_values = list(mk.values())

	return (DATA_PATH, BASE_PATH, PARTS, TEMP_PATH, RFIW_PATH, IMG_PROC, FREQ, mask_keys, mask_values, INFO, ENV, HOR, VER, OS, SERVER)


def file_paths(ops, ent, hor, ver, server):

	# Arreglo que contendrá la ruta de los archivos que serán convertidos en imagenes
	file_array = ["" for x in range(NFILES)]
	for i in range(0, NFILES):  # 12 archivos a procesar 
		if (i < 6):
			ruta = ops + USERNAME + server + ent + hor + str(i*60) + "/"
		else:
			ruta = ops + USERNAME + server + ent + ver + str((i-6)*60) + "/"
		file_array[i] = ruta

	return file_array

def freqs(path):

	with open(path, "r") as f:
		reader = csv.reader(f)
		for i in reader:
			array_freq = i
	size = len(array_freq)
	for i in range(0, size):
		array_freq[i] = float(array_freq[i])
	POINTS = math.trunc((size/100))
	return (array_freq, POINTS)


def comprobation(base_path, points, parts, data, files):

	base = np.genfromtxt(base_path + BASE_FILE_NAME, delimiter=',', usecols=np.arange(0, 55360))
	[fil2, col2] = base.shape

	for i in range(0, 12):  # 12 archivos por día
		archivo = os.listdir(files[i] + data)
		datos = np.genfromtxt(
			files[i] + data + archivo[0], delimiter=',', usecols=np.arange(0, 55360))
		[fil1, col1] = datos.shape
		if (fil1 != fil2) or (col1 < (points*parts)) or (col2 < (points*parts)):
			print ("[ERROR]: Los archivos DATA y/o BASE no tienen un tamaño apropiado")
			exit()


def min(freq, mk, mv):
	for i in range(0, len(mk)):
		if freq <= int(mk[i]):
			minimo = int(mv[i])
			break

	return (minimo)


def img_create(path, freq, y, mk, mv):
	datos = np.genfromtxt(path, delimiter=',')
	[fil, col] = datos.shape
	img = np.zeros((fil, col, 1), np.uint8)

	for i in range(0, fil):  # Mapeo dBm --> pixeles
		for j in range(0, col):
			fr = freq[y]
			y = y + 1
			minimo = min(fr, mk, mv)
			delta = MAXIMO - minimo
			img[i][j] = (datos[i][j] - minimo) * (255/delta)
	y = 0
	return img


def processing(data, parts, points, y, temp, array_freq, mk, mv, img_path, file_array):

	bar2 = ChargingBar('[INFO]: Creando RFI-WINDOWS:', max=NFILES)
	for k in range(0, NFILES):
		archivo = os.listdir(file_array[k] + data)
		datos = np.genfromtxt(file_array[k] + data + archivo[0], delimiter=',', usecols=np.arange(0, 55360))
		[rows, col] = datos.shape
		aux = np.zeros((rows, points), np.float32)
		cut = archivo[0].find(".")
		name = archivo[0]

		for i in range(1, parts+1):
			for j in range(0, points):
				aux[:, j] = datos[:, y]
				y = y + 1
			NAME_FILE = temp + str(name[0:cut]) + "-" + str(i) + ".csv"
			np.savetxt(NAME_FILE, aux, fmt='%3.2f', delimiter=',')
			img_rfi = img_create(NAME_FILE, array_freq, 0, mk, mv)
			cv2.imwrite(file_array[k] + img_path + str(name[0:cut]) + "_win" + str(i) + ".png", img_rfi)
		y = 0
		bar2.next()
	bar2.finish()
	print ("[INFO]: Las Rfi-windows fueron creadas satisfactoriamente.")


def difference(parts, file_array, path_ip, path_rfi, basepath, data):

	bar2 = ChargingBar('[INFO]: Creando Imágenes:', max=NFILES)
	for j in range(0, NFILES):
		archivo = os.listdir(file_array[j] + data)
		cut = archivo[0].find(".")
		name = archivo[0]

		for i in range(1, parts + 1):
			img_rfi = cv2.imread(file_array[j] + path_rfi + str(name[0:cut]) + "_win" + str(i) + ".png")
			img_base = cv2.imread(basepath + "win_" + str(i) + ".png")
			diff_total = cv2.absdiff(img_rfi, img_base)
			# (T,diff_nueva) = cv2.threshold(diff_total, 95, 255, cv2.THRESH_TRUNC)
			cv2.imwrite(file_array[j] + path_ip + str(name[0:cut]) + "_img" + str(i) + ".png", diff_total)
		bar2.next()
	bar2.finish()
	print ("[INFO]: Las Imágenes a clasificar fueron creadas satisfactoriamente.")


if __name__ == "__main__":

	(DATA_PATH, BASE_PATH, PARTS, TEMP_PATH, RFIW_PATH, IMG_PROC, FREQ, mask_keys, mask_values, INFO, ENV, HOR, VER, OS, SERVER) = all_paths()
	file_array = file_paths (OS, ENV, HOR, VER, SERVER)
	(array_freq, POINTS) = freqs (FREQ)
	comprobation (BASE_PATH, POINTS, PARTS, DATA_PATH ,file_array) 
	processing (DATA_PATH, PARTS, POINTS, 0, TEMP_PATH, array_freq, mask_keys, mask_values, RFIW_PATH, file_array)
	difference (PARTS, file_array, IMG_PROC, RFIW_PATH, BASE_PATH, DATA_PATH)

