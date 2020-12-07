import paramiko
import tinys3

ACCESS_KEY_ID = ''
ACCESS_SECRET_KEY = ''
BUCKET_NAME_SWEEPS = 'sweeps-file-zip'
USER = "ubuntu"
HOST = ""
COMM = "python3 /home/ubuntu/main.py"

def lambda_handler(event, context):
        x = bucket_s3 ()
        if x<50:
                print ("In progress...")
        elif x==50: 
                print ("Starting SSH connection with EC2 instance...")
                ssh(USER,HOST,COMM)       
        
def bucket_s3 (): 
        conn = tinys3.Connection(ACCESS_KEY_ID,ACCESS_SECRET_KEY,BUCKET_NAME_SWEEPS,endpoint='s3-sa-east-1.amazonaws.com')
        print ("Done: Successful connection")
        lista = conn.list('')
        x=0
        for fichero in lista:
                print (fichero['key'])
                x=x+1
        print (x)
        return x

def ssh(usuario,hostname,comando,puerto=22):
       
        llave = "keypairtesis.pem"
        key = paramiko.RSAKey.from_private_key_file(llave)
        proxy = None
        conexion = paramiko.SSHClient()
        conexion.load_system_host_keys()
        conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conexion.connect(hostname,puerto,usuario,pkey=key)
        stdin,stdout,stderr = conexion.exec_command(comando)
        print (stdout.read())
        conexion.close()

#NOTAS DE INSTALACION
#Dentro de entorno virtual:
#pip3 install paramiko -t . 
#pip3 install tinys3 -t . --upgrade
