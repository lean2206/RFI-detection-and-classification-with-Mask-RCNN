import csv
import json
import os
import numpy as np
import platform
from getpass import getuser


def name_extractor(file_path):
    sys = platform.system()
    index = 0
    for i in range(len(file_path)-1,0,-1):
        if sys == 'Windows':
            if file_path[i] == '\\':
                index = i + 1
                break
        elif sys == 'Linux':    
            if file_path[i] == '/':  #PARA LINUX
                index = i + 1
                break
    return str(file_path[index:])

def params_ext(config_params_path,field=None):
    with open(config_params_path) as file:
        data = json.load(file)
    
    if field != None:
        return dict(data[field][0])
    else:
        return data

def files_sizer(paths,rows_ref,folder="proc_data"):
    row_dif = []
    data = []
    raw_files = os.listdir(paths[folder])
    #col = np.array((len(raw_files,55361),dtype=int))
    col = []
    names = []

    for i,file in enumerate(raw_files):
        file_f = open(paths[folder] + file, 'r', newline='')
        csv_f = csv.reader(file_f,delimiter=',')
        row_dif.append(sum(1 for row in csv_f) - rows_ref)
        names.append(file)
        file_f.close()
    
    #rows_names = dict(zip(names,row_num))
    #rows_names_minmax = dict((sorted(rows_names.items(),key=operator.itemgetter(1))))

    for i,file in enumerate(names[:-1]):
        if row_dif[i] > 0:
            file_f = open(paths[folder] + file,'r',newline='')
            csv_r = csv.reader(file_f,delimiter=',')
            for row in csv_r:
                data.append(row)
            data2 = iter(data[:len(data) - row_dif[i]])
            data3 = iter(data[len(data) - row_dif[i]:])
            file_f.close()
            os.remove(paths[folder] + file)
            file_f = open(paths[folder] + file,'w',newline='')
            file_f2 = open(paths["residual"] + file[:-4] + "_residual.csv",'w',newline='')
            csv_w = csv.writer(file_f,delimiter=',')
            csv_w2 = csv.writer(file_f2,delimiter=',')
            csv_w.writerows(data2)
            csv_w2.writerows(data3)
            data = []
            data2 = []
            data3 = []
            file_f.close()
            file_f2.close()
        if row_dif[i] < 0:
            aux = abs(row_dif[i])
            try: #para evitar el ultimo archivo
                f = open(paths[folder] + file,'a',newline='')
                f_csv = csv.writer(f,delimiter=',')
                #f_csv.writerow('')
                f2 = open(paths[folder] + names[i+1],'r',newline='')
                f2_csv = csv.reader(f2,delimiter=',')
                first = True
                for ind,x in enumerate(f2_csv):
                    if first and folder=="raw":
                        first = False
                        continue
                    elif first and folder=="proc_data":
                        first = False
                        aux += 1
                    if ind >= aux:
                        break
                    f_csv.writerow(x)
                f.close()
                f2.close()
            except:
                pass
    
""" 
    for i,file in enumerate(raw_files):
        file_f = open(paths[folder] + file, 'r', newline='')
        csv_f = csv.reader(file_f,delimiter=',')
        for row in csv_f:
            col.append(len(row))
        file_f.close()
        min_ = min(col)
        max_ = max(col)
        if (min_ < max_) and (max_ - min_ < 10):
            names.append(file)
    
    for file in names:
        file_f = open(paths[folder] + file, 'r', newline='')
        csv_f = csv.reader(file_f,delimiter=',')
        for row in csv_f:
            data.append(row[:min_])
        file_f.close()
        os.remove(paths[folder] + file)
        file_f = open(paths[folder] + file, 'w', newline='')
        csv_f = csv.writer(file_f,delimiter=',')
        csv_f.writerows(data)
        file_f.close()
"""
 
def data_info_split(paths,file_name,x_limit=3):
    archive_data_path = paths["proc_data"] + file_name
    archive_info_path = paths["proc_info"] + "info_" + file_name
    raw_file_path = paths["raw_csv"] + file_name
    #os.rename(archive_path_data,new_file_name)
    new_file_data = open(archive_data_path,'w',newline='')
    new_file_info = open(archive_info_path,'w',newline='')
    raw_file = open(raw_file_path,'r',newline='')
    writer_data = csv.writer(new_file_data,delimiter=',')
    writer_info = csv.writer(new_file_info,delimiter=',')
    reader = list(csv.reader(raw_file,delimiter=','))

    for line in reader:
        points = len(line)
        writer_data.writerow(line[x_limit:points])
        writer_info.writerow(line[:x_limit])
       
    new_file_data.close()
    new_file_info.close()
    raw_file.close()

