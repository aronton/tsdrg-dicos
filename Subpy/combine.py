import os
import math
import time
import timeit
import numpy as np
import sys
import tarfile
import datetime
import multiprocessing
import scriptCreator
from pathlib import Path
import shutil
import fcntl

LOCK_SUFFIX = ".lock"

dicosPath = "/ceph/work/NTHU-qubit/LYT/tSDRG_random"
scopionPath = "/home/aronton/tSDRG_random"

if os.path.isdir(dicosPath):
    tSDRG_path = dicosPath
    group_path = dicosPath
    
if os.path.isdir(scopionPath):
    tSDRG_path = scopionPath
    group_path = scopionPath
    
# sourcelist = {"ZL":"ZL.csv", "energy":"energy.csv", "seed":"s_re_seed.csv",\
#     "corr1":"_".join(["L_re","P_re","m_re","s_re","corr1.csv"]), "corr2":"_".join(["L_re","P_re","m_re","s_re","corr2.csv"]),\
#     "ZLI":"ZLI.csv", "ZLC":"ZLC.csv", "w_loc":"w_loc.csv", "J_list":"J_list.csv", "dimerization":"dimerization.csv",\
#     "string":"_".join(["L_re","P_re","m_re","s_re","string.csv"])
#     }
sourcelist = {"ZL":"_".join(["L_re","P_re","m_re","s_re","ZL.txt"]), "energy":"_".join(["L_re","P_re","m_re","s_re","energy.txt"]),\
    "corr1":"_".join(["L_re","P_re","m_re","s_re","corr1.txt"]), "corr2":"_".join(["L_re","P_re","m_re","s_re","corr2.txt"]),\
    "ZLI":"_".join(["L_re","P_re","m_re","s_re","ZLI.txt"]), "ZLC":"_".join(["L_re","P_re","m_re","s_re","ZLC.txt"]),\
    "w_loc":"_".join(["L_re","P_re","m_re","s_re","w_loc.txt"]), "J_list":"_".join(["L_re","P_re","m_re","s_re","J_list.txt"]),\
    "string":"_".join(["L_re","P_re","m_re","s_re","string.txt"]), "seed":"_".join(["L_re","P_re","m_re","s_re","seed.txt"]),\
    "dimerization":"_".join(["L_re","P_re","m_re","s_re","dimerization.txt"]),
    "ground":"_".join(["L_re","P_re","m_re","s_re","energy.txt"])
    }

grouplist = {"ZL":"_".join(["L_re","P_re","m_re","s_re","ZL.txt"]), "energy":"_".join(["L_re","P_re","m_re","s_re","energy.txt"]),\
    "corr1":"_".join(["L_re","P_re","m_re","s_re","corr1.txt"]), "corr2":"_".join(["L_re","P_re","m_re","s_re","corr2.txt"]),\
    "ZLI":"_".join(["L_re","P_re","m_re","s_re","ZLI.txt"]), "ZLC":"_".join(["L_re","P_re","m_re","s_re","ZLC.txt"]),\
    "w_loc":"_".join(["L_re","P_re","m_re","s_re","w_loc.txt"]), "J_list":"_".join(["L_re","P_re","m_re","s_re","J_list.txt"]),\
    "string":"_".join(["L_re","P_re","m_re","s_re","string.txt"]), "seed":"_".join(["L_re","P_re","m_re","s_re","seed.txt"]),\
    "dimerization":"_".join(["L_re","P_re","m_re","s_re","dimerization.txt"]),
    "ground":"_".join(["L_re","P_re","m_re","s_re","energy.txt"])
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
            

def checkInside(s, f, sample, phys):
    with open(f,"r") as a:
        a = a.readlines()    
        if a[0].strip() == phys:
            del a[0]
        data = [(v.split(":")[0].strip(),(v.split(":")[1].replace("\n"," ").strip())) for i,v in enumerate(a)]
        sorted_data = sorted(data, key=lambda x: int(x[0]))
    if s == sorted_data[sample+1][1]:
        return True
    else:
        return False


def compare(f1, f2, sample):
    # 讀取兩個檔案
    try:
        with open(f1, "r") as file1:
            a = [line.strip() for line in file1 if line.strip()]
        with open(f2, "r") as file2:
            b = [line.strip() for line in file2 if line.strip()]
    except FileNotFoundError:
        print(f"檔案不存在：{f1} 或 {f2}")
        return False

    # 若有任一檔案為空，直接判定不同
    if not a or not b:
        return False

    # 兩邊都很短（1-2 行），直接比對整體內容
    if len(a) <= 2 and len(b) <= 2:
        return a == b

    # 兩邊都有多行，直接比對整體內容
    if len(a) > 2 and len(b) > 2:
        return a == b

    # ---- 以下為不對稱比對情況 ----

    # 把 a 設為短的那一份，b 為長的（方便處理）
    if len(a) > len(b):
        a, b = b, a  # swap

    # 若 a 有 2 行，先刪掉標題行
    if len(a) == 2:
        data1 = a[1]
    else:
        data1 = a[0]

    # 移除 b 的標題行
    b = b[1:]

    # 在 b 裡搜尋 data1 對應到的 sample 名稱
    for line in b:
        if data1 in line:
            parts = line.split(":")
            if parts[0] == sample:
                return True

    return False

def checkFileNum(dirpath):
    folder = Path(dirpath) 
    file_count = sum(1 for f in folder.iterdir() if f.is_file())
    return file_count

def creatName(BC, J, D, L, P, m, phys):
    mySourceName = sourcelist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m) 
    myTargetName = tarlist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m) 
    groupSourceName = grouplist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m) 
    groupTargetName = tarlist[phys].replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m) 
    return (mySourceName, groupSourceName, myTargetName, groupTargetName)

