import os
import sys
import subprocess
# from subprocess import PIPE
import time
import pprint
import random
import re
import global_value as g

def prepare_solve(banmen,ini_sg_list,core_list,line_num):

    data = []
    ini_sg_list = sorted(ini_sg_list,key = lambda x: x[0])
    
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


    with open(g.path_in_numlink,"w") as f:
        for da in data:
            f.write(da)
            f.write('\n')
    
def conv_boardstr(lines, terminals='initial', _seed=12345):
    """
    問題ファイルを boardstr に変換
    """

    random.seed(_seed)

    boardstr = ''
    
    for line in lines:
        if 'SIZE' in line:
            x, y, z = line.strip().split(' ')[1].split('X')
            boardstr += ('X%02dY%02dZ%d' % (int(x), int(y), int(z)))
        if 'LINE_NUM' in line:
            pass
        if 'LINE#' in line:
            _line = re.sub(r', +', ',', line)
            _line = re.sub(r' +', ' ', _line)
            sp = _line.strip().replace('-', ' ').replace('(', '').replace(')', '').split(' ')
            #print(sp)

            # s (スタート) -> g (ゴール)
            s_str = sp[1].split(',')
            g_str = sp[2].split(',')
            s_tpl = (int(s_str[0].strip()), int(s_str[1].strip()), int(s_str[2].strip()))
            g_tpl = (int(g_str[0].strip()), int(g_str[1].strip()), int(g_str[2].strip()))

            # 端に近い方をスタートにしたいから各端までの距離計算する
            # (探索のキューを小さくしたいから)
            s_dist_x = min(s_tpl[0], int(x) - 1 - s_tpl[0])
            s_dist_y = min(s_tpl[1], int(y) - 1 - s_tpl[1])
            s_dist_z = min(s_tpl[2], int(z) - 1 - s_tpl[2])
            s_dist = s_dist_x + s_dist_y + s_dist_z
            #print(s_dist_x, s_dist_y, s_dist_z, s_dist)
            g_dist_x = min(g_tpl[0], int(x) - 1 - g_tpl[0])
            g_dist_y = min(g_tpl[1], int(y) - 1 - g_tpl[1])
            g_dist_z = min(g_tpl[2], int(z) - 1 - g_tpl[2])
            g_dist = g_dist_x + g_dist_y + g_dist_z
            #print(g_dist_x, g_dist_y, g_dist_z, g_dist)

            # start と goal
            start_term = '%02d%02d%d' % (int(s_str[0]), int(s_str[1]), int(s_str[2]))
            goal_term  = '%02d%02d%d' % (int(g_str[0]), int(g_str[1]), int(g_str[2]))

            # 端に近い方をスタートにするオプションがオンのときは距離に応じて端点を選択する
            if terminals == 'edgefirst':
                if s_dist <= g_dist:
                    boardstr += ('L' + start_term + goal_term)
                else:
                    boardstr += ('L' + goal_term + start_term)
            # ランダムにスタート・ゴールを選ぶ
            elif terminals == 'random':
                if random.random() < 0.5:
                    boardstr += ('L' + start_term + goal_term)
                else:
                    boardstr += ('L' + goal_term + start_term)
            # 問題ファイルに出てきた順
            else:
                boardstr += ('L' + start_term + goal_term)
        if 'CORE' in line:
            _line = re.sub(r', +', ',', line)
            _line = re.sub(r' +', ' ', _line)
            sp = _line.strip().replace('-', ' ').replace('(', '').replace(')', '').split(' ')
            c_str = sp[1].split(',')
            
            c_tpl = (int(c_str[0].strip()), int(c_str[1].strip()), int(c_str[2].strip()) - 1)
            dummy_tpl = (0,0,0)

            core_term = '%02d%02d%d' % (int(c_str[0]), int(c_str[1]), int(c_str[2]))
            dummy_term  = '%02d%02d%d' % (int(dummy_tpl[0]), int(dummy_tpl[1]), int(dummy_tpl[2]))
            boardstr += ('C' + core_term + dummy_term)
            
    return boardstr

def make_boardstr():

    with open(g.path_in_numlink, 'r') as f:
        lines = f.readlines()

    # 問題ファイルを boardstr に変換
    # boardstr = BoardStr.conv_boardstr(lines, args.terminals, args.seed)
    boardstr = conv_boardstr(lines, 'initial', 12345)

    return boardstr

def solve_numlink(banmen,ini_sg_list,core_list,line_num):

    g.path_in_numlink = g.os_path+"/test_pynq.txt"
    g.path_out_numlink = g.os_path+"/result_path.txt"

    prepare_solve(banmen,ini_sg_list,core_list,line_num)

    boardstr = make_boardstr()

    # 表示
    # print("question!")
    # print(boardstr)

    cmd = ["./sim",boardstr,g.path_out_numlink]
    
    proc = subprocess.run(cmd)

def neighbor(pos):
    return [(pos[0]+1,pos[1],pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0],pos[1]+1,pos[2]),(pos[0],pos[1]-1,pos[2]),(pos[0],pos[1],pos[2]+1),(pos[0],pos[1],pos[2]-1)]

def read_answer(banmen,lines,sg_list):

    z = 0
    position_dict = {}
    for index,line in enumerate(lines):
        if "LAYER" in line.split(): 
            for y in range(banmen[1]):
                a = lines[index+1+y].split(",")
                for x in range(banmen[0]):
                    if a[x] != "0":
                        if int(a[x]) not in position_dict.keys():
                            # position_dict[int(a[x])] = [(x,banmen[1]-1-y,z)]
                            position_dict[int(a[x])] = [(x,y,z)]
                        else:
                            # position_dict[int(a[x])].append((x,banmen[1]-1-y,z))
                            position_dict[int(a[x])].append((x,y,z))
            z += 1

    # pprint.pprint(position_dict)

    path_dict = {}

    for num,start,goal in sg_list:
        pos_list = position_dict[num]
        current = start
        path_dict[num] = [current]
        pos_list.remove(current)
        count = 0
        while current != goal:
            # print(current,end = "->")
            nei_list = neighbor(current)
            for nei in nei_list:
                if nei in pos_list:
                    current = nei
                    break
            pos_list.remove(current)
            path_dict[num].append(current)

            count += 1
            if count > 1000:
                print("make_path_error")
                sys.exit()

    # pprint.pprint(path_dict)

    path_list = []
    for num,path in path_dict.items():
        path_list.append([num,path])

    return path_list

    









    
