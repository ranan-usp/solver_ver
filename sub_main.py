import os
import sys
import subprocess
from solver import gen_boardstr,BoardStr
import time
import pprint


def solve(banmen,ini_sg_list,core_list,line_num):
    data = []
    ini_sg_list = sorted(ini_sg_list,key = lambda x: x[0])
    pprint.pprint(ini_sg_list)
    print()
    
    size_info = "SIZE "+str(banmen[0])+"X"+str(banmen[1])+"X"+str(banmen[2])
    data.append(size_info)
    linenum_info = "LINE_NUM "+str(line_num)
    data.append(linenum_info)
    data.append("")
    for sg in ini_sg_list:
        line_info = "LINE#"+str(sg[0])+" ("+str(sg[1][0])+","+str(sg[1][1])+","+str(sg[1][2]+1)+") ("+str(sg[2][0])+","+str(sg[2][1])+","+str(sg[2][2]+1)+")"
        data.append(line_info)
    
    for core in core_list:
        core_info = "CORE "+"("+str(core[0])+","+str(core[1])+","+str(core[2]+1)+")"
        data.append(core_info)

    path = os.getcwd()+"/test_pynq.txt"

    with open(path,"w") as f:
        for da in data:
            f.write(da)
            f.write('\n')
    
    path_result = os.getcwd()+"/result_path.txt"

    boardstr = gen_boardstr.main(path)
    # print(boardstr)
    # boardstr = "X10Y18Z2L0900109002L0901105012L0902103052L0903103062L0904100102L0905106012L0906109022L0717109102L0808109112L0017209172L0401200072L0912208152L0009201092L0709209092L0901206052L0309204092L0701209072L0101201022L0011202152L0016202162";
    
    cmd = ["./sim",boardstr,path_result]
    
    p = subprocess.Popen(cmd)
    #time.sleep(10)
    #p.kill()
 
    return path_result
    




    
