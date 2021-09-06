from glob import glob

import global_value as g

import numpy as np
import random
import os
import copy
import subprocess
import shutil
import codecs
import re
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import json
import pprint
import sys
import glob

def change_param_volt(opamp_path_circuit,path_result_res,path_result_block,line_num):
    result_res = {}
    with open(path_result_res,mode = "r") as fr:
        result_res = json.load(fr)

    result_block = {}
    with open(path_result_block,mode = "r") as fb:
        result_block = json.load(fb)

    #テンプレのネットリスト（元ファイル）
    #file_path_circuit_template = g.os_path + "/netlist/test4.net"
   
    #書き換え後のネットリスト（spiceの入力ファイル）
    #file_path_circuit_temp = r"C:\Users\jpa55\spice\test4_temp.net"

    with codecs.open(g.opamp_path_circuit, "r", "Shift-JIS", "ignore") as file:
        s = file.read()
    lines = s.split("\n")
    #netlist変更
    #print(lines)

    for i in range(len(lines)):
        lines[i] = lines[i].split()

    node_list = list()
    res_value_list = list()
    for num in range(line_num):
    
        for i,line in enumerate(lines):
            if "R"+str(num+1) in line:
                change_point = i
                name = "R"+str(num+1).zfill(3)+"_s"

                start_node = lines[i][2]
                next_node = "n"+str(num+1).zfill(3)+"_s"

                goal_node = lines[i][1]
                lines[change_point] = [name,next_node,start_node,'rsg']

                #pprint.pprint(result_block)
                
                for node in range(len(result_block[str(num+1)])):

                    change_point += 1

                    name = "R"+str(num+1).zfill(3)+"_"+str(node+1)
                    value = "r_n"+str(num+1).zfill(3)+"_"+str(node+1)
                    
                    start_node = next_node
                    next_node = "n"+str(num+1).zfill(3)+"_"+str(node+1)
                    lines.insert(change_point,[name,next_node,start_node,value])

                    node_list.append(next_node)

                    res_value_list.append(value)

                change_point += 1
                name = "R"+str(num+1).zfill(3)+"_g"
                lines.insert(change_point,[name,goal_node,next_node,'rsg'])

    #分岐ブロックを追加
    for key in result_block.keys():
        if "b" in key:
            #print(key)
            bunki_node = "b" + key.split("b")[1].zfill(3)
            #print(bunki_node)
            node_list.append(bunki_node)

    #グラウンドを追加
    node_list.append("0")

    #pprint.pprint(node_list)

    for i,line in enumerate(lines):
        if "add_param" in line:

            change_point_param = i
            for value in res_value_list:
                temp = value
                if temp not in result_res:
                    continue
                change_point_param += 1

                lines.insert(change_point_param,[".param",temp,"=",str(result_res[temp])])
            
    with open(g.file_path_circuit+".net", "w") as f:
        for line in lines:
            for word in line:
                f.write(word)
                f.write(" ")
            f.write("\n")

def meas_volt(evaluate_path):
    print(evaluate_path)
    print(str(g.port))
    cmd = ["hspice","-CC",evaluate_path+".net","-port",str(g.port),"-o","out"]
    
    #print(cmd)
    try:
        res = subprocess.check_call(cmd)
    except:
        print("cmd error in hspice")
        sys.exit()

    path_volt = "out.lis"

    node_volt = {}
    with open(path_volt,"r") as f:
        s = f.read()
    lines = s.split("\n")
    if os.path.exists(path_volt):
        for i,line in enumerate(lines):
            #line = line.split()
            if "operating" in line:
                point = i+4
                point2 = point + 1
                
                for j in range(point,len(lines),1):
                    if len(lines[j]) == 0:
                        break
                    words = re.split('[|(|)|,|]| |\r|=|:',lines[j])
                    lines[j] = [x for x in words if x]
                    for w in range(0,len(lines[j]),3):
                        node_volt[lines[j][w+1]] = float(lines[j][w+2])  
                break

        return node_volt
        """
        path_volt = evaluate_path+".ic*"

        node_volt = {}

        #結果取り出し
        if os.path.exists(path_volt):
            
            with open(path_volt,"r") as f:
                s = f.read()
            lines = s.split("\n")

        
            end_flag = 0
            for row,line in enumerate(lines):
                if '.nodeset' in line:
                    for search_row in range(row+6,len(lines)-1,1):
                        if 'END:' in lines[search_row]:
                            end_flag = 1
                            break
                        words = re.split('[|(|)|,|]| |\r|=',lines[search_row])
                        lines[search_row] = [x for x in words if x]
                        node_volt[lines[search_row][1].split("x1.")[1]] = float(lines[search_row][2])
                if end_flag == 1:
                    break   

            return node_volt
        """

    else:
        print("cannot measure volt")
        sys.exit()