def creatDir(BC, J, D, L, P, m, phys):
    sourcePath = "/".join(["tSDRG","Main_15","data_random","BC_re","J_re","D_re","L_re_P_re_m_re_s_re"])
    tarPath = "/".join(["tSDRG","Main_15","data_collect","BC_re","J_re","D_re","L_re_P_re_m_re"])
    mySourcePathBase = "/".join([tSDRG_path,sourcePath])
    groupSourcePathBase = "/".join([group_path,sourcePath])
    myTargetPathBase = "/".join([tSDRG_path,tarPath])
    groupTargetPathBase = "/".join([group_path,tarPath])
    # sourcePathBase = f"{tSDRG_path}/tSDRG/Main_15/data_random/BC_re/J_re/D_re/L_re_P_re_m_re_s_re/"
    # cpPathBase = f"{group_path}/tSDRG/Main_15/data_random/BC_re/J_re/D_re/L_re_P_re_m_re_s_re/"
    # targetPathBase = f"{group_path}/tSDRG/Main_15/data_collect/BC_re/J_re/D_re/L_re_P_re_m_re/"

    mySourcePath = mySourcePathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    groupSourcePath = groupSourcePathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    myTargetPath = myTargetPathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    groupTargetPath = groupTargetPathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)

    # cpPath = cpPathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    # targetPath = targetPathBase.replace("BC_re", BC).replace("J_re", J).replace("D_re", D).replace("L_re", L).replace("P_re", P).replace("m_re", m)
    
    return (mySourcePath, groupSourcePath, myTargetPath, groupTargetPath)