def csv_to_json(csv_file_path,json_file_path):
    aux_path = csv_file_path[:-4] + ".txt"
    with open(csv_file_path,'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        first = True
        timestamps = []
        for row in reader:
            timestamps.append(list(row)[0])
            if first:
                angle = row[1]
                pol = row[2]
                first = False
    
    info = {}
    info["angle"] = angle
    info["polarization"] = pol
    info["timestamps"] = []
    
    for inx,log in enumerate(timestamps):
        info["timestamps"].append('\"{0}\" : \"{1}\"'.format(inx + 1,log))
        max_val = inx

    with open(aux_path,'w') as txt_f:
        txt_f.write("{\n\t")
        txt_f.write('\"azimut_angle\" : \"' + str(info["angle"]) + "\",\n\t")
        txt_f.write('\"polarization\" : \"' + str(info["polarization"]) + "\",\n\t")
        txt_f.write('\"timestamps\" : [\n\t\t{\n\t\t\t')
        for inx,log in enumerate(info["timestamps"]):
            if inx < max_val:
                txt_f.write(log + ",\n\t\t\t")
            else:
                txt_f.write(log + "\n\t\t\t")
        txt_f.write("\n")
        txt_f.write("\t\t}\n\t]")
        txt_f.write("\n}")

    name = name_extractor(csv_file_path)
    os.rename(aux_path,json_file_path + name[:-4] + ".json")
    os.remove(csv_file_path)

def data_masker(x_axis_file_path, data_source_path, data_sink_path, mask):
    mask_dbm = []
    mask_frec = []

    for key in mask:
        mask_dbm.append(mask[key])
        mask_frec.append(int(key))
    dbm_threshold = mask_dbm[0]
    frec_threshold = mask_frec[0]
    mask_dbm = iter(mask_dbm)
    mask_frec = iter(mask_frec)

    data = np.genfromtxt(data_source_path,delimiter=',')
    x_axis = np.genfromtxt(x_axis_file_path,delimiter=',')

    (fil_data, col_data) = data.shape
    (col_x,) = x_axis.shape

    if col_data != col_x:
        print("data_masker ERROR: Cantidad de columnas no concuerdan")
        return

    for j in range(0,col_data):
        if x_axis[j] <= frec_threshold:
            for i in range(0,fil_data):
                if data[i][j] < dbm_threshold:
                    data[i][j] = dbm_threshold
        else:
            dbm_threshold = next(mask_dbm)
            frec_threshold = next(mask_frec)
            for i in range(0,fil_data):
                if data[i][j] < dbm_threshold:
                    data[i][j] = dbm_threshold
    
    os.remove(data_source_path)
    file_name = name_extractor(data_source_path)
    np.savetxt(fname=data_sink_path + "masked_" + file_name,X=data,fmt='%3.2f',delimiter=',')

def files_organizer(path_to_listdir,reverse_order=True):
    files = os.listdir(path_to_listdir)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(path_to_listdir,x)),reverse=reverse_order)
    return files

def dir_change(routes_dir,path_to_point):
	routes_keys = routes_dir.keys()
	for keys in routes_keys:
		routes_dir[keys] = os.path.join(path_to_point,routes_dir[keys])
	return routes_dir

def tree_creator(dirs,azimutals,subpaths):
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        if ("horizontal/" in dir_name.lower()) or ("vertical/" in dir_name.lower()):
            for ang in azimutals:
                aux = os.path.join(dir_name,ang)
                if not os.path.exists(aux):
                    os.mkdir(aux)
                    for subpath in subpaths:
                        os.mkdir(os.path.join(aux,subpath))   

def rows_splitter(file,dirs,subpaths,frecuencias,x_limit=3):
    with open(os.path.join(dirs["sweeps"],file),"r") as csv_to_read:
        reader = csv.reader(csv_to_read,delimiter=',')
        first = True
        for row in reader:
            if first:
                frec = row[x_limit:]
                with open(os.path.join(frecuencias,"frecuencias.csv"),"w",newline='') as frec_file:
                    frec_csv = csv.writer(frec_file,delimiter=',')
                    frec_csv.writerow(frec)
                    frec = []
                first = False
                continue
            file_path = os.path.join(dirs["env"],row[2])
            file_path = os.path.join(file_path,str(int(float(row[1]))))
            file_path = os.path.join(file_path,subpaths["raw_csv"])
            file_name = "pos_" + str(int(float(row[1]))) + "_raw.csv"
            file_path = os.path.join(file_path,file_name)
            with open(file_path,"a") as raw_file:
                raw_writer = csv.writer(raw_file,delimiter=',')
                raw_writer.writerow(row)
