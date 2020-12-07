
#Script principal para ejecutar en EC2 - Handler Script

import boto3 
import botocore
import os
import tinys3
import shutil
from pyunpack import Archive
from botocore.client import Config
from getpass import getuser
from progress.bar import Bar, ChargingBar
import datatools as dt
import datetime

ACCESS_KEY_ID = ''
ACCESS_SECRET_KEY = ''
BUCKET_NAME_SWEEPS = 'sweeps-file-zip'
BUCKET_NAME_LOGS = 'databaselogs'
TIME_LIMIT = 50 
JSON_PATH = "/home/ubuntu/server/config_params.json"
USERNAME = getuser() + "/"

process_script = "/home/ubuntu/server/process_script.py"
database_logs = "/home/ubuntu/server/database.py"
file_array = ["" for x in range(TIME_LIMIT)]
logs_txt = "/home/ubuntu/logs/logs-" + '{:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()) + ".txt"

def all_paths():

    data = dt.params_ext(JSON_PATH)
    OS = data["os"]
    mf = dt.params_ext (JSON_PATH, "main_folders")
    SERVER = mf["server"]
    ENV = mf ["entorno"] 
    RDB = mf ["raw_database"]
    p = dt.params_ext(JSON_PATH, "paths")
    SWE = p["sweeps"]
    FREC = mf["frecuencias"]
    HOR = p["horizontal"]
    VER = p["vertical"]
    
    down_path = OS + USERNAME + SERVER + ENV + SWE    #Ruta del archivo que sera descargado desde el bucket SWEEPS de AWS S3
    comp_path = OS + USERNAME + SERVER + RDB #Ruta donde se guardan todos los comprimidos 
    entorno = OS + USERNAME + SERVER + ENV #Ruta del entorno 
    freq = OS + USERNAME + SERVER + FREC
    hor = OS + USERNAME + SERVER + ENV + HOR
    ver = OS + USERNAME + SERVER + ENV + VER
    dblogs = OS + USERNAME + mf["server"] + mf["entorno"]  + p["logs"]
    temp = OS + USERNAME + mf["server"] + mf["entorno"] + p["temp"]
	
    return (down_path, comp_path, entorno, freq, hor, ver, dblogs, temp)

def logs (message, first_time=False):

    if (first_time == True): 
        f= open(logs_txt, "w+")
    else: 
        f=open(logs_txt, "a+")
    
    f.write(message + '\n')
    f.close()


def Configuration (): 
    
    s3 = tinys3.Connection(ACCESS_KEY_ID,ACCESS_SECRET_KEY,BUCKET_NAME_SWEEPS,endpoint='s3-sa-east-1.amazonaws.com')
    print ("[INFO]: Done: Successful connection with Amazon Web Services S3")
    lista = s3.list('')
    x=0
    for fichero in lista:
        file_array [x] = fichero ['key']
        x=x+1

    s3 = boto3.resource (   #A partir de esta línea se utiliza exclusivamente el módulo Boto3
        's3',
        aws_access_key_id = ACCESS_KEY_ID,
        aws_secret_access_key = ACCESS_SECRET_KEY,
        config = Config (signature_version='s3v4'),
    )

    logs ("Configuration OK", True)
    return s3