def change_param(opamp_path_circuit,path_result_res,path_result_cap,path_result_block,line_num):
    
    result_res = {}
    with open(path_result_res,mode = "r") as fr:
        result_res = json.load(fr)

    result_cap = {}
    with open(path_result_cap,mode = "r") as fc:
        result_cap = json.load(fc)

    result_block = {}
    with open(path_result_block,mode = "r") as fb:
        result_block = json.load(fb)

    #テンプレのネットリスト（元ファイル）
    #file_path_circuit_template = g.os_path + "/netlist/test4.net"
    file_path_circuit_template = g.opamp_path_circuit
    #書き換え後のネットリスト（spiceの入力ファイル）
    #file_path_circuit_temp = r"C:\Users\jpa55\spice\test4_temp.net"

    with codecs.open(file_path_circuit_template, "r", "Shift-JIS", "ignore") as file:
        s = file.read()
    lines = s.split("\n")
    #netlist変更
    #print(lines)

    for i in range(len(lines)):
        lines[i] = lines[i].split()

    node_list = list()
    res_value_list = list()
    for num in range(line_num):
    
        for i,line in enumerate(lines):
            if "R"+str(num+1) in line:
                change_point = i
                name = "R"+str(num+1).zfill(3)+"_s"

                start_node = lines[i][2]
                next_node = "n"+str(num+1).zfill(3)+"_s"

                goal_node = lines[i][1]
                lines[change_point] = [name,next_node,start_node,'rsg']

                #pprint.pprint(result_block)
                
                for node in range(len(result_block[str(num+1)])):

                    change_point += 1

                    name = "R"+str(num+1).zfill(3)+"_"+str(node+1)
                    value = "r_n"+str(num+1).zfill(3)+"_"+str(node+1)
                    
                    start_node = next_node
                    next_node = "n"+str(num+1).zfill(3)+"_"+str(node+1)
                    lines.insert(change_point,[name,next_node,start_node,value])

                    node_list.append(next_node)

                    res_value_list.append(value)

                change_point += 1
                name = "R"+str(num+1).zfill(3)+"_g"
                lines.insert(change_point,[name,goal_node,next_node,'rsg'])

    #分岐ブロックを追加
    for key in result_block.keys():
        if "b" in key:
            #print(key)
            bunki_node = "b" + key.split("b")[1].zfill(3)
            #print(bunki_node)
            node_list.append(bunki_node)

    #グラウンドを追加
    node_list.append("0")

    #pprint.pprint(node_list)

    cap_value_list = list()

    node_comb = list(itertools.combinations(node_list,2))
    
    for n1,n2 in node_comb:
        
        if n1 == "0":
            temp = "c_"+n2+"_"+n1
        elif n2 == "0":
            temp = "c_"+n1+"_"+n2

        elif n1 > n2:
            temp = "c_"+n2+"_"+n1
        else:
            temp = "c_"+n1+"_"+n2

        #name = "C_"+n1+"_"+n2
        if temp not in result_cap:
            continue

        name = temp.capitalize()
        value = temp
        change_point += 1
        lines.insert(change_point,[name,n2,n1,value])
        cap_value_list.append(value)

    #pprint.pprint(result_cap)

    for i,line in enumerate(lines):
        if "add_param" in line:

            change_point_param = i
            for value in res_value_list:
                temp = value
                if temp not in result_res:
                    continue
                change_point_param += 1

                lines.insert(change_point_param,[".param",temp,"=",str(result_res[temp])])
            
            for value in cap_value_list:
                temp = value
                if temp not in result_cap:
                    continue
                change_point_param += 1

                cap = "{:.25f}".format(result_cap[temp])
                lines.insert(change_point_param,[".param",temp,"=",cap])
        
            break

    with open(opamp_path_circuit+".net", "w") as f:
        for line in lines:
            for word in line:
                f.write(word)
                f.write(" ")
            f.write("\n")

