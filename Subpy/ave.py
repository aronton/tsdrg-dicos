import os
import math
import time
import timeit
import sys
import tarfile
import datetime
import multiprocessing
import scriptCreator
from pathlib import Path
import shutil
import numpy as np



dicosPath = "/ceph/work/NTHU-qubit/LYT/tSDRG_random"
scopionPath = "/home/aronton/tSDRG_random"

if os.path.isdir(dicosPath):
    tSDRG_path = dicosPath
    group_path = dicosPath
    
if os.path.isdir(scopionPath):
    tSDRG_path = scopionPath
    group_path = scopionPath
    
sourcelist = {"ZL":"ZL.csv", "energy":"energy.csv", "seed":"s_re_seed.csv",\
    "corr1":"_".join(["L_re","P_re","m_re","s_re","corr1.csv"]), "corr2":"_".join(["L_re","P_re","m_re","s_re","corr2.csv"]),\
    "ZLI":"ZLI.csv", "ZLC":"ZLC.csv", "w_loc":"w_loc.csv", "J_list":"J_list.csv", "dimerization":"dimerization.csv",\
    "string":"_".join(["L_re","P_re","m_re","s_re","string.csv"])
    }

grouplist = {"ZL":"_".join(["L_re","P_re","m_re","s_re","ZL.txt"]), "energy":"_".join(["L_re","P_re","m_re","s_re","energy.txt"]),\
    "corr1":"_".join(["L_re","P_re","m_re","s_re","corr1.txt"]), "corr2":"_".join(["L_re","P_re","m_re","s_re","corr2.txt"]),\
    "ZLI":"_".join(["L_re","P_re","m_re","s_re","ZLI.txt"]), "ZLC":"_".join(["L_re","P_re","m_re","s_re","ZLC.txt"]),\
    "w_loc":"_".join(["L_re","P_re","m_re","s_re","w_loc.txt"]), "J_list":"_".join(["L_re","P_re","m_re","s_re","J_list.txt"]),\
    "string":"_".join(["L_re","P_re","m_re","s_re","string.txt"]), "seed":"_".join(["L_re","P_re","m_re","s_re","seed.txt"]),\
    "dimerization":"_".join(["L_re","P_re","m_re","s_re","dimerization.txt"])
    }

