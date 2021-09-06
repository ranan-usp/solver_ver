from glob import glob

from hspice import *

import collections
import pprint
import os
import matplotlib.pyplot as plt
import numpy as np
import random
import pprint
import subprocess
import sys
import re
import json


#raphael用の入力ファイル作り
#BLOCK hitotugoto
def make_poly3D(p_list,exe_num,new_path_list):

    flag_raphael = 1

    rho_al = 2.65e-8
    rho_cu = 1.68e-8
    line_width = 2e-6
    t1 = 0.1e-6
    t2 = 0.36e-6
    t3 = t2
    t4 = 0.845e-6
    block_size = 10e-6

    rho = rho_al

    x_list = ["0","blockx/2-w/2","blockx/2+w/2","blockx"]
    y_list = ["0","blocky/2-w/2","blocky/2+w/2","blocky"]

    path_cir = g.os_path + "/output/out_"+str(exe_num)+"/circuit.txt"

    with open(path_cir,"w") as f:
        for circuit_z in p_list:
            f.write("\n")
            for circuit_y in circuit_z:
                for circuit_x in circuit_y:
                    f.write(circuit_x)
                    f.write(" ")
                f.write("\n")

    #volt_list = [0.922,0.922,0.922,0.922,0.922,1.8,0.822,0.822,0.822,0,0.822,0.822]
    
    block_list = {"ru":[(1,0),(2,0),(2,1),(3,1),(3,2),(1,2)],
                "lu":[(1,0),(2,0),(2,2),(0,2),(0,1),(1,1)],
                "lt":[(0,1),(0,2),(1,2),(1,3),(2,3),(2,1)],
                "rt":[(1,1),(3,1),(3,2),(2,2),(2,3),(1,3)],

                "lr":[(0,1),(0,2),(3,2),(3,1)],
                "ut":[(1,0),(2,0),(2,3),(1,3)],

                "tr":[(0,1),(0,2),(1,2),(1,3),(2,3),(2,0),(1,0),(1,1)],
                "tl":[(1,0),(2,0),(2,1),(3,1),(3,2),(2,2),(2,3),(1,3)],
                "tu":[(0,1),(3,1),(3,2),(2,2),(2,3),(1,3),(1,2),(0,2)],
                "tt":[(0,1),(0,2),(3,2),(3,1),(2,1),(2,0),(1,0),(1,1)],

                "r0":[(1,1),(1,2),(3,2),(3,1)],
                "l0":[(0,1),(0,2),(2,2),(2,1)],
                "t0":[(1,1),(1,3),(2,3),(2,1)],
                "u0":[(1,0),(2,0),(2,2),(1,2)],
                
                "t_up_lr":[(0,1),(0,2),(3,2),(3,1)],
                "t_under_lr":[(0,1),(0,2),(3,2),(3,1)],
                "t_up_ut":[(1,0),(2,0),(2,3),(1,3)],
                "t_under_ut":[(1,0),(2,0),(2,3),(1,3)],
                
                "uu":[(1,1),(1,2),(2,2),(2,1)]}
    

    line_pos_list = dict()

    block_num_y = 10
    block_num_x = 10
    block_pos_x = 3
    block_pos_y = 3
    line_num = 20

    block_count = 0

    #with open(out_path,"w") as f:
    for num_z,p_list_z in enumerate(p_list):
        
        new_p_list = list(reversed(p_list_z))
        
        for num_y,p_list_x in enumerate(new_p_list):

            for num_x,p in enumerate(p_list_x):
                #temp = dict()
                #何番の配線か？　どのブロックか？
                block_count += 1

                if "," in p:
                    p_path,p_block = p.split(",")
                    #区別の仕方考えるべき（001,002）
                    #分岐ブロック
                    """
                    if len(p_path) == 3:
                        p_path = 0
                        p_block = p_block
                    #配線ブロック
                    else:
                        p_path = p_path
                        p_block = p_block
                    """
                
                #配線ブロックではないため，都バス
                #素子ブロックか、なにもないか
                else:
                    continue
                
                temp_block = list()
                for px,py in block_list[p_block]:
                    
                    temp_block.append((px+block_pos_x*num_x,py+block_pos_y*num_y))
                            
                key = p_path
                #temp[str((num_x,num_y,num_z))] = temp_block
                temp = [temp_block,(num_x,num_y,num_z)]
                try: 
                    line_pos_list[key].append(temp)
                except KeyError:
                    line_pos_list[key]= [temp]
    #print("line_pos_list")
    


    block_num_dict = dict()
    for key,value in line_pos_list.items():
        if "b" in key:
            block_num_dict[key] = value
    
    for i,path in enumerate(new_path_list):
        path_temp = list()
        for j,p in enumerate(path[1:len(path)-1]):
            for k in range(len(line_pos_list[str(i+1)])):
                
                if (p[0],len(new_p_list)-p[1]-1,p[2]) == line_pos_list[str(i+1)][k][1]:
                    path_temp.append(line_pos_list[str(i+1)][k])
                    break
                    
        block_num_dict[str(i+1)] = path_temp
    
    #print("block_num_dict")
    #pprint.pprint(block_num_dict)

    #raphael script                
    line_block_dict = dict()
    #line_block_dict_all = list()
    for key,value in block_num_dict.items():
        temp2 = list()
        for block in value:
            temp1 = list()
            for pos in block[0]:
                #if out_count == 1:
                    #print(pos)
                    #temp_graph.append([pos[0],pos[1]])

                x_temp = divmod(pos[0],block_pos_x)
                y_temp = divmod(pos[1],block_pos_y)
                #余り
                
                x = x_list[x_temp[1]] + "+blockx*" + str(x_temp[0])
                y = y_list[y_temp[1]] + "+blocky*" + str(y_temp[0])

                temp1.append((x,y))
            if key != "0":
                temp2.append([temp1,block[1]])
            else:
                ################
                temp2.append([temp1,block[1]])

        line_block_dict[key] = temp2


    #raphael用のブロック情報
    path_result_block = g.os_path + "/output/out_"+str(exe_num)+"/block_poly.json"

    with open(path_result_block,"w") as f:
        temp = json.dumps(line_block_dict)
        f.write(temp)
    
    
    #抵抗情報　統一するか　分けるか
    #blockごとの抵抗save
    
    spice_res = {}
    for key,values in line_block_dict.items():
        
        for num in range(len(values)):

            z = values[num][1][2]+1
            t = 0
            if z == 1:
                t = t1
            elif z == 2:
                t = t2
            else:
                t = t3
            
            if "b" in key:
                name = "r" + key
                spice_res[name] = (rho*block_size/(t*line_width))/2
            else:
                name = "r_n" +key.zfill(3)+ "_" + str(num+1)
                spice_res[name] = rho*block_size/(t*line_width)


    path_result_res = g.os_path + "/result_res/"+str(exe_num)+".json"

    with open(path_result_res,"w") as f:
        spice_res = json.dumps(spice_res)
        f.write(spice_res)

    #########################################################################
    #ブロックごとにかかる電圧を測定して，保存

    change_param_volt(g.opamp_path_circuit,path_result_res,path_result_block,line_num)
    block_volt_list = meas_volt(g.dcgain_path)
    
    path_result_block_volt = g.os_path + "/result_block_volt/"+str(exe_num)+".json"

    with open(path_result_block_volt,"w") as f:
        temp = json.dumps(block_volt_list)
        f.write(temp)
    #########################################################################

    """
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)


    colorlist = ["r", "g", "b", "c", "m", "y", "k", "w"]
    for i,temp in enumerate(graph2d):
        x,y = zip(*temp)
        color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])]
        ax.scatter(x,y,c=color)
        #ax.scatter(x,y,c=colorlist[(len(colorlist)-1)%(i+1)])
    fig.savefig("img.png")
    """

    """
    path_out_dir = "./structure/structure"+str(exe_num)
    if not os.path.exists(path_out_dir):
        os.mkdir(path_out_dir)
    """

    #template_path = os_path + "structure/poly3D_template_"+str(n+1)+".txt"
    #for i in range(2):
    insert_line = 32

    


    if flag_raphael == 0:
        template_path = g.os_path + "/structure/poly3D_template.txt"

    else:
        template_path = g.os_path + "/structure/poly3D_template10.txt"


    with open(template_path,"r") as f:
        s = f.read()
    data = s.split("\n")

    for key,line_block in line_block_dict.items():

        for num,block in enumerate(line_block):

            height = str(block[1][2]+1)

            """
            if "b" not in key:
                    
                data.insert(insert_line,"POLY3D name=m"+key+"_"+str(num+1)+"; volt="+str(volt_list[int(key)-1])+";")
            else:

                #分岐ブロックの電圧不明
                volt = key.split("b")[1]
                data.insert(insert_line,"POLY3D name=m"+key+"; volt="+str(volt_list[int(volt)-1])+";")
            """
        
            if "b" not in key:
                
                data.insert(insert_line,"POLY3D name=m"+key+"_"+str(num+1)+"; volt="+str(block_volt_list["n"+key.zfill(3)+"_"+str(num+1)])+";")
            else:

                #分岐ブロックの電圧不明
                b_num = key.split("b")[1]
                data.insert(insert_line,"POLY3D name=m"+key+"; volt="+str(block_volt_list["b"+b_num.zfill(3)])+";")
                
            insert_line += 1
            temp = "coord="
            for pos in block[0]:
                if flag_raphael == 0:
                    temp += pos[0]+","+pos[1]+";"
                else:
                    temp += "defaultx+"+pos[0]+",defaulty+"+pos[1]+";"
            data.insert(insert_line,temp)
            insert_line += 1

            if flag_raphael == 0:
                data.insert(insert_line,"v1 = 0, 0, gndthicks+h"+height+";")
                insert_line += 1
                data.insert(insert_line,"v2 = 0, 0, gndthicks+h"+height+"+t"+height+";")
            else:
                data.insert(insert_line,"v1 = 0, 0, defaultz+gndthicks+h"+height+";")
                insert_line += 1
                data.insert(insert_line,"v2 = 0, 0, defaultz+gndthicks+h"+height+"+t"+height+";")

            insert_line += 1
            data.insert(insert_line,"perp = 0.0, 1.0, 0.0;")
            insert_line += 1


        #out_path = os_path + "structure/structure"+str(exe_num)+"/inter-layer"+str(exe_num)+"-"+str(n)+".txt"
        out_path = g.os_path + "/structure/"+str(exe_num)+".txt"

        #元のファイルに書き込み
        with open(out_path, mode='w')as f:
            for da in data:
                f.write(da)
                f.write('\n')
    
