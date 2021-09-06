
import random
from sys import path_hooks
import numpy as np
import pandas as pd
import os
import pprint
import json

import global_value as g
from implementation_temp import *
from raphael_poly3D_temp import execute_raphael
from block import Block
from hspice import *
from sub_main import solve

class Wiring():

    def __init__(self,exe_num,banmen,line_width,circuit_block,line_num,block_info,num_fix) -> None:
        
        self.exe_num = exe_num
        self.banmen = banmen
        self.circuit_block = circuit_block
        self.line_num = line_num
        self.block_info = block_info
        self.position_fix = None
        self.count_fix = 0
        self.num_fix = num_fix
        self.pos_candidate_x = [i for i in range(0,self.banmen[0],1)]
        self.pos_candidate_y = [i for i in range(0,self.banmen[1],1)]
        self.pos_candidate_z = [i for i in range(0,self.banmen[2],1)]
        self.pos_candidate = [self.pos_candidate_x,self.pos_candidate_y,self.pos_candidate_z]
        self.width_x = self.banmen[0]
        self.width_y = self.banmen[1]
        self.height = self.banmen[2]
        self.line_width = line_width
        self.bunki_where = []

    def __del__(self):
        pass

    def make_fix_pos(self):

        num_vin,num_vout,num_vdd,num_vss = self.num_fix
            
        out_frame = set()

        fix_pos = list()

        out_frame_left = [(0,i,j) for i in range(1,self.banmen[1]-1,1) for j in range(self.banmen[2])]
        out_frame_right = [(self.banmen[0]-1,i,j) for i in range(1,self.banmen[1]-1,1) for j in range(self.banmen[2])]
        out_frame_up = [(i,0,j) for i in range(1,self.banmen[0]-1,1) for j in range(self.banmen[2])]
        out_frame_under = [(i,self.banmen[1]-1,j) for i in range(1,self.banmen[0]-1,1) for j in range(self.banmen[2])]

        out_frame |= set(out_frame_left)
        out_frame |= set(out_frame_right)
        out_frame |= set(out_frame_up)
        out_frame |= set(out_frame_under)

        vin,vout,vdd,vss = random.sample([i for i in range(0,self.banmen[2],1)],4)

        pos_vin = random.sample([x for x in out_frame if x[0] == 0 and x[2] == vin],num_vin)
        #print(pos_vin)
        for pos in pos_vin:
            fix_pos.append(pos)
        out_frame = out_frame - set(pos_vin)

        pos_vout = random.sample([x for x in out_frame if x[0] == self.banmen[0]-1 and x[2] == vout],num_vout)
        #print(pos_vout)
        for pos in pos_vout:
            fix_pos.append(pos)
        out_frame = out_frame - set(pos_vout)

        pos_vdd = random.sample([x for x in out_frame if (x[0] == 0 or x[1] == 0 or x[0] == self.banmen[0]-1 or x[1] == self.banmen[1]-1) and x[2] == vdd],num_vdd)
        #print(pos_vdd)
        for pos in pos_vdd:
            fix_pos.append(pos)
        out_frame = out_frame - set(pos_vdd)

        pos_vss = random.sample([x for x in out_frame if (x[0] == 0 or x[1] == 0 or x[0] == self.banmen[0]-1 or x[1] == self.banmen[1]-1) and x[2] == vss],num_vss)
        #print(pos_vss)
        for pos in pos_vss:
            fix_pos.append(pos)
        out_frame = out_frame - set(pos_vss)

        return fix_pos

    def evo_make_fix_pos(self,pos):     
        out_frame = set()

        out_frame_left = [(0,i,j) for i in range(1,self.banmen[1]-1,1) for j in range(self.banmen[2])]
        out_frame_right = [(self.banmen[0]-1,i,j) for i in range(1,self.banmen[1]-1,1) for j in range(self.banmen[2])]
        out_frame_up = [(i,0,j) for i in range(1,self.banmen[0]-1,1) for j in range(self.banmen[2])]
        out_frame_under = [(i,self.banmen[1]-1,j) for i in range(1,self.banmen[0]-1,1) for j in range(self.banmen[2])]
        
        out_frame |= set(out_frame_left)
        out_frame |= set(out_frame_right)
        out_frame |= set(out_frame_up)
        out_frame |= set(out_frame_under)

        out_frame = list(out_frame)

        out_frame = sorted(out_frame,key = lambda x: (pos[0]-x[0])**2 + (pos[1]-x[1])**2 + (pos[2]-x[2])**2)

        return out_frame

    def sort_distance(self,fix_sg_list):
        temp = copy.deepcopy(fix_sg_list)
        count = 0
        for num,start in fix_sg_list:

            a = self.evo_make_fix_pos(start)
            
            d = (start[0]-a[0][0])**2+(start[1]-a[0][1])**2+(start[2]-a[0][2])**2
            temp[count].append(d)
            count += 1

        temp = sorted(temp,key = lambda val: val[2])


        return temp
        
    def random_pos_block_temp(self):
        
        while True:
            #境界条件の位置を決定
            self.position_fix = self.make_fix_pos()
           
            g.bunki_where = []
            g.fix_where = []
            g.fix_pos = []
            g.fix_pos_num = []
            g.hantei = [0]*self.line_num
            g.num_pos = {}
            g.pos_set = set()
            g.num_core_pos_dict = dict()
            #ネットリスト上の配線のスタートとゴールの座標に合わせる．

            result_block_list = []
            num_position_list = []
            pos_info_dict = {}
            count = 0
            flag = 0

            false_count = 0
            g.count_fix = 0
            for num,block_info in enumerate(self.block_info):
                count += 1
                block = Block(num,self.banmen,block_info,self.position_fix,self.count_fix,self.pos_candidate)
                res = block.start()

                if res == "false":
                    false_count += 1
                    flag = 1
                    break

                result_block,num_position,pos_info = block.out_param()
                
                #BLOCKひとつ分の情報格納
                result_block_list.append(result_block)
                num_position_list[len(num_position_list):len(num_position_list)] = num_position

                for numm,pos in pos_info:
                    pos_info_dict[numm] = pos

                del block


            if num == len(self.block_info)-1 and flag == 0:
                break

            if false_count > 500:
                return "false"
        
        #各番号の座標まとめ
        num_position_list.sort()
 
        return result_block_list,num_position_list,pos_info_dict

    def ini_make_path(self,num_position_list):
        walls = []
        #素子ブロックと分岐ブロックの位置情報
        core_list = list()

        #配線の開始位置と終端位置の情報
        sg_list = list()

        sg_count = 0

        count = 0
        
        for num,position in enumerate(num_position_list):
            
            #core_listの作成，diagram4.wallsの作成
            #diagram4.wallsは，ナンバーリンク（配線）で通ってはいけない位置を指定できる
            if position[0] == "-1":
                core_list.append(position[1])
                walls.append(position[1])
                """
                diagram4.weights[position[1]] = weight
                """
                continue

            elif position[0] == "0":
                continue

            else:
                count += 1
                #sg_listの作成（開始位置と終端位置の2つ座標をまとめるため）
                if count%2 == 1:
                    number = int(num_position_list[num][0].split("-")[0])
                  
                    sg_list.append([number,position[1],num_position_list[num+1][1]])

                    #print(sg_count,position[1],position_list[num+1][1])
                    
                    #?(1)
                    walls.append(position[1])
                    walls.append(num_position_list[num+1][1])

                    """
                    diagram4.weights[position[1]] = weight
                    diagram4.weights[position_list[num+1][1]] = weight
                    """
        """
        for remove_pos in g.fix_pos:
            walls.remove(remove_pos)
        """
    

        return sg_list,core_list,walls

    #Rip-up and reroute法
    def evo_make_path(self,diagram4,num_position_list,pos_info_dict,count_make_path):

        ###
        weight = 5
        ###
        ini_sg_list,core_list,walls = self.ini_make_path(num_position_list)
        """
        short_sg_list = sorted(ini_sg_list,key = lambda x: (x[1][0]-x[2][0])**2 + (x[1][1]-x[2][1])**2 + (x[1][2]-x[2][2])**2)
        sg_list_list = []
        sg_list_list.append(short_sg_list)
        for _ in range(4):
            #配線の順番をランダムに決める．
            random_sg_list = random.sample(ini_sg_list,len(ini_sg_list))
            sg_list_list.append(random_sg_list)
        """
        #a_star_searchによって，得られた配線の位置情報(path)をまとめる
        
        core_set = set(core_list)
        ans_path_list = list()
        false_path_count = 0
        
        #wallsには，初期段階でコア座標と端子座標を格納している
        diagram4.walls = copy.deepcopy(walls)
       
        #Rip-up and reroute法
        #配線がほかの配線と被ってしまった配線番番号を格納
        again_path_num = list()
        #はじめは，すべての配線番号が対象
        fix_sg_list = list()
        for path_num,start,goal in ini_sg_list:
            if path_num in g.fix_pos_num:
                if start in g.fix_pos:
                    fix_sg_list.append([path_num,goal])
                else:
                    fix_sg_list.append([path_num,start])

            again_path_num.append(path_num)
        flag = 0

        
        #再び配線する番号がなくなれば，終了(被りがなくなれば終了)
        while len(again_path_num) > 0:
            #このループで，配線した番号とパスを格納
            
            print("===============")
            print(again_path_num)
            path_list = list()
            random_sg_list = random.sample(ini_sg_list,len(ini_sg_list))
            

            for path_num,start,goal in random_sg_list:
                # 境界条件ブロックは後で
                if path_num not in g.fix_pos_num:
                    #被り判定の出た配線番号だけ処理
                    if path_num in again_path_num:

                        #お互いの端子がお互いのコア座標に入っている場合
                        duplicate = list(set([start,goal]) & core_set)
                        if len(duplicate) == 2:
                            path = [start,goal]
                        
                        #お互いの端子が同じ座標にある場合
                        elif start == goal:
                            path = [start]
                            
                        else:
                            #配線のスタートとゴールの並び替え
                            if pos_info_dict[str(path_num)+"-s"] != start:
                                temp = start
                                start = goal
                                goal = temp
                            
                            #?(1)
                            #配線のために，端子にある座標はwallsから取り除く必要あり
                            diagram4.walls.remove(start)
                            diagram4.walls.remove(goal)
                            #重さも調整可能
                            """
                            del diagram4.weights[start]
                            del diagram4.weights[goal]
                            """
                            #came_fromにpath情報掲載？
                            came_from, cost_so_far = a_star_search(diagram4, start, goal)
                            try:
                                #came_fromで得た情報から，パスをたどれるか
                                path=reconstruct_path(came_from, start=start, goal=goal)
                            except KeyError:
                                #ナンバーリンク失敗
                                return "false"

                            diagram4.walls.append(start)
                            diagram4.walls.append(goal)
                        #各配線のpath情報保存
                        path_list.append([path_num,path])

                        #配線の位置に進入禁止対策
                        #diagram4.walls[len(diagram4.walls):len(diagram4.walls)] = path

            #again_path_numについて，処理終了
            # path_listについて処理開始    
            #############################
            for target_path_num,target_path in path_list:
                # lは，すべてのパスがもつ各座標をまとめたもの
                # 被り判定用
                # target_pathの中の座標がLにその数だけあればcontinue
                L = [x for row in path_list for x in row[1]]
                l_count = 0
                for l in L:
                    if l in target_path:
                        l_count += 1

                duplicate_count = l_count - len(target_path)
                flag = 0
                if duplicate_count != 0:
                    #dummy
                    duplicate_list = []
                    flag_p = 0
                    # path_tempは，path情報
                    #被り数2なら通過させて,相手を通過させない
                    if duplicate_count == 1 and (target_path_num not in duplicate_list):
                        # 被っている相手方を見つけ出すためのfor文
                        for i,pos in enumerate(target_path):
                            
                            for compare_path_num,compare_path in path_list:
                                
                                if target_path_num == compare_path_num:
                                    continue

                                if pos in compare_path:
                                    diagram4.walls.append(pos)
                                    duplicate_list.append(compare_path_num)
                                    flag_p = 1
                                    break

                            if flag_p == 1:
                                flag_p = 0
                                break

                    # lが2つ以上同じ座標を持つということは，再度パスを見つける必要がある
                    else:
                        print(duplicate_count)
                        #print("=====duplicate=====")

                        flag = 1
                        break
                # flag == 0なら，被りがないので，パス確定
                if flag == 0:
                    #print("=====pass=====")
                    # パスが確定したので，again_path_numから除外
                    again_path_num.remove(target_path_num)
                    # ans_path_listに格納
                    ans_path_list.append([target_path_num,target_path])
                    # 進入禁止のためにwallsに格納
                    diagram4.walls[len(diagram4.walls):len(diagram4.walls)] = target_path

            
            #確定したpathのリストが，sg_listと同じ長さになれば終了
            #ans_path_listとcore_listを返す
            if len(ans_path_list) == (len(ini_sg_list)-len(g.fix_where)):
                #############################
                pprint.pprint(fix_sg_list)
                print()
                for path_num,start,goal in fix_sg_list:

                    if start == goal:
                            path = [start]
                    else:

                        if pos_info_dict[str(path_num)+"-s"] != start:
                            temp = start
                            start = goal
                            goal = temp
                        #?(1)
                        #配線のために，端子にある座標はwallsから取り除く必要あり
                        diagram4.walls.remove(start)
                        diagram4.walls.remove(goal)
                        #重さも調整可能
                        """
                        del diagram4.weights[start]
                        del diagram4.weights[goal]
                        """
                        #came_fromにpath情報掲載？
                        came_from, cost_so_far = a_star_search(diagram4, start, goal)
                        try:
                            #came_fromで得た情報から，パスをたどれるか
                            path=reconstruct_path(came_from, start=start, goal=goal)
                        except KeyError:
                            #ナンバーリンク失敗
                            return "false"

                    ans_path_list.append([path_num,path])
                    # 進入禁止のためにwallsに格納
                    diagram4.walls[len(diagram4.walls):len(diagram4.walls)] = path

                S = set()
                sum_a = 0
                for a in ans_path_list:
                    S = S | set(a[1])
                    print(len(S),end="->")
                    sum_a += len(a[1])
                    print(sum_a)
                
                pprint.pprint(ans_path_list)
                print()
                return ans_path_list,core_list

            else:

                # whileのループが500回で終了
                # 見込みなしなので，新たな素子配置をする    
                false_path_count += 1

                if false_path_count == 100:
                    print()
                    return "false"
                    
            """
            for p in path:
                diagram4.weights[p] = weight
            """
    #境界条件後回し法
    def evo2_make_path(self,diagram4,num_position_list,pos_info_dict,count_make_path):
    
        ###
        weight = 5
        ###
        ini_sg_list,core_list,walls = self.ini_make_path(num_position_list)

        fix_sg_list = list()
        for path_num,start,goal in ini_sg_list:
            if path_num in g.fix_pos_num:
                if start in g.fix_pos:
                    fix_sg_list.append([path_num,goal])
                else:
                    fix_sg_list.append([path_num,start])


        short_sg_list = sorted(ini_sg_list,key = lambda x: (x[1][0]-x[2][0])**2 + (x[1][1]-x[2][1])**2 + (x[1][2]-x[2][2])**2)
        sg_list_list = []
        sg_list_list.append(short_sg_list)
        for _ in range(2):
            #配線の順番をランダムに決める．
            random_sg_list = random.sample(ini_sg_list,len(ini_sg_list))
            sg_list_list.append(random_sg_list)

        #a_star_searchによって，得られた配線の位置情報(path)をまとめる
        
        false_path_count = 0
        core_set = set(core_list)
        
        for sg_list in sg_list_list:
            path_list = list()
            
            diagram4.walls = copy.deepcopy(walls)
          
            for path_num,start,goal in sg_list:
                if path_num not in g.fix_pos_num:

                    duplicate = list(set([start,goal]) & core_set)
                    if len(duplicate) == 2:
                        path = [start,goal]
                    
                    #配線のスタートとゴールの並び替え
                    elif start == goal:
                        #?(1)
                        path = [start]
                        
                    else:
                        if pos_info_dict[str(path_num)+"-s"] != start:
                            temp = start
                            start = goal
                            goal = temp

                        #?(1)
                        diagram4.walls.remove(start)
                        diagram4.walls.remove(goal)

                        """
                        del diagram4.weights[start]
                        del diagram4.weights[goal]
                        """
                        
                        #algorithmの種類（遠回りもできる）
                        # -> bread fast algorithm
                        # -> djikstro's algorithm
                        # -> a* algorithm

                        #came_fromにpath情報掲載？
                        came_from, cost_so_far = a_star_search(diagram4, start, goal)

                        #draw_grid(diagram4, point_to=came_from, start=start, goal=goal)
                        #print("***********************")

                        try:
                            #path確認
                            path=reconstruct_path(came_from, start=start, goal=goal)
                            
                        except KeyError:
                            #ナンバーリンク失敗
                            break

                    #print(path_num)
                    #print(path)

                #各配線のpath情報保存
                    path_list.append([path_num,path])

                #draw_grid(diagram4, path=reconstruct_path(came_from, start=start, goal=goal))

                #配線の位置に進入禁止対策
                    diagram4.walls[len(diagram4.walls):len(diagram4.walls)] = path

                if len(path_list) == len(sg_list)-len(g.fix_pos_num):
                    print("===============")
                    sorted_fix_sg_list = self.sort_distance(fix_sg_list)
                    for path_num,start,d in sorted_fix_sg_list:
                        out_frame = self.evo_make_fix_pos(start)
                        print(path_num,start)
                        count = 0
                        for goal in out_frame:
                            diagram4.walls.append(start)
                            diagram4.walls.append(goal)
                            if start == goal:
                                    path = [start]
                            else:
                                if pos_info_dict[str(path_num)+"-s"] != start:
                                    temp = start
                                    start = goal
                                    goal = temp
                                #?(1)
                                #配線のために，端子にある座標はwallsから取り除く必要あり
                                diagram4.walls.remove(start)
                                diagram4.walls.remove(goal)
                                #重さも調整可能
                                """
                                del diagram4.weights[start]
                                del diagram4.weights[goal]
                                """
                                #came_fromにpath情報掲載？
                                came_from, cost_so_far = a_star_search(diagram4, start, goal)
                                try:
                                    #came_fromで得た情報から，パスをたどれるか
                                    path=reconstruct_path(came_from, start=start, goal=goal)
                                    break

                                except KeyError:
                                    #ナンバーリンク失敗
                                    count += 1
                                    diagram4.walls.append(start)
                                    diagram4.walls.append(goal)
                                
                                    if count == len(out_frame):
                                        return "false"

                        path_list.append([path_num,path])
                        

                        # 進入禁止のためにwallsに格納
                        diagram4.walls[len(diagram4.walls):len(diagram4.walls)] = path
                        if len(path_list) == len(ini_sg_list):
                            pprint.pprint(path_list)
                            print()

                            return path_list,core_list
                    
            false_path_count += 1

            if false_path_count == len(sg_list_list):
                
                return "false"

            """
            for p in path:
                diagram4.weights[p] = weight
            """

    
        return path_list,core_list

    def make_path(self,diagram4,num_position_list,pos_info_dict,count_make_path):
        
        ###
        weight = 5
        ###
        ini_sg_list,core_list,walls = self.ini_make_path(num_position_list)
        
        result_path = solve(self.banmen,ini_sg_list,core_list,self.line_num)
        
        with open(result_path,"r") as f:
            s = f.read()
        lines = s.split("\n")
        pprint.pprint(lines)
        return "ans"


        short_sg_list = sorted(ini_sg_list,key = lambda x: (x[1][0]-x[2][0])**2 + (x[1][1]-x[2][1])**2 + (x[1][2]-x[2][2])**2)
        sg_list_list = []
        sg_list_list.append(short_sg_list)
        for _ in range(9):
            #配線の順番をランダムに決める．
            random_sg_list = random.sample(ini_sg_list,len(ini_sg_list))
            sg_list_list.append(random_sg_list)

        core_set = set(core_list)

        #a_star_searchによって，得られた配線の位置情報(path)をまとめる
        
        false_path_count = 0
        for sg_list in sg_list_list:
            path_list = list()
            
            diagram4.walls = copy.deepcopy(walls)
          
            for path_num,start,goal in sg_list:
                
                #配線のスタートとゴールの並び替え

                duplicate = list(set([start,goal]) & core_set)
                if len(duplicate) == 2:
                    path = [start,goal]
                elif start == goal:
                    #?(1)
                    path = [start]
                    
                else:
                    if pos_info_dict[str(path_num)+"-s"] != start:
                        temp = start
                        start = goal
                        goal = temp

                    #?(1)
                    diagram4.walls.remove(start)
                    diagram4.walls.remove(goal)

                    """
                    del diagram4.weights[start]
                    del diagram4.weights[goal]
                    """
                    
                    #algorithmの種類（遠回りもできる）
                    # -> bread fast algorithm
                    # -> djikstro's algorithm
                    # -> a* algorithm

                    #came_fromにpath情報掲載？
                    came_from, cost_so_far = a_star_search(diagram4, start, goal)

                    #draw_grid(diagram4, point_to=came_from, start=start, goal=goal)
                    #print("***********************")

                    try:
                        #path確認
                        path=reconstruct_path(came_from, start=start, goal=goal)
                        
                    except KeyError:
                        #ナンバーリンク失敗
                        
                        break

                #print(path_num)
                #print(path)

                #各配線のpath情報保存
                path_list.append([path_num,path])

                #draw_grid(diagram4, path=reconstruct_path(came_from, start=start, goal=goal))

                #配線の位置に進入禁止対策
                diagram4.walls[len(diagram4.walls):len(diagram4.walls)] = path

                if len(path_list) == len(sg_list):
                    return path_list,core_list
                    
            false_path_count += 1

            if false_path_count == len(sg_list_list):
                
                return "false"

            """
            for p in path:
                diagram4.weights[p] = weight
            """

    
        return path_list,core_list


    def make_perfect_path(self,result_block_list,path_list,block_direction):

        block_info = list()

        for temp in result_block_list:
            if temp[0] == ['x', 'x', 'not_stand']:
                continue
            pos_list = list()
            #index_list = list()
            for i,index in enumerate(temp[1]):
                #print("index->"+str(index))
                if index == 0:
                    continue
                    
                    #index_list.append(index)
                if index == -1:
                    core = temp[3][i]
                    neighbor_list = [(core[0]-1,core[1],core[2]),(core[0]+1,core[1],core[2]),(core[0],core[1]-1,core[2]),(core[0],core[1]+1,core[2]),(core[0],core[1],core[2]+1),(core[0],core[1],core[2]-1)]
                    neighbor_pos = list()
                    for neighbor in neighbor_list:

                        try:
                            neighbor_num = temp[3].index(neighbor)
                        except ValueError:
                            continue
                        if temp[1][neighbor_num] != -1:
                            if temp[1][neighbor_num] != 0:
                                neighbor_pos.append(temp[3][neighbor_num])
                    block_info.append([core,neighbor_pos])

                    continue

                pos_list.append(temp[3][i])

        for i,path in enumerate(path_list):
            
            for initial in block_direction:
                #print(initial[0])
                
                if path[0] in initial[1]:
                    
                    a = np.array(path[1][0])-np.array(initial[0])
                    b = np.array(path[1][-1])-np.array(initial[0])

                    #print("num->",end=" ")
                    #print(num)
                    #if initial[0] == (width_x//2,0,0):

                    #vddについて
                    if initial[0][1] == 0 and initial[0] in self.position_fix: 
                        #print("vdd")

                        insert_position = (initial[0][0],-1,initial[0][2])
            
                        if path_list[i][1][0] == initial[0] and insert_position not in path_list[i][1]:

                            path_list[i][1].insert(0,insert_position)
                        else:
                            path_list[i][1].append(insert_position)

                    #vinについて
                    elif initial[0][0] == 0 and initial[0] in self.position_fix:
                        #print("vin")

                        insert_position = (-1,initial[0][1],initial[0][2])

                        if path_list[i][1][0] == initial[0] and insert_position not in path_list[i][1]:
        
                            path_list[i][1].insert(0,insert_position)
                        else:
                            path_list[i][1].append(insert_position)
                        

                    elif initial[0][0] == self.width_x-1 and initial[0] in self.position_fix:
                        #print("vout")

                        insert_position = (self.width_x-1+1,initial[0][1],initial[0][2])

                        if path_list[i][1][0] == initial[0] and insert_position not in path_list[i][1]:
            
                            path_list[i][1].insert(0,insert_position)
                        else:
                            path_list[i][1].append(insert_position)

                    #elif initial[0] == (width_x//2,width_y-1,0):
                    elif initial[0][1] == self.width_y-1 and initial[0] in self.position_fix:
                        #print("ground")

                        insert_position = (initial[0][0],self.width_y-1+1,initial[0][2])

                        if path_list[i][1][0] == initial[0] and insert_position not in path_list[i][1]:

                            path_list[i][1].insert(0,insert_position)
                        else:
                            path_list[i][1].append(insert_position)

                    elif len(np.where(a==0)[0] == 0) == 3 or len(np.where(b==0)[0] == 0) == 3:
                        continue
                    else:
                        for info in block_info:
                        
                            if path[1][0] in info[1] and info[0] not in path_list[i][1]:
                                path_list[i][1].insert(0,info[0])
                                break

                            elif path[1][-1] in info[1] and info[0] not in path_list[i][1]:
                                path_list[i][1].append(info[0])
                                break
        return path_list

    def make_banmen(self,num_position_list,pos_info_dict):
        count_make_path  = 0
        while True:
                #設定した回路のサイズで，ナンバーリンク用の盤面を作る．
            diagram4 = GridWithWeights(self.banmen[0], self.banmen[1], self.banmen[2])
        
            ans = self.make_path(diagram4,num_position_list,pos_info_dict,count_make_path)
            print("=========")
            print(ans)
            print("=========")

            return ans
                
        
        #pathを番号順に並び替え
        path_list.sort()

        #配線のpath情報のみのリスト
        temp_new_path_list = np.array(path_list)
        
        new_path_list = temp_new_path_list[:,1].tolist()

        return core_list,path_list,new_path_list

    def output_result(self,path_list):
    
        width_x,width_y,height = self.banmen
        
        result = list()
        for z in range(height):
            temp1 = list()
            for y in range(width_y):
                temp2 = list()
                for x in range(width_x):
                    flag = 0
                    for p,path in enumerate(path_list):
                        if (x,y,z) in path:
                            temp2.append(p+1)
                            flag = 1
                            break
                    if flag==0:    
                        temp2.append(0)
                temp1.append(temp2)
            result.append(temp1)
        return result

    def make_block_direction(self,result_block_list):

        block_direction = list()

        #result_block = [[roulette,conversion],num_list,block_size,position]
 
        for i in range(len(result_block_list)):
            temp = list()
            #core座標追加
            #素子ブロックと分岐ブロック
            if -1 in result_block_list[i][1]:
                core_index_list = [i for i, x in enumerate(result_block_list[i][1]) if x == -1]
                for core_index in core_index_list:
                    temp = list()
                    core = result_block_list[i][3][core_index]
                    temp.append(core)
                    neighbor_list = [(core[0]-1,core[1],core[2]),(core[0]+1,core[1],core[2]),(core[0],core[1]-1,core[2]),(core[0],core[1]+1,core[2]),(core[0],core[1],core[2]-1),(core[0],core[1],core[2]+1)]
                    neighbor_num_list = list()
                    for neighbor in neighbor_list:
                        try:
                            neighbor_index = result_block_list[i][3].index(neighbor)
                            neighbor_num = result_block_list[i][1][neighbor_index]
                            
                            if neighbor_num != -1:
                                if neighbor_num != 0:
                                    neighbor_num_list.append(neighbor_num)

                        except ValueError:
                            continue
                    temp.append(neighbor_num_list)

                    block_direction.append(temp)
                    
            #境界条件ブロック
            else:
                temp.append(result_block_list[i][3][0])
            
                #端子方向のブロックの配線番号
                temptemp = list()
                for num in result_block_list[i][1]:

                    if num not in [0,-1]:
                        temptemp.append(num)
                        
                temp.append(temptemp)

                block_direction.append(temp)


        return block_direction

    def save_information(self,result_block_list,num_position_list,core_list,path_list,block_direction):
        #dirがないとerrorがでるので，なかったら作る
        path_out_dir = g.os_path + "/output/out_"+str(self.exe_num)
        if not os.path.exists(path_out_dir):
            os.mkdir(path_out_dir)

        #block情報出力
        df_info = pd.DataFrame(result_block_list,columns=["posture","num_list","block_size","position_list"])
        path_out = g.os_path + "/output/out_"+str(self.exe_num)+"/result_block_list.csv"
        df_info.to_csv(path_out)

        df_info = pd.DataFrame(num_position_list,columns=["num","position"])
        path_out = g.os_path + "/output/out_"+str(self.exe_num)+"/num_position_list.csv"
        df_info.to_csv(path_out)
       
        df_info = pd.DataFrame(core_list)
        path_out = g.os_path + "/output/out_"+str(self.exe_num)+"/core_list.csv"
        df_info.to_csv(path_out)

        df_info = pd.DataFrame(path_list,columns=["num","path"])
        path_out = g.os_path + "/output/out_"+str(self.exe_num)+"/path_list.csv"
        df_info.to_csv(path_out)

        df_info = pd.DataFrame(block_direction,columns=["core_pos","nums"])
        path_out = g.os_path + "/output/out_"+str(self.exe_num)+"/block_direction.csv"
        df_info.to_csv(path_out)

    def make_circuit_structure(self,result_block_list,path_list):

        #print("length="+str(len(block_info)))
        #pprint.pprint(block_info)
        circuit = [[["0" for _ in range(self.width_x)] for _ in range(self.width_y)] for _ in range(self.height)]

        #core_color = [str(-1*(i+1)) for i in range(len(result_block))]
        core_color = ["-"+str(x) for x in range(1,10,1)]
        hantei = [0]*len(path_list)

        
        
        for path in path_list:
            #print(path)
            #path ->

            for i in range(len(path[1])-2):
                temp = np.concatenate([np.array(path[1][i+1])-np.array(path[1][i]),np.array(path[1][i+2])-np.array(path[1][i+1])],0)
                if (temp == np.array([-1,0,0,0,-1,0])).all() or (temp == np.array([0,1,0,1,0,0])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",rt"
                elif (temp == np.array([1,0,0,0,-1,0])).all() or (temp == np.array([0,1,0,-1,0,0])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",lt"
                elif (temp == np.array([0,-1,0,1,0,0])).all() or (temp == np.array([-1,0,0,0,1,0])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",ru"
                elif (temp == np.array([0,-1,0,-1,0,0])).all() or (temp == np.array([1,0,0,0,1,0])).all() :
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",lu"
                elif (temp == np.array([1,0,0,1,0,0])).all() or (temp == np.array([-1,0,0,-1,0,0])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",lr"
                elif (temp == np.array([0,1,0,0,1,0])).all() or (temp == np.array([0,-1,0,0,-1,0])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",ut"
                elif (temp == np.array([1,0,0,0,0,1])).all() or (temp == np.array([0,0,-1,-1,0,0])).all() or (temp == np.array([1,0,0,0,0,-1])).all() or (temp == np.array([0,0,1,-1,0,0])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",l0"
                elif (temp == np.array([-1,0,0,0,0,1])).all() or (temp == np.array([0,0,-1,1,0,0])).all() or (temp == np.array([-1,0,0,0,0,-1])).all() or (temp == np.array([0,0,1,1,0,0])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",r0"
                elif (temp == np.array([0,1,0,0,0,1])).all() or (temp == np.array([0,0,-1,0,-1,0])).all() or (temp == np.array([0,1,0,0,0,-1])).all() or (temp == np.array([0,0,1,0,-1,0])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",t0"
                elif (temp == np.array([0,-1,0,0,0,1])).all() or (temp == np.array([0,0,-1,0,1,0])).all() or (temp == np.array([0,-1,0,0,0,-1])).all() or (temp == np.array([0,0,1,0,1,0])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",u0"
                elif (temp == np.array([0,0,1,0,0,1])).all() or (temp == np.array([0,0,-1,0,0,-1])).all():
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = str(path[0])+",uu"
                else:
                    circuit[path[1][i+1][2]][path[1][i+1][1]][path[1][i+1][0]] = "false"
        
        color_count = 0
        #pprint.pprint(result_block_list)
        for i,block in enumerate(result_block_list):
            if block[0] == ['x', 'x', 'not_stand']:
                continue

            #分岐ブロックごとの区別が必要
            #分岐と素子のブロックを分けるべき？
            elif i+1 in g.bunki_where:
                temp = block[1].index(-1)
                if block[0] in [['u',0,"not_stand"],["d",1,"not_stand"]]:
                    #print("ok")
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",tr"
                elif block[0] in [['r',0,"not_stand"],["l",1,"not_stand"]]:
                    #print("ok")
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",tu"
                elif block[0] in [['d',0,"not_stand"],["u",1,"not_stand"]]:
                    #print("ok")
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",tl"
                elif block[0] in [['l',0,"not_stand"],["r",1,"not_stand"]]:
                    #print("ok")
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",tt"

                elif block[0] in [['l',0,"stand_up"],["r",1,"stand_up"],['r',0,"stand_up"],["l",1,"stand_up"]]:
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",t_up_lr"

                elif block[0] in [['l',0,"stand_under"],["r",1,"stand_under"],['r',0,"stand_under"],["l",1,"stand_under"]]:
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",t_under_lr"

                elif block[0] in [['d',0,"stand_up"],["u",1,"stand_up"],['u',0,"stand_up"],["d",1,"stand_up"]]:
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",t_up_ut"

                elif block[0] in [['d',0,"stand_under"],["u",1,"stand_under"],['u',0,"stand_under"],["d",1,"stand_under"]]:
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",t_under_ut"

                elif block[0] in [['u',0,"stand_super"],["d",1,"stand_super"]]:
                    #print("ok")
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",t_super_l"
                elif block[0] in [['r',0,"stand_super"],["l",1,"stand_super"]]:
                    #print("ok")
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",t_super_t"
                elif block[0] in [['d',0,"stand_super"],["u",1,"stand_super"]]:
                    #print("ok")
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",t_super_r"
                elif block[0] in [['l',0,"stand_super"],["r",1,"stand_super"]]:
                    #print("ok")
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = "b"+str(i+1)+",t_super_u"

            else:
                temp_list = [i for i, x in enumerate(block[1]) if x == -1]
                for temp in temp_list:
                    circuit[block[3][temp][2]][block[3][temp][1]][block[3][temp][0]] = core_color[color_count]
                color_count += 1

        return circuit

    def make_poly3D(self,p_list,new_path_list):

        flag_raphael = 0

        if flag_raphael == 0:
            template_path = g.os_path + "/structure/poly3D_template.txt"

        else:
            template_path = g.os_path + "/structure/poly3D_template10.txt"

    
        rho_al = 2.65e-8
        rho_cu = 1.68e-8
        
        t1 = 0.1e-6
        t2 = 0.36e-6
        t3 = t2
        t4 = 0.845e-6
        t5 = t4
        block_size = 10e-6
        rho = rho_al
        line_width = self.line_width

        with open(template_path,"r") as f:
            s = f.read()
        lines = s.split("\n")
        
        for i in range(len(lines)):
            if "*window_size" in lines[i]:
                window_size_point = i+1
                lines[window_size_point] = lines[window_size_point].split()
                lines[window_size_point][1] = "sizex="+str(self.width_x)
                lines[window_size_point][2] = "sizey="+str(self.width_y)
                lines[window_size_point] = " ".join(lines[window_size_point])
            elif "*line_width" in lines[i]:
                line_width_point = i+1
                lines[line_width_point] = lines[line_width_point].split()
                lines[line_width_point][1] = "w="+str(float(line_width))
                lines[line_width_point] = " ".join(lines[line_width_point])
        with open(template_path,"w") as f:
            for line in lines:
                f.write(line)
                f.write("\n")
       
        x_list = ["0","blockx/2-w/2","blockx/2+w/2","blockx"]
        y_list = ["0","blocky/2-w/2","blocky/2+w/2","blocky"]

        path_cir = g.os_path + "/output/out_"+str(self.exe_num)+"/circuit.txt"

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
                    "t_super_u":[(1,0),(2,0),(2,2),(1,2)],
                    "t_super_l":[(0,1),(0,2),(2,2),(2,1)],
                    "t_super_r":[(1,1),(1,2),(3,2),(3,1)],
                    "t_super_t":[(1,1),(1,3),(2,3),(2,1)],
                    
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
        path_result_block = g.os_path + "/output/out_"+str(self.exe_num)+"/block_poly.json"

        with open(path_result_block,"w") as f:
            temp = json.dumps(line_block_dict)
            f.write(temp)
        
        
        #抵抗情報　統一するか　分けるか
        #blockごとの抵抗save
        
        spice_res = {}
        for key,values in line_block_dict.items():
            
            for num in range(len(values)):

                z = values[num][1][2]+1
                t = 0.1
                if z == 1:
                    t = t1
                elif z == 2:
                    t = t2
                elif z == 3:
                    t = t3
                elif z == 4:
                    t == t5
                else:
                    t = 1
                
                if "b" in key:
                    name = "r" + key
                    spice_res[name] = (rho*block_size/(t*line_width))/2
                else:
                    name = "r_n" +key.zfill(3)+ "_" + str(num+1)
                    spice_res[name] = rho*block_size/(t*line_width)


        path_result_res = g.os_path + "/result_res/"+str(self.exe_num)+".json"

        with open(path_result_res,"w") as f:
            spice_res = json.dumps(spice_res)
            f.write(spice_res)

        #########################################################################
        #ブロックごとにかかる電圧を測定して，保存

        change_param_volt(g.opamp_path_circuit,path_result_res,path_result_block,line_num)
        block_volt_list = meas_volt(g.dcgain_path)
        
        path_result_block_volt = g.os_path + "/result_block_volt/"+str(self.exe_num)+".json"

        with open(path_result_block_volt,"w") as f:
            temp = json.dumps(block_volt_list)
            f.write(temp)
        #########################################################################

        insert_line = 32

        


        if flag_raphael == 0:
            template_path = g.os_path + "/structure/poly3D_template.txt"

        else:
            template_path = g.os_path + "/structure/poly3D_template10.txt"

        for h in range(self.height):
            with open(template_path,"r") as f:
                s = f.read()
            data = s.split("\n")

            for key,line_block in line_block_dict.items():

                for num,block in enumerate(line_block):

                    height = str(block[1][2]+1)
                    if height in [str(h),str(h+1)]:
                
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
                out_path = g.os_path + "/structure/"+str(self.exe_num)+"_"+str(h)+".txt"

                #元のファイルに書き込み
                with open(out_path, mode='w')as f:
                    for da in data:
                        f.write(da)
                        f.write('\n')

    #powerpoint_3Dモデル
    def output_pp_vba(self,circuit):   
        #path_csv = "/home/ranan/analog-block/output/out_"+str(exe_num)+"/cir_layer_"+str(z+1)+".csv"

        circuit_temp = copy.deepcopy(circuit)

        #ppのvba用？
        path_pp_macro_txt = g.os_path + "/output/out_"+str(self.exe_num)+"/cir_layer_macro.txt"

        with open(path_pp_macro_txt,"w") as f:
            for z in range(self.height):
                for y in range(self.width_y):
                    for x in range(self.width_x):
                        #pp出力のvbaのために配線番号いらない，ブロックノカタチのみ
                        if "," in circuit_temp[z][y][x]:
                            temp = circuit_temp[z][y][x].split(",")
                            circuit_temp[z][y][x] = temp[1]
                        f.write('Block_List('+str(z)+','+str(y)+','+str(x)+') = "'+circuit_temp[z][y][x]+'"\n')

    def start(self):

        ans_random_pos_block = self.random_pos_block_temp()
        if ans_random_pos_block == "false":
            print("random_pos_error")
            return "false"
        else:
            result_block_list,num_position_list,pos_info_dict = ans_random_pos_block

        ans_make_banmen = self.make_banmen(num_position_list,pos_info_dict)

        return ans_make_banmen

        if ans_make_banmen == "false":
            print("make_banmen_error")
            return "false"
        else:
            core_list,path_list,new_path_list = ans_make_banmen

        #csv出力のためのresult(pp出力作ったので，いらないかも)
        #ppはパワポの略
        result = self.output_result(new_path_list)

        #show_output(size_info[0],size_info[1],size_info[2],result)

        #output_csv(banmen,result,exe_num,result_block_list,circuit_block)

        #coreの座標と端子方向のブロックの配線番号をまとめる
        #pathにcore座標を追加するため

        block_direction = self.make_block_direction(result_block_list)
    
        
        self.save_information(result_block_list,num_position_list,core_list,path_list,block_direction)

        path_list = self.make_perfect_path(result_block_list,path_list,block_direction)

        #各座標に配線番号とブロックの種類を情報に持つ3次元配列
        #実質，回路のレイアウト情報
        circuit = self.make_circuit_structure(result_block_list,path_list)

        #powerpointで3Dモデル作り
        self.output_pp_vba(circuit)


        #raphaelのための入力ファイル作り
        self.make_poly3D(circuit,new_path_list)

        

        #ここまでで，試行1回
        print("success")
        return "success"


    
        








            

    