def is_nonempty_file(p: str) -> bool:
    """exists and size > 0"""
    try:
        return os.path.exists(p) and os.path.getsize(p) > 0
    except OSError:
        return False


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

    mySourcePath    = folder[0] + "/" + name[0]
    groupSourcePath = folder[1] + "/" + name[1]
    myTarPath       = folder[2] + "/" + name[2]
    groupTarPath    = folder[3] + "/" + name[3]

    lock_path = groupTarPath + LOCK_SUFFIX
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)

    # ---- 從一開始就鎖住 ----
    lock_f = open(lock_path, "w")
    try:
        fcntl.flock(lock_f, fcntl.LOCK_EX)
        print(f"🔒 取得 lock [PID {os.getpid()}] → {lock_path}")

        seedArray = list(range(s1, s2 + 1))

        # 先讀舊的 groupTar，避免重複 seed
        seedInside = set()
        if os.path.exists(groupTarPath):
            with open(groupTarPath, "r") as originFile:
                originalText = originFile.readlines()

            if originalText:
                # 第一行通常是 phys
                body_lines = originalText[1:]
                for line in body_lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        seed = int(line.split(":")[0].strip())
                        seedInside.add(seed)
                    except ValueError:
                        # 避免因為奇怪行格式直接炸掉
                        continue

        context = ""
        nanlist = []
        for seed in seedArray:
            # s1 != 1 時，避免處理已經存在的 seed
            if s1 != 1 and seed in seedInside:
                continue

            groupSource = groupSourcePath.replace("s_re", str(seed))
            mySource    = mySourcePath.replace("s_re", str(seed))

            if os.path.exists(groupSource) and os.path.exists(mySource):
                if compare(groupSource, mySource, seed):
                    fcontext = fread(mySource, phys)
                    file_ok = is_nonempty_file(mySource)
                else:
                    if groupSource != mySource:
                        shutil.copy(mySource, groupSource)
                        
                    fcontext = fread(groupSource, phys)
                    file_ok = is_nonempty_file(groupSource)
                    
                if file_ok is False:
                    nanlist.append(seed)
                    
            elif os.path.exists(mySource):
                shutil.copy(mySource, groupSource)
                fcontext = fread(groupSource, phys)
                
                file_ok = is_nonempty_file(mySource)
                
                if file_ok is False:
                    nanlist.append(seed)
                    
            elif os.path.exists(groupSource):
                fcontext = fread(groupSource, phys)
                file_ok = is_nonempty_file(mySource)
                if file_ok is False:
                    nanlist.append(seed)
            else:
                # 兩邊都沒有資料，跳過
                nanlist.append(seed)
                continue

            if fcontext is not None:
                if phys == "ground":
                    fcontext = float(fcontext.split()[1]) - float(fcontext.split()[0])   # 只取第一個數值（能量值）
                    context += f"{seed}:{fcontext}\n"
                else:
                    context += f"{seed}:{fcontext}\n"
        print("No file for seed", nanlist)
        if context != "":
            # 若 sort_if_needed 會調整 s1，就保留新的 s1
            context, s1_new = sort_if_needed(context)

            save_context(context, s1_new, groupTarPath, myTarPath, phys)

    finally:
        fcntl.flock(lock_f, fcntl.LOCK_UN)
        lock_f.close()
        print(f"🔓 釋放 lock [PID {os.getpid()}] → {lock_path}")


def save_context(context, s1, groupTarPath, myTarPath, phys):
    # 這裡就不用再鎖了，Combine 已經持有全域 lock
    os.makedirs(os.path.dirname(groupTarPath), exist_ok=True)

    mode = "w" if s1 == 1 else "a"

    if s1 == 1:
        # 檔案一開始寫入時，加上 phys 頭
        context = f"{phys}\n{context}"

    with open(groupTarPath, mode) as f1:
        f1.write(context)
        print(f"✅ 寫入完成 ({'WRITE' if s1 == 1 else 'APPEND'}) → {groupTarPath}")


        
# def Combine(BC, J, D, L, P, m, phys, s1, s2):
#     folder = creatDir(BC, J, D, L, P, m, phys)
#     name = creatName(BC, J, D, L, P, m, phys)
#     mySourcePath = folder[0] + "/" + name[0]
#     groupSourcePath = folder[1] + "/" + name[1]
#     myTarPath = folder[2] + "/" + name[2]
#     groupTarPath = folder[3] + "/" + name[3]
#     seedArray = list(range(s1, s2 + 1))
#     # with open(groupTarPath, "r") as originFile:
#     #     originaText = originFile.readlines()
#     context = ""
#     if s1 != 1 and os.path.exists(groupTarPath):
#         with open(groupTarPath, "r") as originFile:
#             originalText = originFile.readlines()
#         del originalText[0]
#         seedInside = [int(line.split(":")[0].strip()) for line in originalText if line.strip()]    # print("originaText")
#     for seed in seedArray:
#         groupSource = groupSourcePath.replace("s_re", str(seed))
#         mySource = mySourcePath.replace("s_re", str(seed))
#         if s1 != 1:
#             if seed in seedInside:
#                 continue
#         if os.path.exists(groupSource) and os.path.exists(mySource):
#             if compare(groupSource, mySource, seed):                
#                 fcontext = fread(mySource, phys)
#             else:
#                 # os.remove(groupSource)
#                 shutil.copy(mySource, groupSource)
#                 fcontext = fread(groupSource, phys)
#         elif os.path.exists(mySource):
#             # os.makedirs(os.path.dirname(groupSource), exist_ok=True)
#             shutil.copy(mySource, groupSource)
#             # os.remove(mySource)
#             fcontext = fread(groupSource, phys)
#         elif os.path.exists(groupSource):
#             fcontext = fread(groupSource, phys)
#         else:
#             continue

