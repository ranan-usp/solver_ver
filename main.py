
import random
import numpy as np
import pandas as pd
import os
import pprint
import json
import sys
import re

import global_value as g
from implementation_temp import *
from raphael_poly3D_temp import execute_raphael
from hspice import *
from wiring import Wiring
from block import Block

def read_input(input_file):
    #入力ファイル読み込み
    with open(input_file,"r") as f:
        s = f.read()
    lines = s.split("\n")

    block_info = list()

    circuit_block = 0
    #情報読み込み（試行回数分繰り返す必要はないかも，改善の余地あり）
    for num,line in enumerate(lines):
        line = re.split("\s|X|,",line)
        
        if "SIZE" in line:
            width_x = int(line[1])
            width_y = int(line[2])
            height = int(line[3])
        
        if "BLOCK_NUM" in line:
            block_num = int(line[1])
        
        if "LINE_NUM" in line:
            line_num = int(line[1])

        #BLOCK情報読み込み
        if re.match("BLOCK#.+",line[0]):

            #BLOCKのサイズ
            block_size_x = int(line[1])
            block_size_y = int(line[2])
            block_type = line[3]

            if block_type == "b" or block_type == "c":
                circuit_block += 1

            #BLOCKを一次元配列化->num_list
            num_list = list()
            for i in range(block_size_y):
                num_list[len(num_list):len(num_list)] = lines[num+1+i].split(",")

            block_info.append([block_type,[block_size_x,block_size_y],num_list])

    banmen = [width_x,width_y,height]


    return banmen,block_num,circuit_block,line_num,block_info

def exe_hspice(exe_num,line_num,banmen,line_width):
    path_result_res = g.os_path + "/result_res/"+str(exe_num)+".json"
    path_result_cap = g.os_path + "/result_cap/"+str(exe_num)+".json"
    path_result_block = g.os_path + "/output/out_"+str(exe_num)+"/block_poly.json"

    change_param(g.file_path_circuit,path_result_res,path_result_cap,path_result_block,line_num)

    name_list = ["banmen","line_width"]
    value_list = [banmen,line_width]

    ans = exe_netlist(g.dcgain_path,"ac")
    """
    =============
    ([[17.337, 1026200.0, 6668000.0, 98.356, 27.0, 1.0]],
    ['dcgain', 'bw', 'w0', 'p0', 'temper', 'alter#'])
    """
    value = ans[0]
    name = ans[1]
    count = 0
    for i,n in enumerate(name):
        if n == "temper":
            count = i
            break
        name_list.append(n)
    for j,v in enumerate(value[0]):
        if j == count:
            break
        value_list.append(v)

    ans = exe_netlist(g.pdis_path,"dc")
    value = ans[0]
    name = ans[1]
    df = pd.DataFrame(data=value,columns=name)
    eva_name = "pdis"
    name_list.append(eva_name)
    value_list.append(df.mean()[eva_name])

    ans = exe_netlist(g.slewrate_path,"tran")
    value = ans[0]
    name = ans[1]
    df = pd.DataFrame(data=value,columns=name)
    eva_name = "sr"
    name_list.append(eva_name)
    value_list.append(df[eva_name].values[0])

    ans = exe_netlist(g.psrr_path,"ac")
    value = ans[0]
    name = ans[1]
    df = pd.DataFrame(data=value,columns=name)
    eva_name = "psrr"
    name_list.append(eva_name)
    value_list.append(df[eva_name].values[0])

    ans = exe_netlist(g.cmmr_path,"ac")
    value = ans[0]
    name = ans[1]
    df = pd.DataFrame(data=value,columns=name)
    eva_name = "cmrr"
    name_list.append(eva_name)
    value_list.append(df[eva_name].values[0])

    ans = exe_netlist(g.noise_path,"out_noise")
    value = ans[0]
    name = ans[1]
    name_list.append(name)
    value_list.append(value)

    ans = exe_netlist(g.rout_path,"out_rout")
    value = ans[0]
    name = ans[1]
    name_list[len(name_list):len(name_list)] = name
    value_list[len(value_list):len(value_list)] = value

    v_list = [value_list]
    df = pd.DataFrame(data=v_list,columns=name_list)

    if exe_num == 0:
        df.to_csv('result_finish.csv', index=False)
    else:
        df.to_csv('result_finish.csv', mode='a', index=False, header=False)

    if os.path.exists(path_result_res):   
        os.remove(path_result_res)
    if os.path.exists(path_result_cap):   
        os.remove(path_result_cap)
    if os.path.exists(path_result_block):   
        os.remove(path_result_block)



if __name__ == "__main__": 

    #g.port = sys.argv[1]
    g.os_path = os.getcwd()

    g.file_path_circuit = g.os_path + "/opamp_netlist/opamp"
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

    g.opamp_path_circuit = g.os_path + "/opamp_netlist/opamp_temp.net"

    finish_point = 3000

    #入力ファイル->素子ブロック，分岐ブロック，境界条件のブロック

    #inv
    #input_file = g.os_path+"/input/sample_inv.txt"

    #opamp
    input_file = g.os_path+"/input/sample_amp.txt"
    num_fix = [2,1,2,2]

    #試行回数
    max_exe_num = 1
    max_banmen,block_num,circuit_block,line_num,ini_block_info = read_input(input_file)
    min_banmen = [7,7,4]
    banmen_list = []
    for i in range(min_banmen[0],max_banmen[0],1):
        for j in range(min_banmen[1],max_banmen[1],1):
            banmen_list.append([i,j,4])
    banmen_list.remove([7,7,4])
    
    height = 4
    
    line_width_list = [float(i/10) for i in range(10,21,1)]
    
    false_count = 0
    for exe_num in range(max_exe_num):
        
        false_flag = 0
        result = "false"
        print(exe_num)
        false_count = 0
        
        
        while result == "false":
            
            line_width = random.choice(line_width_list)
            banmen = random.choice(banmen_list)
            banmen[2] = height
            print(banmen)
            block_info = copy.deepcopy(ini_block_info)
            
            wiring = Wiring(exe_num,banmen,line_width,circuit_block,line_num,block_info,num_fix)
            
            result = wiring.start()
            #結果表示（ナンバーリンクソルバーが失敗するときもある）
            print("=============================")
            print("=============================")
            print("=============================")
            print("=============================")

            if result == "false":
                false_count += 1
                print(false_count)
            if false_count > 10:
                banmen_list.remove(banmen)
                false_flag = 1
                break

            del wiring

        df = pd.DataFrame(data=[[exe_num,banmen[0],banmen[1],banmen[2],false_count]],columns=["exe_num","x","y","z","false"])

        if exe_num == 0:
            df.to_csv('result_false.csv', index=False)
        else:
            df.to_csv('result_false.csv', mode='a', index=False, header=False)

        
        if false_flag == 1:
            pass

        elif false_flag == 0:

            execute_raphael(exe_num,line_num)

            exe_hspice(exe_num,line_num,banmen,line_width)
            
            """
        

            #file_path_circuit = os_path+"test4"
            #change_param(file_path_circuit,path_result_res,path_result_cap,path_result_block)
            """
            """
            if os.path.exists(path_result_res):   
                os.remove(path_result_res)
            if os.path.exists(path_result_cap):   
                os.remove(path_result_cap)
            if os.path.exists(path_result_block):   
                os.remove(path_result_block)
            """
       