def execute_raphael(num,line_num):
    
    #for l in range(layer):
    #path_in_raphael = g.os_path + "/structure/"+str(num)+"_"+str(i)+".txt"
    path_glob = g.os_path + "/structure/"+str(num)+"_*.txt"
    spice_cap = dict()
    path_result_cap = g.os_path + "/result_cap/"+str(num)+".json"
    h = 0
    
    for in_path in glob.glob(path_glob):
        print(in_path)
        
        path_in_raphael = in_path
        cmd1 = "raphael"
        cmd2 = "rc3"
        cmd3 = "-b"
        cmd4 = '""'

        cmd = [cmd1,cmd2,cmd3,cmd4,path_in_raphael]
        #print(cmd)
        try:
            res = subprocess.check_call(cmd)
        except:
            print("cmd error in raphael")
            sys.exit()

        #path_out_raphael = g.os_path + "/"+str(num)+"_"+str(i)+".txt.out"
        path_out_raphael = g.os_path + "/"+str(num)+"_"+str(h)+".txt.out"
        h += 1
        #path_result_cap = g.os_path + "/result_cap/"+str(num)+"_"+str(i)+".json"
        

        with open(path_out_raphael,"r") as f:
            s = f.read()
        lines = s.split("\n")
        
        flag = lines.index(" ==> SPICE Models for Entire Capacitance Matrix (in Farad)")

        for index in range(flag+2,len(lines),1):
            lines[index] = lines[index].split(" ")

            #linux windows 0 1
            if len(lines[index]) == 1:
                break

            temp1 = re.split("[m|_|.]",lines[index][2])

            if temp1 == ["grnd"]:
                continue

            if "b" in temp1[1]:
                bunki_num = temp1[1].split("b")[1]
                n1 = "b"+str(int(bunki_num)).zfill(3)
            else:
                n1 = "n" + str(int(temp1[1])).zfill(3) + "_" + temp1[2]
            
            if lines[index][3] == "GROUND_RC3":
                n2 = "0"
            else:
                temp2 = re.split("[m|_|.]",lines[index][3])
                if "b" in temp2[1]:
                    bunki_num = temp2[1].split("b")[1]
                    n2 = "b"+str(int(bunki_num)).zfill(3)
                else:
                    n2 = "n" + str(int(temp2[1])).zfill(3) + "_" + temp2[2]

            if n1 == n2:
                continue

            elif n1 == "0":
                name = "c_"+n2+"_"+n1
            elif n2 == "0":
                name = "c_"+n1+"_"+n2

            elif n1 > n2:
                name = "c_"+n2+"_"+n1
            else:
                name = "c_"+n1+"_"+n2
            
            spice_cap[name] = float(lines[index][4])
        
        if os.path.exists(path_out_raphael):
            os.remove(path_out_raphael)
        
    with open(path_result_cap,"w") as f:
        spice_cap = json.dumps(spice_cap)
        f.write(spice_cap)

    for in_path in glob.glob(path_glob):
        if os.path.exists(in_path):
            os.remove(in_path)

#テスト用
if __name__ == "__main__":

    line_num = 17
    
    max_exe_num = 5
    for exe_num in range(max_exe_num):
        #for i in range(2):
        """
        execute_raphael(exe_num,i,line_num)
        if os.path.exists(g.os_path + "/"+str(exe_num)+"_"+str(i)+".txt.out"):   
            os.remove(g.os_path + "/"+str(exe_num)+"_"+str(i)+".txt.out")
        """
        
        execute_raphael(exe_num,line_num)
        if os.path.exists(g.os_path + "/"+str(exe_num)+".txt.out"):   
            os.remove(g.os_path + "/"+str(exe_num)+".txt.out")