def Upload_files (s3, dirpath, bucket): #Carga de archivos a un bucket de S3

    os.system ("cd "+ dirpath)
    files = os.listdir (dirpath)
    for i in range (0, len(files)):
        data = open (dirpath + files[i], 'rb')
        s3.Bucket(bucket).put_object(Key= '{:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()) + "/" + files[i], Body=data)
    print ("[INFO]: Done: Successful upload")
    os.system("cd")
    logs ("Upload OK")


def Download_files (s3): #Descarga de los 50 archivos almacenados en un bucket de S3

    bar2 = ChargingBar('[INFO]: Descargando comprimidos de Amazon Web Services S3', max=TIME_LIMIT)
    for i in range (0, TIME_LIMIT):
        try:
            s3.Bucket(BUCKET_NAME_SWEEPS).download_file(file_array[i], down_path + file_array[i])
            #print ("Done")
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("[ERROR]: El objeto no existe en el bucket.")
            else:
                raise
        bar2.next()
    bar2.finish()
    logs ("Download OK")



def Decompress (pathf, cpath): #Descomprime archivos .tar.lzma y luego los mueve de carpeta

    bar2 = ChargingBar('[INFO]: Descomprimiendo los archivos...', max=TIME_LIMIT)
    for i in range (0, TIME_LIMIT):
        name = pathf + file_array[i]
        Archive(name).extractall(pathf)
	    #os.remove (down_path + file_array[i])
        shutil.move(name, cpath + file_array[i])
        bar2.next()
    bar2.finish()
    logs ("Decompress files OK")

def Stack_Builder (dp, ENV, FREC, HOR, VER): 

    print ("[INFO]: Inicializando Stack Builder...")

    extracted_files = dt.files_organizer(dp)
    subpaths = dt.params_ext(JSON_PATH,"subpaths")

    dirs = []
    dirs = {"env":ENV,"sweeps":dp}

    bar2 = ChargingBar('[INFO]: Construyendo stacks...', max=len(extracted_files))
    for file in extracted_files:
        dt.rows_splitter(file,dirs,subpaths,FREC)
        bar2.next()
    bar2.finish()

    mask = dt.params_ext(JSON_PATH,"mask")

    bar2 = ChargingBar('[INFO]: Procesando stacks...', max=len([HOR,VER]))
    for pol in [HOR,VER]:
        dirs = dt.files_organizer(pol)
        for dir_name in dirs:
            subpaths = dt.params_ext(JSON_PATH,"subpaths")
            paths_ = dt.dir_change(subpaths,os.path.join(pol,dir_name))
            csv_name = str(os.listdir(paths_["raw_csv"])[0])
            dt.data_info_split(paths_,csv_name)
            name = str(os.listdir(paths_["proc_info"])[0])
            dt.csv_to_json(os.path.join(paths_["proc_info"],name),paths_["proc_info"])
            raw_data_files = os.listdir(paths_["proc_data"])
            for file in raw_data_files:
                dt.data_masker(os.path.join(FREC,"frecuencias.csv"),os.path.join(paths_["proc_data"],file),paths_["proc_data"],mask)
            paths_ = []
            paths = []
        
        bar2.next()
    bar2.finish()

    print("[INFO]: Stack Builder finalizó su operación correctamente.")
    logs ("Stack builder operation OK")

def delete_operations (SWEEPS, ENV, HOR, VER, DBLOGS, TEMP):
   
    shutil.rmtree(ENV)
    os.mkdir(ENV)

    angles = dt.params_ext(JSON_PATH,"angles")
    azimutals = []
    for ang in angles.values():
        azimutals.append(str(ang))

    dirs = [SWEEPS,HOR,VER,DBLOGS,TEMP]
    subpaths = dt.params_ext(JSON_PATH,"subpaths")
    dt.tree_creator(dirs,azimutals,subpaths.values())
    logs ("Delete and create dirs OK")


if __name__ == "__main__":

    (down_path, comp_path, entorno, freq, hor, ver, dblogs, temp) = all_paths()
    delete_operations(down_path, entorno, hor,ver,dblogs,temp)
    s3 = Configuration ()
    Download_files (s3)
    Decompress (down_path, comp_path)
    Stack_Builder(down_path, entorno, freq, hor, ver)
    os.system ("python3 " + process_script)
    logs ("Processing OK")
    #Llamada al script de la Red Neuronal
    os.system("python3 /home/ubuntu/server/Mask_RCNN/rcnn.py /home/ubuntu/server/config_params.json")
    ##############
    os.system ("python3 " + database_logs)
    logs ("Database OK")
    Upload_files (s3, dblogs, BUCKET_NAME_LOGS)
    delete_operations (down_path, entorno, hor, ver, dblogs, temp)