#         if fcontext is not None:
#             context += f"{seed}:{fcontext}\n"
#     if context != "":
#         context, s1 = sort_if_needed(context)
        
#         save_context(context, s1, groupTarPath, myTarPath, phys)
#         # os.makedirs(os.path.dirname(myTarPath), exist_ok=True)
# def save_context(context, s1, groupTarPath, myTarPath, phys):
#     if not os.path.exists(groupTarPath):
#         os.makedirs(os.path.dirname(groupTarPath), exist_ok=True)

#     mode = "w" if s1 == 1 else "a"

#     if s1 == 1:
#         context = f"{phys}\n{context}"

#     with open(groupTarPath, mode) as f1:
#         try:
#             # 嘗試非阻塞加鎖
#             fcntl.flock(f1, fcntl.LOCK_EX | fcntl.LOCK_NB)
#             print(f"✅ 立即取得鎖 [PID {os.getpid()}] ({'WRITE' if s1==1 else 'APPEND'}): {groupTarPath}")
#         except BlockingIOError:
#             print(f"⏳ 鎖住等待中 [PID {os.getpid()}] → {groupTarPath}")
#             fcntl.flock(f1, fcntl.LOCK_EX)
#             print(f"✅ 最終取得鎖 [PID {os.getpid()}]")

#         try:
#             f1.write(context)
#         finally:
#             fcntl.flock(f1, fcntl.LOCK_UN)
#             print(f"🔓 檔案已解鎖 [PID {os.getpid()}] → {groupTarPath}")
            
        
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


            
if __name__ == "__main__":
    file = sys.argv[1]
    arg = []
    # Jstr = [f"Jdis{str(i).zfill(3)}" for i in range(int(J),int(J)+1)]
    # Jstr = [f"Jdis{str(i).zfill(3)}" for i in range(10,201,10)]

    # Dstr = [f"Dim{str(i).zfill(3)}" for i in range(101)]
    # Lstr = [f"L{num}" for num in range(31, 255, 32)]  # 只有 L512
    # Lstr = [f"L{num}" for num in range(8, 512, 8)]  # 只有 L512
    # BC = "OBC"
    # Pdis = "20"
    # chi = "40"
    a = scriptCreator.para("read",file)
    parameterlist = a.para
    para=scriptCreator.paraList1(parameterlist["L"],parameterlist["J"],parameterlist["D"],parameterlist["S"])
    BC = parameterlist["BC"]
    Pdis = parameterlist["Pdis"]
    chi = str(parameterlist["chi"])
    # s1 = int(parameterlist["S"]["S1"])
    # s2 = int(parameterlist["S"]["S2"])
    s1 = int(sys.argv[2])
    s2 = int(sys.argv[3])
    if BC == "PBC":
        s_list = ["ZL","corr1","corr2","string","J_list","energy","dimerization","w_loc","seed"]
        s_list = ["ZL","corr1","corr2","seed","energy"]
    else:
        s_list = ["ZL","corr1","corr2","J_list","energy","dimerization","w_loc","seed"]
        s_list = ["corr1","corr2","seed","energy"]
        # s_list = ["ground"]
    # s1 = 1
    # s2 = 10000    
    # for s in s_list:
    #     for L in para.L_str:
    #         for J in para.J_str:
    #                 arg.append((BC, J, para.D_str[0], L, f"P{Pdis}", f"m{chi}", s, s1, s2))
    for s in s_list:
        for L in para.L_str:
            for D in para.D_str:
                for J in para.J_str:
                    arg.append((BC, J, D, L, f"P{Pdis}", f"m{chi}", s, s1, s2))
    print(s_list, para.L_str, para.J_str, para.D_str, Pdis, chi, BC, s1, s2)  
    def fun(arg):
        print("---------------------col--------------------\n")

        with multiprocessing.Pool(processes=10) as pool:
            results1 = pool.starmap(Combine, arg)
        print("---------------------colf--------------------\n")
        # with multiprocessing.Pool(processes=20) as pool:
        #     results1 = pool.starmap(checkAndDelete, arg)
            
    # 計算函數執行時間
    execution_time = timeit.timeit(lambda: fun(arg), number=1)

    # 執行並顯示結果
    # results1, results2 = fun(arg)
    print(f"Execution time: {execution_time} seconds")    
