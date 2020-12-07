#Carga de archivos

import boto3 
from botocore.client import Config
import os 
import shutil

ACCESS_KEY_ID = ''
ACCESS_SECRET_KEY = ''
BUCKET_NAME = 'sweeps-file-zip' 

path = '/home/pi/RFIMS-CART/uploads/' 
destino = '/usr/local/'
file = os.listdir (path)
shutil.move (path + file[0], destino + file [0])

data = open (file[0], 'rb')

s3 = boto3.resource (
    's3',
    aws_access_key_id = ACCESS_KEY_ID,
    aws_secret_access_key = ACCESS_SECRET_KEY,
    config = Config (signature_version='s3v4'),
)

s3.Bucket(BUCKET_NAME).put_object(Key=file[0], Body=data)
os.remove (file[0])

print ("Done")