def exe_netlist(evaluate_path,evo):

    cmd = ["hspice","-CC",evaluate_path+".net","-port",str(g.port),"-o","out"]
    #print(cmd)
    try:
        res = subprocess.check_call(cmd)
    except:
        print("cmd error in hspice")
        sys.exit()

    if evo == "ac":
        path_glob = "out.ma*"
    elif evo == "dc":
        path_glob = "out.ms*"
    elif evo == "tran":
        path_glob = "out.mt*"
    else:
        if evo == "out_noise":
            out_path = os.getcwd()+"/out.lis"
            if os.path.exists(out_path):
                ans = 0
                with open(out_path) as f:
                    s = f.read()
                lines = s.split("\n")
                flag = 0
                for i in range(len(lines)-1,0,-1):
                    if len(lines[i]) == 0:
                        continue
                    a = lines[i].split()
                    if "v/hz" in a:
                        words = re.split('[|(|)|,|]| |\r|=',lines[i])
                        words = [x for x in words if x]
                        for word in words:
                            try:
                                ans = float(word)
                                #print(ans)
                                flag = 1
                                break
                            except ValueError:
                                pass
                        if flag == 1:
                            break

                #os.remove(out_path)
                name = "noise"
                return ans,name
            else:
                #sys.exit()
                return -1,"noise"

        elif evo =="out_rout":
            out_path = os.getcwd()+"/out.lis"
            if os.path.exists(out_path):
                with open(out_path) as f:
                    s = f.read()
                lines = s.split("\n")

                name_list = []
                value_list = []
                for i in range(len(lines)-1,0,-1):
                    if len(lines[i]) == 0:
                        continue
                    a = lines[i].split()
                    if "small-signal" in a:
                        words = re.split('[|(|)|,|]| |\r|=',lines[i])
                        words = [x for x in words if x]
                        for j in range(i+3,i+5,1):
                            words = re.split('[|(|)|,|]| |\r|=',lines[j])
                            words = [x for x in words if x]
                            name_list.append(words[0])
                            
                            for word in words:
                                try:
                                    ans = float(word)
                                    value_list.append(ans)
                                    break
                                except ValueError:
                                    pass
                        break
                os.remove(out_path)
                return value_list,name_list
            else:
                #sys.exit()
                return [-1]*2,["input","output"]
    ans = []

    for out_path in glob.glob(path_glob):

        #結果取り出し
        if os.path.exists(out_path):
            
            with open(out_path,"r") as f:
                s = f.read()
            lines = s.split("\n")
            name_list = []
            value_list = []
            for row,line in enumerate(lines):
                #words = re.split('[|(|)|,|]| |\r|=',line)
                #lines[row] = [x for x in words if x]
                if ".TITLE" in lines[row]:
                    
                    for search_row in range(row+1,len(lines),1):
                        words = re.split('[|(|)|,|]| |\r|=',lines[search_row])
                        lines[search_row] = [x for x in words if x]
                        for word in lines[search_row]:
                            try:
                                value_list.append(float(word))
                            except ValueError:
                                name_list.append(word)
                    break
            new_value_list = []
            for i in range(0,len(value_list),len(name_list)):
                temp = value_list[i:i+len(name_list)]
                new_value_list.append(temp)
            

            ans[len(ans):len(ans)] = new_value_list

            os.remove(out_path)

        else:
            print("out_path is not found!")
            
            sys.exit()

    return ans,name_list




"""
if __name__ == "__main__":
    
    

    g.dcgain_path = g.os_path+"/opamp_netlist/dcgain"
    g.pdis_path = g.os_path+"/opamp_netlist/pdis"
    g.cmmr_path = g.os_path+"/opamp_netlist/cmmr"
    g.common_mode_path = g.os_path+"/opamp_netlist/common_mode"
    g.noise_path = g.os_path+"/opamp_netlist/noise"
    g.out_range_path = g.os_path+"/opamp_netlist/out_range"
    g.psrr_path = g.os_path+"/opamp_netlist/psrr"
    g.rout_path = g.os_path+"/opamp_netlist/rout"
    g.slewrate_path = g.os_path+"/opamp_netlist/slewrate"
    g.thd_path = g.os_path+"/opamp_netlist/thd"

    g.out_hspice_path = g.os_path+"opamp_netlist/out.out"

    g.path_circuit = g.os_path + "/opamp_netlist/opamp_temp.net"
    g.file_path_circuit = g.os_path + "/opamp_netlist/opamp"

    line_num = 17
    max_exe_num = 1

    for exe_num in range(max_exe_num):
            
        path_result_res = g.os_path + "/result_res/"+str(exe_num)+".json"
        path_result_cap = g.os_path + "/result_cap/"+str(exe_num)+".json"
        path_result_block = g.os_path + "/output/out_"+str(exe_num)+"/block_poly.json"

        change_param(g.file_path_circuit,path_result_res,path_result_cap,path_result_block,line_num)

        ans1 = exe_netlist(g.dcgain_path)

        print(ans1)

        ans2 = exe_netlist(g.pdis_path)

        print(ans2)
"""


    