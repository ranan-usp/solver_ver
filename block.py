from hspice import exe_netlist
from itertools import count
import numpy as np
import random
import global_value as g
import pprint
import copy


class Block():

    def __init__(self,num,banmen,block_info,position_fix,count_fix,pos_candidate) -> None:
        self.ini_block_info = block_info
        self.ini_fix = [position_fix,count_fix]

        self.num = num
        self.banmen = banmen
        self.block_type = block_info[0]
        self.block_size_x = block_info[1][0]
        self.block_size_y = block_info[1][1]
        self.num_list = block_info[2]
        self.position_x = None
        self.position_y = None
        self.position_z = None
        self.roulette = random.choice(["u","r","d","l"])
        self.conv = random.choice([0,1])
        self.posture = None
        self.pos_candidate = pos_candidate

        self.position_fix = position_fix
        self.count_fix = count_fix

        self.pos_list = []
        self.position_list = []
        self.bangou_list = []
        self.core_duplicate = []

        self.param = []
        self.num_position_list = []
        self.pos_info = []

    def __del__(self):
        pass

    def initialization(self):

        self.block_type = self.ini_block_info[0]
        self.block_size_x = self.ini_block_info[1][0]
        self.block_size_y = self.ini_block_info[1][1]
        self.num_list = self.ini_block_info[2]
        self.position_x = None
        self.position_y = None
        self.position_z = None
        self.roulette = random.choice(["u","r","d","l"])
        self.conv = random.choice([0,1])
        self.posture = None

        self.pos_list = []
        self.position_list = []
        self.bangou_list = []
        self.core_duplicate = []

        return "succenss"

    def conversion(self):
         #反転するか否か
        
        num_list_temp = np.array(self.num_list)
        num_list_temp = np.reshape(num_list_temp,(self.block_size_y,self.block_size_x))
        for j in range(len(num_list_temp)):
            for i in range(self.block_size_x//2):
                temp = num_list_temp[j][i]
                num_list_temp[j][i] = num_list_temp[j][self.block_size_x-1-i]
                num_list_temp[j][self.block_size_x-1-i] = temp

        num_list_temp = np.reshape(num_list_temp,self.block_size_x*self.block_size_y)

        self.num_list = num_list_temp.tolist()

        return "success"

    def rotation(self):
        #回転方向決定
        
        #回転というか，num_listの順番入れ替えとx,y方向の長さの変更
        if self.roulette == "u":
            #print(roulette,num_list)
            return "success"

        elif self.roulette == "r":
            new_num_list = list()
            for i in range(self.block_size_x):
                for j in range(self.block_size_y-1,-1,-1):
                    new_num_list.append(self.num_list[j*self.block_size_x+i])
            #print(roulette,new_num_list)

            self.num_list = new_num_list
            temp = self.block_size_x
            self.block_size_x = self.block_size_y
            self.block_size_y = temp
            return "success"

        elif self.roulette == "d":
            new_num_list = list(reversed(self.num_list))
            self.num_list = new_num_list
            return "success"
        
        elif self.roulette == "l":
            new_num_list = list()
            for i in range(self.block_size_x-1,-1,-1):
                for j in range(self.block_size_y):
                    new_num_list.append(self.num_list[i+self.block_size_x*j])
            #print(roulette,new_num_list)

            self.num_list = new_num_list
            temp = self.block_size_x
            self.block_size_x = self.block_size_y
            self.block_size_y = temp
            return "success"

    def ini_position(self):
        pos_candidate_x,pos_candidate_y,pos_candidate_z = self.pos_candidate
        width_x,width_y,height = self.banmen
        
        while True:
            self.position_x = random.choice(pos_candidate_x)
            if self.position_x+self.block_size_x-1 < width_x-1:
                break
        #y座標決定
        #pos_y = random.choices(pos_candidate_y,weights = weights_list_y)[0]
        
        while True:
            self.position_y = random.choice(pos_candidate_y)
            if self.position_y+self.block_size_y-1 < width_y-1:
                break

        if self.block_type == "b":
            self.position_z = random.choice(pos_candidate_z)
            if self.position_z == 0:
                self.posture = random.choice(["stand_up","not_stand"])
            elif self.position_z == height-1:
                self.posture = random.choice(["stand_under","not_stand"])
            else:
                self.posture = random.choice(["stand_up","stand_under","stand_super","not_stand"])
            
        elif self.block_type == "f":
            self.position_z = random.choice(pos_candidate_z)
            self.posture = "not_stand"

        else:
            self.position_z = 0
            self.posture = "not_stand"

        return "success"

    def position_sit(self):

        self.bangou_list = []
        self.pos_list = []
        self.position_list = []
        
        #num_listのカウンター
        count = 0
        
        for i in range(self.block_size_y):
            for j in range(self.block_size_x):
                #n = num_list[i*block_size_x+j]
                n = self.num_list[count]
                
                count += 1

                #座標決定
                pos = (self.block_size_x+j,self.position_y+i,self.position_z)

                self.position_list.append(pos)

                if n == "0":
                    continue

                if n == "-1":
                    self.pos_list.append(pos)
                    continue

                #配線番号取り出し，sとかgついてるから，splitする
                bangou = int(n.split("-")[0])-1

                if g.hantei[bangou] == 0:
                    g.num_pos[bangou+1] = pos
                    g.hantei[bangou] = 1
                    self.pos_list.append(pos)
                    self.bangou_list.append(bangou)
                elif g.hantei[bangou] == 1:
                    if pos != g.num_pos[bangou+1]:
                        #同じ番号において，初めに代入した座標とは違うときは，pos_list（かぶり判定用）に入れる．
                        #BLCOK内の座標まとめる
                        self.pos_list.append(pos)
        
        #数字ペアの座標がお互いのコアの座標であれば，被り判定すり抜け
        core_index_list = [i for i, x in enumerate(self.num_list) if x == "-1"]
        for core_index in core_index_list:
            core_pos = self.position_list[core_index]
            surrounding_core_pos = [(core_pos[0]+1,core_pos[1],core_pos[2]),(core_pos[0]-1,core_pos[1],core_pos[2]),
                                    (core_pos[0],core_pos[1]+1,core_pos[2]),(core_pos[0],core_pos[1]-1,core_pos[2]),
                                    (core_pos[0],core_pos[1],core_pos[2]+1),(core_pos[0],core_pos[1],core_pos[2]-1),]
            for s_core_pos in surrounding_core_pos:
                try:
                    surround_num_index = self.position_list.index(s_core_pos)
                except ValueError:
                    continue
                num = self.num_list[surround_num_index]
                if num not in ["-1","0"]:
                    bangou = int(num.split("-")[0])
                    if bangou not in g.num_core_pos_dict:
                        g.num_core_pos_dict[bangou] = [s_core_pos,core_pos]
                        self.core_duplicate.append(bangou)
                    else:
                        exist_s_core_pos,exist_core_pos = g.num_core_pos_dict[bangou]
                        if exist_s_core_pos == core_pos and exist_core_pos == s_core_pos:
                            
                            self.pos_list.remove(s_core_pos)
       
        return "success"

    def position_stand(self):
        self.bangou_list = []
        self.pos_list = []
        self.position_list = []
        
        #num_listのカウンター
        count = 0

        flag = 0
        flag_first = 0
        flag_second = 0

        if self.block_size_x > self.block_size_y:
            flag = 1
            range_horizonal = self.block_size_x
            range_vertical = self.block_size_y
            if "-1" not in self.num_list[:self.block_size_x]:
                flag_first = 1
                num_list_temp = self.num_list[self.block_size_x:] + self.num_list[:self.block_size_x]
            else:
                num_list_temp = self.num_list

        else:
            range_horizonal = self.block_size_y
            range_vertical = self.block_size_x
            #左側にないとき
            if "-1" not in self.num_list[0:len(self.num_list):2]:
                flag_second = 1
                num_list_temp = self.num_list[1:len(self.num_list):2] + self.num_list[0:len(self.num_list):2]
            #左側にあるとき
            else:
                num_list_temp = self.num_list[0:len(self.num_list):2] + self.num_list[1:len(self.num_list):2]

        for i in range(range_vertical):
            for j in range(range_horizonal):

                #n = num_list[i*block_size_x+j]
                n = num_list_temp[count]

                count += 1
                
                #座標決定
                if flag == 1 and self.posture == "stand_up":
                    pos = (self.position_x+j,self.position_y,self.position_z+i)
                elif flag == 1 and self.posture == "stand_under":
                    pos = (self.position_x+j,self.position_y,self.position_z-i)
                elif flag == 0 and self.posture == "stand_up":
                    pos = (self.position_x,self.position_y+j,self.position_z+i)
                elif flag == 0 and self.posture == "stand_under":
                    pos = (self.position_x,self.position_y+j,self.position_z-i)
                    
                self.position_list.append(pos)

                # n == "0" はかぶり判定なし
                if n == "0":
                    continue

                # n == "-1"において，侵入禁止のため，かぶり判定あり（例外なし）
                if n == "-1":
                    self.pos_list.append(pos)
                    continue

                #配線番号取り出し，sとかgついてるから，splitする
                # ex) 1-s,9-g
                
                bangou = int(n.split("-")[0])-1

                #一度も，その番号での座標が決定されていない
                if g.hantei[bangou] == 0:
                    #その番号での座標を格納(一度目)      
                    g.num_pos[bangou+1] = pos
                    #一度，その番号の座標を格納すれば洋ナシ
                    g.hantei[bangou] = 1
                    #一度目なので，pos_list格納（二度目で同じ座標であったときは，pos_listに入れなくてよい）
                    self.pos_list.append(pos)
                    #この関数で，処理した番号の記憶
                    self.bangou_list.append(bangou)
                #すでに格納済み
                elif g.hantei[bangou] == 1:

                    if pos != g.num_pos[bangou+1]:
                        #同じ番号において，初めに代入した座標とは違うときは，pos_list（かぶり判定用）に入れる．
                        self.pos_list.append(pos)

        temp_list = []
        # x軸方向の分岐ブロックにおいて，num_listを入れ替えたので，戻す
        # flag == 1 and flag_first == 0 においては，何もしていないのでそのままで可
        if flag == 1:
            if flag_first == 1:
                temp_list = self.position_list[self.block_size_x:] + self.position_list[:self.block_size_x]
            else:
                temp_list = self.position_list[:self.block_size_x] + self.position_list[self.block_size_x:]

        # flag == 0 -> block_size_y > block_size_x
        # y軸方向に座標をずらすため，一時的にnum_listの変更があり，元のnum_listと座標を対応させるために，工夫が必要
        else:
            #flag_secound == 1 -> 分岐ブロックのcore(-1)が右側に所属しているとき
            if flag_second == 1:
                for i in range(self.block_size_y):
                    temp_list.extend([self.position_list[self.block_size_y:][i],self.position_list[:self.block_size_y][i]])

            #flag_secound == 0 -> 左側に所属しているとき
            else:
                for i in range(self.block_size_y):
                    temp_list.extend([self.position_list[:self.block_size_y][i],self.position_list[self.block_size_y:][i]])

        self.position_list = temp_list

        #数字ペアの座標がお互いのコアの座標であれば，被り判定すり抜け
        core_index_list = [i for i, x in enumerate(self.num_list) if x == "-1"]
        for core_index in core_index_list:
            core_pos = self.position_list[core_index]
            surrounding_core_pos = [(core_pos[0]+1,core_pos[1],core_pos[2]),(core_pos[0]-1,core_pos[1],core_pos[2]),
                                    (core_pos[0],core_pos[1]+1,core_pos[2]),(core_pos[0],core_pos[1]-1,core_pos[2]),
                                    (core_pos[0],core_pos[1],core_pos[2]+1),(core_pos[0],core_pos[1],core_pos[2]-1),]
            for s_core_pos in surrounding_core_pos:
                try:
                    surround_num_index = self.position_list.index(s_core_pos)
                except ValueError:
                    continue
                num = self.num_list[surround_num_index]
                if num not in ["-1","0"]:
                    bangou = int(num.split("-")[0])
                    if bangou not in g.num_core_pos_dict:
                        self.core_duplicate.append(bangou)
                        g.num_core_pos_dict[bangou] = [s_core_pos,core_pos]
                    else:
                        exist_s_core_pos,exist_core_pos = g.num_core_pos_dict[bangou]
                        if exist_s_core_pos == core_pos and exist_core_pos == s_core_pos:
                            
                            self.pos_list.remove(s_core_pos)

        return "success"

    def position_super(self):

        self.bangou_list = []
        self.pos_list = []
        self.position_list = []
        
        #num_listのカウンター
        count = 0
        flag = 0

        if self.block_size_x > self.block_size_y:
            flag = 1
            range_horizonal = self.block_size_y
            range_vertical = self.block_size_x
        else:
            range_horizonal = self.block_size_x
            range_vertical = self.block_size_y
            
        if flag == 1:
            for i in range(range_horizonal):
                for j in range(1,-2,-1):

                    #n = num_list[i*block_size_x+j]
                    n = self.num_list[count]
                    count += 1
                    pos = (self.position_x,self.position_y+i,self.position_z+j)
                        
                    self.position_list.append(pos)

                    # n == "0" はかぶり判定なし
                    if n == "0":
                        continue

                    # n == "-1"において，侵入禁止のため，かぶり判定あり（例外なし）
                    if n == "-1":
                        self.pos_list.append(pos)
                        continue

                    #配線番号取り出し，sとかgついてるから，splitする
                    # ex) 1-s,9-g
                    
                    bangou = int(n.split("-")[0])-1

                    #一度も，その番号での座標が決定されていない
                    if g.hantei[bangou] == 0:
                        #その番号での座標を格納(一度目)      
                        g.num_pos[bangou+1] = pos
                        #一度，その番号の座標を格納すれば洋ナシ
                        g.hantei[bangou] = 1
                        #一度目なので，pos_list格納（二度目で同じ座標であったときは，pos_listに入れなくてよい）
                        self.pos_list.append(pos)
                        #この関数で，処理した番号の記憶
                        self.bangou_list.append(bangou)
                    #すでに格納済み
                    elif g.hantei[bangou] == 1:

                        if pos != g.num_pos[bangou+1]:
                            #同じ番号において，初めに代入した座標とは違うときは，pos_list（かぶり判定用）に入れる．
                            self.pos_list.append(pos)

        else:
            for i in range(1,-2,-1):
                for j in range(range_horizonal):

                    #n = num_list[i*block_size_x+j]
                    n = self.num_list[count]
                    count += 1
                    pos = (self.position_x+j,self.position_y,self.position_z+i)
                        
                    self.position_list.append(pos)

                    # n == "0" はかぶり判定なし
                    if n == "0":
                        continue

                    # n == "-1"において，侵入禁止のため，かぶり判定あり（例外なし）
                    if n == "-1":
                        self.pos_list.append(pos)
                        continue

                    #配線番号取り出し，sとかgついてるから，splitする
                    # ex) 1-s,9-g
                    
                    bangou = int(n.split("-")[0])-1

                    #一度も，その番号での座標が決定されていない
                    if g.hantei[bangou] == 0:
                        #その番号での座標を格納(一度目)      
                        g.num_pos[bangou+1] = pos
                        #一度，その番号の座標を格納すれば洋ナシ
                        g.hantei[bangou] = 1
                        #一度目なので，pos_list格納（二度目で同じ座標であったときは，pos_listに入れなくてよい）
                        self.pos_list.append(pos)
                        #この関数で，処理した番号の記憶
                        self.bangou_list.append(bangou)
                    #すでに格納済み
                    elif g.hantei[bangou] == 1:

                        if pos != g.num_pos[bangou+1]:
                            #同じ番号において，初めに代入した座標とは違うときは，pos_list（かぶり判定用）に入れる．
                            self.pos_list.append(pos)

        #数字ペアの座標がお互いのコアの座標であれば，被り判定すり抜け
        core_index_list = [i for i, x in enumerate(self.num_list) if x == "-1"]
        for core_index in core_index_list:
            core_pos = self.position_list[core_index]
            surrounding_core_pos = [(core_pos[0]+1,core_pos[1],core_pos[2]),(core_pos[0]-1,core_pos[1],core_pos[2]),
                                    (core_pos[0],core_pos[1]+1,core_pos[2]),(core_pos[0],core_pos[1]-1,core_pos[2]),
                                    (core_pos[0],core_pos[1],core_pos[2]+1),(core_pos[0],core_pos[1],core_pos[2]-1),]
            for s_core_pos in surrounding_core_pos:
                try:
                    surround_num_index = self.position_list.index(s_core_pos)
                except ValueError:
                    continue
                num = self.num_list[surround_num_index]
                if num not in ["-1","0"]:
                    bangou = int(num.split("-")[0])
                    if bangou not in g.num_core_pos_dict:
                        g.num_core_pos_dict[bangou] = [s_core_pos,core_pos]
                        self.core_duplicate.append(bangou)
                    else:
                        exist_s_core_pos,exist_core_pos = g.num_core_pos_dict[bangou]
                        if exist_s_core_pos == core_pos and exist_core_pos == s_core_pos:
                            
                            self.pos_list.remove(s_core_pos)
        return "success"

    def start(self):
       
        if self.block_type == "f":
            
            position = self.position_fix[g.count_fix]

            g.count_fix += 1
            #境界条件ブロックなので，回転なし，反転なし，サイズは1×1
            self.roulette = "x"
            self.conv = "x"
            self.posture = "not_stand"

            self.position_list = [position]
            n = copy.deepcopy(self.num_list[0])
            bangou = int(n.split("-")[0])-1
            g.hantei[bangou] = 1
            g.num_pos[bangou+1] = position
            g.pos_set |= set([position])
            
            g.fix_where.append(self.num+1)
            g.fix_pos.append(position)
            g.fix_pos_num.append(bangou+1)

            return "success"

        else:
            count_out = 0

            while True:

                res = self.initialization()
                
                res = self.ini_position()
                
                res = self.conversion()
               
                res = self.rotation()

                if self.posture == "not_stand":
                    res = self.position_sit()
                elif self.posture == "stand_super":
                    res = self.position_super()
                else:
                    res = self.position_stand()

                #かぶり判定,len(duplicate)==0ならかぶりなし
                
                depulicate = list(set(self.pos_list) & g.pos_set)

                if count_out > 300:
                
                    return "false"
                
                if len(depulicate) == 0:
                
                    #loop解除のためのflag=0
                    #他の座標とかぶらないためのset
                    
                    g.pos_set |= set(self.pos_list)
                    if self.block_type == "b":
                        g.bunki_where.append(self.num+1)
                    
                    return "success"

                else:

                    for bango in self.core_duplicate:
                        temp = g.num_core_pos_dict.pop(bango)
                    for bango in self.bangou_list:
                        g.hantei[bango] = 0
                    
                    count_out += 1

    def out_param(self):

        temp_num_list = ["0"] * len(self.num_list)

        for i,num in enumerate(self.num_list):
            if "s" in num or "g" in num:
                self.pos_info.append([num,self.position_list[i]])
                num = num.split("-")[0]
            temp_num_list[i] = int(num)

        self.param.append([self.roulette,self.conv,self.posture])
        self.param.append(temp_num_list)
        self.param.append([self.block_size_x,self.block_size_y])
        self.param.append(self.position_list)

        count_pos = 0
        #BLOCKは，番号を持たない0をもっているため，0の座標以外の座標まとめ
        #print(num_list)
        for i in range(self.block_size_y):
            for j in range(self.block_size_x):

                n = self.num_list[count_pos]
                pos = self.position_list[count_pos]
               
                count_pos += 1
                if n == "0":
                    continue

                #print(n,pos_temp)
                #print(pos_temp)
                self.num_position_list.append([n,pos])

        return self.param,self.num_position_list,self.pos_info


        

            





        