tarlist = {
    "ZL":"_".join(["ZL","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "energy":"_".join(["energy","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "corr1":"_".join(["corr1","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "corr2":"_".join(["corr2","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "ZLI":"_".join(["ZLI","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "ZLC":"_".join(["ZLC","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "w_loc":"_".join(["w_loc","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "J_list":"_".join(["J_list","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "string":"_".join(["string","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "seed":"_".join(["seed","L_re","P_re","m_re.txt"]),
    "dimerization":"_".join(["dimerization","L_re","P_re","m_re.txt"]),
    "ground":"_".join(["ground","L_re","P_re","m_re","J_re","D_re.txt"])
    }

metalist = {
    "ZL":"_".join(["ZL","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "energy":"_".join(["gap","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "corr1":"_".join(["corr1","L_re","P_re","m_re","J_re","D_re","dx_re.txt"]),\
    "corr2":"_".join(["corr2","L_re","P_re","m_re","J_re","D_re","dx_re.txt"]),\
    "dimerization":"_".join(["dimerization","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "ground":"_".join(["gap","L_re","P_re","m_re","J_re","D_re.txt"])
    }

metaDislist = {
    "ZL":"_".join(["ZL_dis","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "energy":"_".join(["gap_dis","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "corr1":"_".join(["corr1_dis","L_re","P_re","m_re","J_re","D_re","dx_re.txt"]),\
    "corr2":"_".join(["corr2_dis","L_re","P_re","m_re","J_re","D_re","dx_re.txt"]),\
    "dimerization":"_".join(["dimerization_dis","L_re","P_re","m_re","J_re","D_re.txt"]),\
    "ground":"_".join(["gap","L_re","P_re","m_re","J_re","D_re.txt"])
    }


def creatName(BC, J, D, L, P, m, phys):
    mySourceName = sourcelist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m) 
    myTargetName = tarlist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m) 
    groupSourceName = grouplist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m) 
    groupTargetName = tarlist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m) 
    groupAveName = metalist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    groupDisName = metaDislist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    return (mySourceName, groupSourceName, myTargetName, groupTargetName, groupAveName, groupDisName)


def creatDir(BC, J, D, L, P, m, phys):
    avePath = "/".join(["tSDRG","Main_15","metadata","BC_re","J_re","D_re","L_re_P_re_m_re_s_re"])
    sourcePath = "/".join(["tSDRG","Main_15","data_random","BC_re","J_re","D_re","L_re_P_re_m_re_s_re"])
    tarPath = "/".join(["tSDRG","Main_15","data_collect","BC_re","J_re","D_re","L_re_P_re_m_re"])
    mySourcePathBase = "/".join([tSDRG_path,sourcePath])
    groupSourcePathBase = "/".join([group_path,sourcePath])
    myTargetPathBase = "/".join([tSDRG_path,tarPath])
    groupTargetPathBase = "/".join([group_path,tarPath])
    avePathBase = "/".join([tSDRG_path,avePath])

    mySourcePath = mySourcePathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    groupSourcePath = groupSourcePathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    myTargetPath = myTargetPathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    groupTargetPath = groupTargetPathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    myAvePath = avePathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m).replace("s_re", "meta")
    myDisPath = avePathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m).replace("s_re", "dis")
 
    return (mySourcePath, groupSourcePath, myTargetPath, groupTargetPath, myAvePath, myDisPath)

def fread(f, phys):
    if os.path.exists(f):
        with open(f,"r") as a:
            a = a.readlines()
            if len(a) == 0:
                return 
            else:
                if phys in a[0].strip():
                    del a[0]
                a = "".join(a)
                a = a.replace("\n"," ")
                return a
    else:
        return 

def create_tarball_files(output_filename, file_list):
    with tarfile.open(output_filename, "w:gz") as tar:
        for file in file_list:
            tar.add(file, arcname=file)  # arcname 保持原始檔名
    print(f"已打包 {len(file_list)} 個檔案到 {output_filename}")

def kill_files(file_list):
    for i,f in enumerate(file_list):
        os.system("rm " + f)
    return f"已刪除 {len(file_list)} 個檔案，從{file_list[0]}到{file_list[-1]}"
    
def cp_files(file_list):
    for i,f in enumerate(file_list):
        os.system("cp " + f)
    print(f"已複製 {len(file_list)} 個檔案，從{file_list[0]}到{file_list[-1]}")



def parse_context(context):
    """
    將原始字串解析為鍵值對列表。
    """
    lines = [line.strip() for line in context.strip().split('\n') if line.strip()]
    pairs = []
    for line in lines:
        if ':' in line:
            key_value = line.split(':', 1)
            if len(key_value) == 2:
                key_str, value = key_value
                try:
                    key_int = int(key_str.strip())
                    pairs.append((key_int, value.strip()))
                except ValueError:
                    continue
    return pairs

def is_sorted(pairs):
    """
    檢查鍵值對列表是否已按鍵的升序排序。
    """
    return all(pairs[i][0] <= pairs[i + 1][0] for i in range(len(pairs) - 1))

def sort_context(pairs):
    """
    對鍵值對列表按鍵進行排序，並重建為字串格式。
    """
    sorted_pairs = sorted(pairs, key=lambda x: x[0])
    s1 = sorted_pairs[0][0]  # 假設第一個鍵是 s1
    sorted_lines = [f"{key}:{value}" for key, value in sorted_pairs]
    return '\n'.join(sorted_lines), s1

def sort_if_needed(context):
    """
    若資料未排序，則進行排序；否則返回原始資料。
    """
    pairs = parse_context(context)
    if is_sorted(pairs):
        print("資料已排序，無需排序。")
        s1 = int(pairs[0][0])  # 假設第一個鍵是 s1
        return context, s1
    else:
        print("資料未排序，開始排序。")
        return sort_context(pairs)
        
def Combine(BC, J, D, L, P, m, phys, s1, s2):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)

    mySourcePath = folder[0] + "/" + name[0]
    groupSourcePath = folder[1] + "/" + name[1]
    myTarPath = folder[2] + "/" + name[2]
    groupTarPath = folder[3] + "/" + name[3]

    seedArray = list(range(s1, s2 + 1))
    # with open(groupTarPath, "r") as originFile:
    #     originaText = originFile.readlines()
    context = ""
    # print("originaText")
    for seed in seedArray:
        groupSource = groupSourcePath.replace("s_re", str(seed))
        mySource = mySourcePath.replace("s_re", str(seed))
        # if f"{seed}:" in originaText[seed-1]:
        #     continue
        if os.path.exists(groupSource) and os.path.exists(mySource):
            if compare(groupSource, mySource, seed):                
                fcontext = fread(mySource, phys)
            else:
                # os.remove(groupSource)
                shutil.copy(mySource, groupSource)
                fcontext = fread(groupSource, phys)
        elif os.path.exists(mySource):
            # os.makedirs(os.path.dirname(groupSource), exist_ok=True)
            shutil.copy(mySource, groupSource)
            # os.remove(mySource)
            fcontext = fread(groupSource, phys)
        elif os.path.exists(groupSource):
            fcontext = fread(groupSource, phys)
        else:
            continue

        if fcontext is not None:
            context += f"{seed}:{fcontext}\n"

    if context != "":
        context, s1 = sort_if_needed(context)
        
        save_context(context, s1, groupTarPath, myTarPath, phys)
        # os.makedirs(os.path.dirname(myTarPath), exist_ok=True)


def save_context(context, s1, groupTarPath, myTarPath, phys):
    if not os.path.exists(groupTarPath):
        os.makedirs(os.path.dirname(groupTarPath), exist_ok=True)

    mode = "w" if s1 == 1 else "a"

    if s1 == 1:
        context = f"{phys}\n{context}"

    with open(groupTarPath, mode) as f1:
        try:
            # 嘗試非阻塞加鎖
            fcntl.flock(f1, fcntl.LOCK_EX | fcntl.LOCK_NB)
            print(f"✅ 立即取得鎖 [PID {os.getpid()}] ({'WRITE' if s1==1 else 'APPEND'}): {groupTarPath}")
        except BlockingIOError:
            print(f"⏳ 鎖住等待中 [PID {os.getpid()}] → {groupTarPath}")
            fcntl.flock(f1, fcntl.LOCK_EX)
            print(f"✅ 最終取得鎖 [PID {os.getpid()}]")

        try:
            f1.write(context)
        finally:
            fcntl.flock(f1, fcntl.LOCK_UN)
            print(f"🔓 檔案已解鎖 [PID {os.getpid()}] → {groupTarPath}")
            
    if phys == "ZL":
        save_ZL(BC, J, D, L, P, m, phys, groupTarPath)
    elif phys == "energy":
        save_gap(BC, J, D, L, P, m, phys, groupTarPath)
    elif phys == "corr1" or phys == "corr2":
        save_corr(BC, J, D, L, P, m, phys, groupTarPath)
        
def parameter_read_dict(filename):
    parameters = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key:
                        parameters[key] = value
    except FileNotFoundError:
        print(f"無法開啟檔案: {filename}")
    
    return parameters

def dimerAverage(BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    myTarPath = folder[2] + "/" + name[2]
    if path is not None:
        myTarPath = path
    dimerlist = []
    
    try:
        if not os.path.exists(myTarPath):
            raise FileNotFoundError
        auto_delete_empty = True
        if os.path.getsize(myTarPath) == 0:
            if auto_delete_empty:
                os.remove(myTarPath)
                print(f"[刪除] 空檔案已刪除：{myTarPath}")
            raise ValueError("檔案為空")
        with open(myTarPath, "r") as targetFile:
            dimerlist = targetFile.readlines()
            if type(dimerlist[0]) == str or dimerlist[0] == "dimerization":
                del dimerlist[0]
        dimerlist = [float(line.split(":")[-1]) for line in dimerlist]
        if not dimerlist:
            if auto_delete_empty:
                os.remove(myTarPath)
                print(f"[刪除] 空檔案已刪除：{myTarPath}")
            raise ValueError("檔案內容為空")
    except FileNotFoundError:
        print(f"File not found: {myTarPath}")
        return False, False, False
    except ValueError as e:
        print(f"跳過空檔案: {BC}, {J}, {D}, {L}, {P}, {m}, {phys} → {e}")
        return False, False, False
    save_dimerDistribute(dimerlist, BC, J, D, L, P, m, phys, myTarPath)
    dimerAve = np.mean(dimerlist)
    sample = len(dimerlist)
    error = np.std(dimerlist, ddof=1)

    return dimerAve, sample, error

def save_dimerDistribute(zllist, BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    dimerDisBase = folder[5] + "/" + name[5]
    context = "dimerization\n"
    for i, value in enumerate(zllist):
        context += f"{value}\n"
    if context == "dimerization\n":
        return
    else:
        if not os.path.exists(dimerDisBase):
            os.makedirs(os.path.dirname(dimerDisBase), exist_ok=True)
        with open(dimerDisBase, "w") as targetFile:
            targetFile.write(context)

def save_dimer(BC, J, D, L, P, m, phys, path=None):
    dimerization, sample, error = dimerAverage(BC, J, D, L, P, m, phys, path)
    if dimerization == False:
        print(f"Error: No data found for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")
        return
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    myTarPath = folder[4] + "/" + name[4]

    if not os.path.exists(myTarPath):
        os.makedirs(os.path.dirname(myTarPath), exist_ok=True)
    with open(myTarPath, "w") as targetFile:
        targetFile.write(f"dimerization, sample, errorbar\n{dimerization}, {sample}, {error/math.sqrt(sample)}")    
    print(f"dimerization, sample, errorbar\n{dimerization}, {sample}, {error/math.sqrt(sample)} for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")


def gapAverage(BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    myTarPath = folder[2] + "/" + name[2]
    if path is not None:
        myTarPath = path
    gaplist = []
    try:
        with open(myTarPath, "r") as targetFile:
            collect = targetFile.readlines()
            collect = [line.strip() for line in collect]
            if collect and collect[0] == "energy":
                del collect[0]
            # print("collect:", collect)
            for line in collect:
                line = line.split(":")[-1].split(" ")
                try:
                    gap = float(line[1]) - float(line[0])
                    gaplist.append(gap)
                except Exception as e:
                    print(e)
    except FileNotFoundError:
        print(f"File not found: {myTarPath}")
        return False, False, False
    save_gapDistribute(gaplist, BC, J, D, L, P, m, phys, myTarPath)
    gapAve = np.mean(gaplist)
    sample = len(gaplist) 
    error = np.std(gaplist, ddof=1)

    return gapAve, sample, error

def save_gapDistribute(gaplist, BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    gapDisBase = folder[5] + "/" + name[5]
    context = "ground_state_gap\n"
    for i, value in enumerate(gaplist):
        context += f"{value}\n"
    
    if context == "ground_state_gap\n":
        return
    else:
        if not os.path.exists(gapDisBase):
            os.makedirs(os.path.dirname(gapDisBase), exist_ok=True)
        with open(gapDisBase, "w") as targetFile:
            targetFile.write(context)

def save_gap(BC, J, D, L, P, m, phys, path=None):
    gapAve, sample, error = gapAverage(BC, J, D, L, P, m, phys, path)
    if gapAve == False:
        print(f"Error: No data found for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")
        return
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    myTarPath = folder[4] + "/" + name[4]
    # print(f"myTarPath:{myTarPath}")
    if not os.path.exists(myTarPath):
        os.makedirs(os.path.dirname(myTarPath), exist_ok=True)
    with open(myTarPath, "w") as targetFile:
        targetFile.write(f"ground_state_energy, sample, errorbar\n{gapAve}, {sample}, {error/math.sqrt(sample)}")
    print(f"ground_state_energy, sample, errorbar\n{gapAve}, {sample}, {error/math.sqrt(sample)} for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")


def gap2ndAverage(BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    myTarPath = folder[2] + "/" + (name[2].replace("gap", "gap2"))
    if path is not None:
        myTarPath = path
    gaplist = []
    try:
        with open(myTarPath, "r") as targetFile:
            collect = targetFile.readlines()
            collect = [line.strip() for line in collect]
            if collect and collect[0] == "energy":
                del collect[0]
            # print("collect:", collect)
            for line in collect:
                line = line.split(":")[-1].split(" ")
                try:
                    gap2 = float(line[2]) - float(line[1])
                    gaplist.append(gap2)
                except Exception as e:
                    print(e)
    except FileNotFoundError:
        print(f"File not found: {myTarPath}")
        return False, False, False
    save_gap2ndDistribute(gaplist, BC, J, D, L, P, m, phys, myTarPath)
    gapAve = np.mean(gaplist)
    sample = len(gaplist) 
    error = np.std(gaplist, ddof=1)

    return gapAve, sample, error

def save_gap2ndDistribute(gaplist, BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    gapDisBase = folder[5] + "/" + (name[5].replace("gap", "gap2"))
    context = "2ndgap\n"
    for i, value in enumerate(gaplist):
        context += f"{value}\n"
    
    if context == "2ndgap\n":
        return
    else:
        if not os.path.exists(gapDisBase):
            os.makedirs(os.path.dirname(gapDisBase), exist_ok=True)
        with open(gapDisBase, "w") as targetFile:
            targetFile.write(context)

def save_gap2nd(BC, J, D, L, P, m, phys, path=None):
    gapAve, sample, error = gap2ndAverage(BC, J, D, L, P, m, phys, path)
    if gapAve == False:
        print(f"Error: No data found for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")
        return
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    myTarPath = folder[4] + "/" + (name[4].replace("gap", "gap2"))
    # print(f"myTarPath:{myTarPath}")
    if not os.path.exists(myTarPath):
        os.makedirs(os.path.dirname(myTarPath), exist_ok=True)
    with open(myTarPath, "w") as targetFile:
        targetFile.write(f"2ndgap, sample, errorbar\n{gapAve}, {sample}, {error/math.sqrt(sample)}")
    print(f"2ndgap, sample, errorbar\n{gapAve}, {sample}, {error/math.sqrt(sample)} for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")
    

   
def corrAverage(BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    myTarPath = folder[2] + "/" + name[2]
    if path is not None:
        myTarPath = path
    corrDic = {}
    try:
        with open(myTarPath, "r") as targetFile:
            collect = targetFile.readlines()
            collect = [line.strip() for line in collect]
            if collect and collect[0] == "corr1":
                del collect[0]
            # print("collect:", collect)
            for line in collect:
                line = line.split(":")[-1].split(" ")
                for data in line:
                    if data:
                        parts = data.split(",")
                        if len(parts) >= 3:
                            try:
                                x1, x2 = int(parts[0]), int(parts[1])
                                corr = float(parts[2])
                                key = x2 - x1
                                if key not in corrDic:
                                    corrDic[key] = []
                                corrDic[key].append(corr*(-1)**key)
                            except ValueError:
                                continue  # 忽略無法轉換的數據
    except FileNotFoundError:
        print(f"File not found: {myTarPath}")
        return False, False, False
    save_corrDistribute(corrDic, BC, J, D, L, P, m, phys)
    corr = {}
    sample = {}
    error = {}
    for key, values in corrDic.items():
        sample[key] = len(values)
        corr[key] = np.mean(values)
        error[key] = np.std(values, ddof=1) if len(values) > 1 else 0.0

    return corr, sample, error

def save_corrDistribute(corrDic, BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    corrDisBase = folder[5] + "/" + name[5]
    for key, values in list(corrDic.items())[-4:]:
        if BC == "OBC":
            if key < int(L[1::])-5:
                continue
        context = ""
        if BC == "OBC":
            context = f"C_etoe=<S(0)S(dx={key})>*(-1)^{key}\n"
        elif BC == "PBC":
            context = f"C_bulk=<S(0)S(dx={key})>*(-1)^{key}\n"
        corrDisPath = corrDisBase.replace("dx_re", f"dx={key}")
        for value in values:
            context += f"{value}\n"
        
        if context == f"C_etoe=<S(0)S(dx={key})>*(-1)^{key}\n" or context ==  f"C_bulk=<S(0)S(dx={key})>*(-1)^{key}\n":
            continue
        else:
            if not os.path.exists(corrDisPath):
                os.makedirs(os.path.dirname(corrDisPath), exist_ok=True)
            with open(corrDisPath, "w") as targetFile:
                targetFile.write(context)

def save_corr(BC, J, D, L, P, m, phys, path=None):
    corr, sample, error = corrAverage(BC, J, D, L, P, m, phys, path)
    if corr == False:
        print(f"Error: No data found for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")
        return
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    myTarPathBase = folder[4] + "/" + name[4]
    # print(f"myTarPath:{myTarPath}")
    for key, values in list(corr.items()):
        if BC == "OBC":
            if key < int(L[1::])-5:
                continue
        if corr[key] == None:
            continue
        myTarPath = myTarPathBase.replace("dx_re", f"dx={key}")
        if BC == "OBC":
            context = f"C_etoe=<S(0)S(dx={key})>*(-1)^{key},sample,errorbar\n" + f"{corr[key]},{sample[key]},{error[key]/math.sqrt(sample[key])}"
        elif BC == "PBC":
            context = f"C_bulk=<S(0)S(dx={key})>*(-1)^{key},sample,errorbar\n" + f"{corr[key]},{sample[key]},{error[key]/math.sqrt(sample[key])}"
        if not os.path.exists(myTarPath):
            os.makedirs(os.path.dirname(myTarPath), exist_ok=True)
        with open(myTarPath, "w") as targetFile:
            targetFile.write(context)
        if BC == "PBC":
            print(f"C_bulk=<S(0)S(dx={key})>*(-1)^{key},sample,errorbar\n" + f"{corr[key]},{sample[key]},{error[key]/math.sqrt(sample[key])} for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")
        else:    
            print(f"C_etoe=<S(0)S(dx={key})>*(-1)^{key},sample,errorbar\n" + f"{corr[key]},{sample[key]},{error[key]/math.sqrt(sample[key])} for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")
            

# def save_ground(BC, J, D, L, P, m, phys, path=None):
#     folder = creatDir(BC, J, D, L, P, m, phys)
#     name = creatName(BC, J, D, L, P, m, phys)
#     # print( f"folder[4]:{folder[4]}")
#     myTarPath = folder[2] + "/" + name[2]
#     gapDisBase = folder[5] + "/" + name[5]
#     shutil.copy(myTarPath, gapDisBase)
#     gapAveBase = folder[4] + "/" + name[4]
#     # if gapDisBase[0] == "ground_state_gap"
#     # gaplist
#     if not os.path.exists(myTarPath):
#         os.makedirs(os.path.dirname(myTarPath), exist_ok=True)
#     with open(myTarPath, "w") as targetFile:
#         targetFile.write(f"ground_state_energy, sample, errorbar\n{gapAve}, {sample}, {error/math.sqrt(sample)}")
#     print(f"ground_state_energy, sample, errorbar\n{gapAve}, {sample}, {error/math.sqrt(sample)} for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")
            

def ZLAverage(BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    myTarPath = folder[2] + "/" + name[2]
    if path is not None:
        myTarPath = path
    zllist = []
    
    try:
        if not os.path.exists(myTarPath):
            raise FileNotFoundError
        auto_delete_empty = True
        if os.path.getsize(myTarPath) == 0:
            if auto_delete_empty:
                os.remove(myTarPath)
                print(f"[刪除] 空檔案已刪除：{myTarPath}")
            raise ValueError("檔案為空")
        with open(myTarPath, "r") as targetFile:
            zllist = targetFile.readlines()
            if type(zllist[0]) == str or zllist[0] == "ZL":
                del zllist[0]
        zllist = [float(line.split(":")[-1]) for line in zllist]
        if not zllist:
            if auto_delete_empty:
                os.remove(myTarPath)
                print(f"[刪除] 空檔案已刪除：{myTarPath}")
            raise ValueError("檔案內容為空")
    except FileNotFoundError:
        print(f"File not found: {myTarPath}")
        return False, False, False
    except ValueError as e:
        print(f"跳過空檔案: {BC}, {J}, {D}, {L}, {P}, {m}, {phys} → {e}")
        return False, False, False
    save_zlDistribute(zllist, BC, J, D, L, P, m, phys, myTarPath)
    zlAve = np.mean(zllist)
    sample = len(zllist)
    error = np.std(zllist, ddof=1)

    return zlAve, sample, error

def save_zlDistribute(zllist, BC, J, D, L, P, m, phys, path=None):
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    zlDisBase = folder[5] + "/" + name[5]
    context = "ZL\n"
    for i, value in enumerate(zllist):
        context += f"{value}\n"
    if context == "ZL\n":
        return
    else:
        if not os.path.exists(zlDisBase):
            os.makedirs(os.path.dirname(zlDisBase), exist_ok=True)
        with open(zlDisBase, "w") as targetFile:
            targetFile.write(context)

def save_ZL(BC, J, D, L, P, m, phys, path=None):
    zlAve, sample, error = ZLAverage(BC, J, D, L, P, m, phys, path)
    if zlAve == False:
        print(f"Error: No data found for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")
        return
    folder = creatDir(BC, J, D, L, P, m, phys)
    name = creatName(BC, J, D, L, P, m, phys)
    # print( f"folder[4]:{folder[4]}")
    myTarPath = folder[4] + "/" + name[4]

    if not os.path.exists(myTarPath):
        os.makedirs(os.path.dirname(myTarPath), exist_ok=True)
    with open(myTarPath, "w") as targetFile:
        targetFile.write(f"ZL, sample, errorbar\n{zlAve}, {sample}, {error/math.sqrt(sample)}")    
    print(f"ZL, sample, errorbar\n{zlAve}, {sample}, {error/math.sqrt(sample)} for {BC}, {J}, {D}, {L}, {P}, {m}, {phys}")

def list_txt_files(directory):
    txt_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                full_path = os.path.join(root, file)
                txt_files.append(full_path)
    return txt_files

if __name__ == "__main__":
    file = sys.argv[1]
    arg = []
    a = scriptCreator.para("read",file)
    parameterlist = a.para
    para=scriptCreator.paraList1(parameterlist["L"],parameterlist["J"],parameterlist["D"],parameterlist["S"])
    BC = parameterlist["BC"]
    Pdis = parameterlist["Pdis"]
    chi = str(parameterlist["chi"])
    s1 = int(sys.argv[2])
    s2 = int(sys.argv[3])

    for D in para.D_str:
        for L in para.L_str:
            for J in para.J_str:
                save_corr(BC, J, D, L, f"P{Pdis}", f"m{chi}", "corr1")    
                save_corr(BC, J, D, L, f"P{Pdis}", f"m{chi}", "corr2")
                save_ZL(BC, J, D, L, f"P{Pdis}", f"m{chi}", "ZL")  
                save_dimer(BC, J, D, L, f"P{Pdis}", f"m{chi}", "dimerization")  
                # save_ground(BC, J, D, L, f"P{Pdis}", f"m{chi}", "ground")   
                save_gap(BC, J, D, L, f"P{Pdis}", f"m{chi}", "energy")   
                save_gap2nd(BC, J, D, L, f"P{Pdis}", f"m{chi}", "energy")  
                 