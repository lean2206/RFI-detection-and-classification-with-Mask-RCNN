import os
import shutil

ACCESS_KEY_ID = ''
ACCESS_SECRET_KEY = ''
BUCKET_NAME = "initial-setup"

def S3Configuration (): 
    #Esta función se encarga de descargar los archivos de Amazon S3
    
    import boto3 
    import botocore
    import tinys3
    from botocore.client import Config

    s3 = boto3.resource ('s3',aws_access_key_id = ACCESS_KEY_ID,aws_secret_access_key = ACCESS_SECRET_KEY,config = Config (signature_version='s3v4'),)
    my_bucket = s3.Bucket(BUCKET_NAME)
    for s3_object in my_bucket.objects.all():
        # Los archivos son descargados en el directorio actual
        path, filename = os.path.split(s3_object.key)
        my_bucket.download_file(s3_object.key, filename)
    
    os.system("sudo mv /home/ubuntu/datatools.py /usr/lib/python3/dist-packages/") 

def TreeCreator():
    #Esta función crea todos los directorios necesarios para la instancia 

    from getpass import getuser
    import datatools as dt
    import zipfile 

    json_path = "config_params.json"
    angles = dt.params_ext(json_path,"angles")
    azimutals = []
    for ang in angles.values():
        azimutals.append(str(ang))

    SERVER = os.path.join(dt.params_ext(json_path)["os"],getuser(),dt.params_ext (json_path, "main_folders")["server"])
    ENTORNO = os.path.join(SERVER,dt.params_ext(json_path, "main_folders")["entorno"])
    SWEEPS = os.path.join(ENTORNO,dt.params_ext(json_path, "paths")["sweeps"])
    HOR = os.path.join(ENTORNO,dt.params_ext(json_path, "paths")["horizontal"])
    VER = os.path.join(ENTORNO,dt.params_ext(json_path, "paths")["vertical"])
    DBLOGS = os.path.join(ENTORNO,dt.params_ext(json_path, "paths")["logs"])
    TEMP = os.path.join(ENTORNO,dt.params_ext(json_path, "paths")["temp"])
    RAWDB = os.path.join(SERVER,dt.params_ext(json_path, "main_folders")["raw_database"])
    BASE = os.path.join(SERVER,dt.params_ext(json_path, "main_folders")["base"])
    FREQ = os.path.join(SERVER,dt.params_ext(json_path, "main_folders")["frecuencias"])
    dirs = [SERVER,ENTORNO,SWEEPS,HOR,VER,DBLOGS,TEMP,RAWDB,BASE,FREQ] #Faltan carpetas que necesitan crearse (rever)
    subpaths = dt.params_ext(json_path,"subpaths")
    dt.tree_creator(dirs,azimutals,subpaths.values())
    os.mkdir("/home/ubuntu/logs/")
    
    """
    shutil.move("process_script.py",SERVER)
    shutil.move("database.py",SERVER)
    shutil.move(json_path,SERVER)
    shutil.move("frecuencias.csv",FREQ)
    """
    os.system ("sudo mv /home/ubuntu/process_script.py /home/ubuntu/server/process_script.py")
    os.system ("sudo mv /home/ubuntu/database.py /home/ubuntu/server/database.py")
    os.system ("sudo mv /home/ubuntu/config_params.json /home/ubuntu/server/config_params.json")
    os.system ("sudo mv /home/ubuntu/frecuencias.csv /home/ubuntu/server/x_axis/frecuencias.csv")


    zf=zipfile.ZipFile("base.zip", "r")
    for i in zf.namelist():
        zf.extract(i, path=BASE)

    #os.remove("base.zip")
    os.system("sudo rm base.zip")

def Grafana (): 

    os.system ("sudo apt-get install -y adduser libfontconfig1")
    os.system ("wget https://dl.grafana.com/oss/release/grafana_6.7.2_amd64.deb")
    os.system ("sudo dpkg -i grafana_6.7.2_amd64.deb")
    os.system ("sudo service grafana-server start")
    #Install plugin piechart 
    os.system ("sudo grafana-cli plugins install grafana-piechart-panel")
    os.system ("sudo service grafana-server restart")

def RCNN():

    os.system ("sudo mv /home/ubuntu/Mask_RCNN /home/ubuntu/server/")
    os.system ("cd /home/ubuntu/server/")
    os.system ("unzip Mask_RCNN.zip")
    os.system ("rm Mask_RCNN.zip")
    os.system ("cd Mask_RCNN/")
    os.system ("pip3 install -r requirements.txt")
    os.system ("sudo python3 setup.py install")


if __name__ == "__main__":
    
    S3Configuration()
    TreeCreator()
    Grafana()
    #RCNN()
