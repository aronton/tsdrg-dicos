import os
import math
import time
import sys
import multiprocessing 
import datetime
import scriptCreator
import subprocess
import combine


dicosPath = "/ceph/work/NTHU-qubit/LYT/tSDRG_random"
scopionPath = "/home/aronton/tSDRG_random"

if os.path.isdir(dicosPath):
    tSDRG_path = dicosPath
    group_path = dicosPath
    
if os.path.isdir(scopionPath):
    tSDRG_path = scopionPath
    group_path = scopionPath
# create namelist of task
def submitPara(parameterlist, tSDRG_path):

    p = parameterlist
    Spin = parameterlist["Spin"]
    Ncore = parameterlist["Ncore"]
    partition = parameterlist["partition1"]
    task = parameterlist["task"]
    para=scriptCreator.paraList1(parameterlist["L"],parameterlist["J"],parameterlist["D"],parameterlist["S"])
    L_num = para.L_num
    L_p_num = para.L_p_num
    L_str = para.L_str
    L_p_str = para.L_p_str
    

    
    # print("L_num:",L_num)
    # print("L_p_num:",L_p_num)
    # print("L_str:",L_str)
    # print("L_p_str:",L_p_str)

    S_num = para.S_num
    S_str = para.S_str
    s1 = parameterlist["S"]["S1"]
    s2 = parameterlist["S"]["S2"]
    ds = parameterlist["S"]["dS"]
    # print("S_num:",S_num)
    # print("S_str:",S_str)

    J_num = para.J_num
    J_p_num = para.J_p_num
    J_str = para.J_str
    J_p_str = para.J_p_str
    J_s100 = para.J_s100
    J_p_s100 = para.J_p_s100


    # print("J_num",J_num)
    # print("J_p_num",J_p_num)
    # print("J_str:",J_str)
    # print("J_p_str:",J_p_str)
    # print("J_s100:",J_s100)
    # print("J_p_s100:",J_p_s100)
    
    D_num = para.D_num
    D_p_num = para.D_p_num
    D_str = para.D_str
    D_p_str = para.D_p_str
    D_s100 = para.D_s100
    D_p_s100 = para.D_p_s100

    # print("D_num:",D_num)
    # print("D_p_num:",D_p_num)
    # print("D_str:",D_str)
    # print("D_p_str:",D_p_str)
    # print("D_s100:",D_s100)
    # print("D_p_s100:",D_p_s100)
    Spin=parameterlist["Spin"]
    Pdis=parameterlist["Pdis"]
    chi=parameterlist["chi"]
    BC=parameterlist["BC"]
    try:
        check_Or_Not=parameterlist["check_Or_Not"]
    except KeyError as e:
        print(e)
    # with open("./", "r") as file:
    #     template = file.readlines()
    
    # os.system( "cd " + tSDRG_path + "/tSDRG/Main_" + str(Spin))
    os.chdir(
        tSDRG_path + "/Subpy"
    )
    script_path_tot = "" 
    jobNamelist = []
    argvlist = []
    # for l,L in enumerate(L_num):
    #     for j,J in enumerate(J_num):
    #         for d,D in enumerate(D_num):
    #             # for s_i in range(len(S_num)):
    #             #     s = S_num[s_i]
    #             if parameterlist["task"] == "submit"
    #                 argvlist.append([str(Spin),L,J,D,Pdis,chi,task,check_Or_Not])
                # argvlist.append([str(Spin),L,J,D,Pdis,bondDim,str(s[0]),str(s[-1]),check_Or_Not])
    for l,L in enumerate(L_str):
        for j,J in enumerate(J_str):
            for d,D in enumerate(D_str):
                # for s_i in range(len(S_num)):
                #     s = S_num[s_i]
                name = ["Spin"+str(Spin),L,J,D,"P"+str(Pdis),"BC="+BC,"chi"+str(chi),"partition="+str(partition),"seed1="+str(s1),"seed2="+str(s2),"ds="+str(ds),"task="+task]
                name = "_".join(name)
                jobNamelist.append(name)
                argvlist.append((Spin, L_num[l], J_num[j], D_num[d], Pdis, BC, chi, partition, s1, s2, ds, task))
    return (jobNamelist, argvlist)           

# edit script & submit task
def EditandSub(paraPath,script_path,output_path,jobName):
    task = ""
    with open(paraPath,"r") as file:
        elementlist = file.readlines()
        for element in elementlist:
            if "partition" in element:
                partition = str(element.split(":")[1].replace("\n",""))
                # partition = str(element.replace("",":"))
            elif "ds" in element:
                ds = str(element.split(":")[1].replace("\n",""))
            elif "seed1" in element:
                s1 = str(element.split(":")[1].replace("\n",""))
            elif "seed2" in element:
                s2 =str(element.split(":")[1].replace("\n",""))
            elif "task" in element:
                task =str(element.split(":")[1].replace("\n",""))
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_path += f"/{jobName}.txt"
    
    replacements = {
        "replace1": jobName,
        "replace2": str(ds),
        "replace3": str(partition),
        "replace4": output_path,
        # "replace5": str(ds)
    }
    # print(task)
    if task == "submit":
        with open("run1.sh", 'r') as file:
            content = file.read()
    if task == "collect":
        with open("run1.sh", 'r') as file:
            content = file.read()
    # 依據 replacements 替換文字
    for old_text, new_text in replacements.items():
        content = content.replace(old_text, new_text)
    # print(content)
    if not os.path.exists(script_path):
        os.makedirs(script_path)
    script_path += f"/{jobName}.sh"
    # 將結果寫入新檔案
    with open(script_path, 'w') as file:
        file.write(content)

    print(f"替換完成，結果已儲存至 {script_path}")

    submit_cmd = f"sbatch {script_path} {paraPath} true"
    os.system(submit_cmd)    

def taskSeperate(jobNamelist):
    parameter = []
    jobNamelist = jobNamelist[0]
    s = ["Spin", "_L", "_Jdis", "_Dim", "_P", "_BC=", "_chi", "_partition", "_seed1", "_seed2", "_ds", "_task"]
    for i,jobName in enumerate(jobNamelist):
        elementlist = jobName.split("_")
        L = elementlist[1]
        J = elementlist[2]
        D = elementlist[3]
            
    # os.makedirs("/".join([tSDRG_path,"parameterRead",now_year,now_date,"_".join([jobName,f"{now_time}.txt"])]). exist_ok=True)
        dic = {}
        for element in elementlist:
            if "D" in element:
                dic["Dstr"] = element
                s = str(element.replace("Dim",""))
                # file.writelines("D:" + s[0] + "." + s[1] + s[2] + "\n")
            elif "J" in element:
                dic["Jstr"] = element
                s = str(element.replace("Jdis",""))
                # file.writelines("J:"+ s[0] + "." + s[1] + s[2] + "\n")
            elif "L" in element:
                dic["Lstr"] = element
                s = str(element.replace("L",""))
                # file.writelines("L:"+ s + "\n")
            elif "BC" in element:
                dic["BC"] = element
                # file.writelines(element.replace("=",":") + "\n")
            elif "partition" in element:
                dic["partition"] = element.replace("partition=","")
                # file.writelines("partition:" + partition + "\n")
            elif "P" in element:
                dic["Pdis"] = element
                s = str(element.replace("P",""))
                # file.writelines("Pdis:" + s[0] + s[1] + "\n")
            elif "chi" in element:
                dic["chi"] = str(element.replace("chi","B"))
                s = str(element.replace("chi",""))
                # file.writelines("chi:" +s[0] + s[1] + "\n")
            elif "seed1" in element:
                dic["seed1"] = str(element.replace("seed1=",""))
                s1 = str(element.replace("=",":").replace("seed","s"))
                # file.writelines(s + "\n")
            elif "seed2" in element:
                dic["seed2"] = str(element.replace("seed2=",""))
                s2 = str(element.replace("=",":").replace("seed","s"))
                # file.writelines(s + "\n")
            elif "ds" in element:
                dic["ds"] = str(element.replace("ds=",""))
                ds = str(element.replace("=",":"))
                # file.writelines(s + "\n")
            elif "check" in element:
                dic["check"] = str(element.replace("check=",""))
                # file.writelines(element + "\n")
            elif "task" in element:
                dic["task"] = str(element.replace("task=",""))
                task = str(element.replace("=",":"))
                # file.writelines(s + "\n")    
            elif "Spin" in element:
                dic["Spin"] = str(element.replace("Spin=",""))
                Spin = str(element.replace("Spin",""))
        parameter.append(dic)       
    return parameter[0] 
        

# organize task and parameter name into scriptpath
def submit(parameterlist, tSDRG_path, jobNamelist=None):

    splitStr = ["Spin", "_L", "_Jdis", "_Dim", "_P10", "_P20", "_BC=", "_chi", "_partition=", "_seed1=", "_seed2=", "_ds=", "_task="]
    splitNum = []
    if jobNamelist == None:
        p = parameterlist
        Ncore = parameterlist["Ncore"]
        partition = parameterlist["partition1"]
        Spin=parameterlist["Spin"]
        Pdis=parameterlist["Pdis"]
        chi=parameterlist["chi"]
        BC=parameterlist["BC"]
        if parameterlist["task"] == "submit":
            check_Or_Not=parameterlist["check_Or_Not"]
        ds=parameterlist["S"]["dS"]
        jobNamelist, arg = submitPara(parameterlist, tSDRG_path)
    else:
        jobName = jobNamelist[0]
        chiNum = jobName.find("_chi")
        partitionNum = jobName.find("_partition")
        chi = jobName[chiNum+4:partitionNum]
        # partition = jobName[partitionNum+11:partitionNum+13]
        SpinNum = jobName.find("Spin")
        LNum = jobName.find("_L")
        # L = jobName[LNum+4:LNum]
        Spin = jobName[SpinNum+4:LNum]
        
        BCNum = jobName.find("_BC=")
        BC = jobName[BCNum+4:BCNum+7]

        

    record_dir = tSDRG_path + "/tSDRG" + "/Main_" + str(Spin) + "/jobRecord" 
    # if parameterlist["task"] == "collect":
    # # record_dir = tSDRG_path + "/tSDRG" + "/Main_" + str(Spin) + "/jobRecord" 
    #     script_dir = record_dir + "/collect_script" + "/" + str(BC) + "/B" + str(chi)
    #     output_dir = record_dir + "/collect_slurmOutput" + "/" + str(BC) + "/B" + str(chi)
    # else:
    script_dir = record_dir + "/script" + "/" + str(BC) + "/B" + str(chi)
    output_dir = record_dir + "/slurmOutput" + "/" + str(BC) + "/B" + str(chi)
    nt=datetime.datetime.now()
    now_year = str(nt.year)
    now_date = str(nt.year) + "_" + str(nt.month) + "_" + str(nt.day)
    now_time = "H" + str(nt.hour) + "_M" + str(nt.minute) + "_S" + str(nt.second)

    # with open("/".join([tSDRG_path,"parameterRead",now_year,now_date])) as file:
    

    # with open("run.sh", "r") as file:
    #     template = file.readlines()

    # os.system( "cd " + tSDRG_path + "/tSDRG/Main_" + str(Spin))
    os.chdir(
        tSDRG_path + "/Subpy"
    )

    # script_path_tot = "" 
    for i, name in enumerate(jobNamelist):
        print(f"{i+1, name}")
    for i,jobName in enumerate(jobNamelist):
        elementlist = jobName.split("_")
        L = elementlist[1]
        J = elementlist[2]
        D = elementlist[3]
        
        script_path = script_dir + "/" + L + "/" + J + "/" + D  
        output_path = output_dir + "/" + L + "/" + J + "/" + D

        if parameterlist["task"]=="submit":
            if not os.path.exists("/".join([tSDRG_path,"Subpy","parameterRead",now_year,now_date])):
                os.makedirs("/".join([tSDRG_path,"Subpy","parameterRead",now_year,now_date]))
            paraPath = "/".join([tSDRG_path,"Subpy","parameterRead",now_year,now_date,"_".join([jobName,f"{now_time}.txt"])])

        if parameterlist["task"]=="collect":
            if not os.path.exists("/".join([tSDRG_path,"Subpy","collectPara",now_year,now_date])):
                os.makedirs("/".join([tSDRG_path,"Subpy","collectPara",now_year,now_date]))
            paraPath = "/".join([tSDRG_path,"Subpy","collectPara",now_year,now_date,"_".join([jobName,f"{now_time}.txt"])])
            
        # os.makedirs("/".join([tSDRG_path,"parameterRead",now_year,now_date,"_".join([jobName,f"{now_time}.txt"])]). exist_ok=True)
        with open(paraPath,"w") as file:
            for element in elementlist:
                if "D" in element:
                    s = str(element.replace("Dim",""))
                    file.writelines("D:" + s[0] + "." + s[1] + s[2] + "\n")
                elif "J" in element:
                    s = str(element.replace("Jdis",""))
                    file.writelines("J:"+ s[0] + "." + s[1] + s[2] + "\n")
                elif "L" in element:
                    s = str(element.replace("L",""))
                    file.writelines("L:"+ s + "\n")
                elif "BC" in element:
                    file.writelines(element.replace("=",":") + "\n")
                elif "partition" in element:
                    partitionNum = jobName.find("_partition=")
                    seed1Num = jobName.find("_seed1=")
                    partition = jobName[partitionNum + len("_partition="):seed1Num]
                    file.writelines("partition:" + partition + "\n")
                # elif "P" in element:
                #     s = str(element.replace("P",""))
                #     file.writelines("Pdis:" + s[0] + s[1] + "\n")
                # elif "chi" in element:
                #     s = str(element.replace("chi",""))
                #     file.writelines("chi:" +s[0] + s[1] + "\n")
                elif element.startswith("P"):
                    s = element[1:]
                    file.writelines("Pdis:" + s + "\n")
                elif element.startswith("chi"):
                    s = element[len("chi"):]
                    file.writelines("chi:" + s + "\n")
                elif "seed1" in element:
                    s = str(element.replace("=",":").replace("seed","s"))
                    file.writelines(s + "\n")
                elif "seed2" in element:
                    s = str(element.replace("=",":").replace("seed","s"))
                    file.writelines(s + "\n")
                elif "ds" in element:
                    s = str(element.replace("=",":"))
                    file.writelines(s + "\n")
                elif "check" in element:
                    file.writelines(element + "\n")
                elif "task" in element:
                    s = str(element.replace("=",":"))
                    file.writelines(s + "\n")
            # file.writelines("ds:"+str(ds) + "\n")
        EditandSub(paraPath, script_path, output_path, jobName)



def find(parameterlist):
    print("find")
    p = parameterlist
    # flag = input("Job_state R/P")
    if p["status"] == "R":
        Job_state = "RUNNING"
    elif p["status"] == "P":
        Job_state = "PENDING"
    elif p["status"] == "skip" :
        Job_state = "skip"

    Ncore = p["Ncore"]
    partition = p["partition1"]      
    
    if partition != "skip":
        job_list = os.popen("squeue " + "-u aronton " + "-p " + str(partition) + " -o \"%.15i %.25P %.150j %.20T %.20M\"")
    else:
        job_list = os.popen("squeue " + "-u aronton " + " -o \"%.15i %.25P %.150j %.20T %.20M\"")
    job_list = list(job_list)

    del job_list[0]
    for i in range(len(job_list)):
        job_list[i] = job_list[i].split()    

    para = scriptCreator.paraList1(p["L"],p["J"],p["D"],p["S"])

    if (p["L"]["L1"] != "skip") and (p["L"]["L2"] != "skip") and (p["L"]["dL"] != "skip"): 
        L_num = para.L_num
        L_p_num = para.L_p_num
        L_str = para.L_str
        L_p_str = para.L_p_str       
        temp = []
        for l in L_str:
            for e in job_list:
                if l in e[2]:
                    temp.append(e)
        job_list = temp

            
    if (p["J"]["J1"] != "skip") and (p["J"]["J2"] != "skip") and (p["J"]["dJ"] != "skip"): 
        J_num = para.J_num
        J_p_num = para.J_p_num
        J_str = para.J_str
        J_p_str = para.J_p_str
        J_s100 = para.J_s100
        J_p_s100 = para.J_p_s100
        temp = []
        for j in J_str:
            for e in job_list:
                if j in e[2]:
                    temp.append(e)
        job_list = temp




    if (p["D"]["D1"] != "skip") and (p["D"]["D2"] != "skip") and (p["D"]["dD"] != "skip"): 
        D_num = para.D_num
        D_p_num = para.D_p_num
        D_str = para.D_str
        D_p_str = para.D_p_str
        D_s100 = para.D_s100
        D_p_s100 = para.D_p_s100
        temp = []
        for d in D_str:
            for e in job_list:
                if d in e[2]:
                    temp.append(e)
            # if i in job_list
        job_list = temp
        
    Pdis=p["Pdis"]
    chi=p["chi"]
    BC=p["BC"]
        
    if (p["Spin"] != "skip"): 
        Spin=str(p["Spin"])
        job_list = list(filter(lambda n: Spin in n[2],job_list))
    if (p["Pdis"] != "skip"): 
        Pdis=str(p["Pdis"])
        job_list = list(filter(lambda n: Pdis in n[2],job_list))        
    if (p["chi"] != "skip"): 
        chi=str(p["chi"])
        job_list = list(filter(lambda n: chi in n[2],job_list))   
    if (p["BC"] != "skip"): 
        BC=str(p["BC"])
        job_list = list(filter(lambda n: BC in n[2],job_list))    
    if (Job_state != "skip"): 
        job_list = list(filter(lambda n: Job_state in n[3],job_list))     
     
    return job_list

def cancel(parameterlist):

    job_list = find(parameterlist)

    print("Cancel : \n\n")
    print("------------------------------------------------- \n\n")
    
    for i in range(len(job_list)):
        print(job_list[i][2])    
    yes = input(f"These {len(job_list)} jobs are found, are you going to cancel them ?(Y or y to delete)")
    if yes == "y" or yes == "Y":
        for i in range(len(job_list)):
            cmd = "scancel " + job_list[i][0]
            print(cmd + " : " + job_list[i][2])    
            os.system(cmd)        
    else:
        return
def get(parameterlist):
    
    job_list = find(parameterlist)
    task_list = []
    for job in job_list:
        task_list.append(job[2])
        
    return task_list


def show(parameterlist):
        
    job_list = find(parameterlist)

    print("show\n\n")
    print("------------------------------------------------------\n\n")

    for i in range(len(job_list)):
        print(job_list[i])

def collectData(parameterlist):
    parameterlist = a.para
    para=scriptCreator.paraList1(parameterlist["L"],parameterlist["J"],parameterlist["D"],parameterlist["S"])
    BC = parameterlist["BC"]
    Pdis = parameterlist["Pdis"]
    chi = "m" + str(parameterlist["chi"])
    s1 = int(parameterlist["S"]["S1"])
    s2 = int(parameterlist["S"]["S2"])

    if BC == "PBC":
        s_list = ["ZL","corr1","corr2","string","J_list","energy","dimerization","w_loc","seed"]
    else:
        s_list = ["ZL","corr1","corr2","J_list","energy","dimerization","w_loc","seed"]
        
    for s in s_list:
        for L in para.L_str:
            for J in para.J_str:
                    arg.append((BC, J, para.D_str[0], L, f"P{Pdis}", f"{chi}", s, s1, s2))
    print("---------------------col--------------------\n")
    with multiprocessing.Pool(processes=Ncore) as pool:
        results1 = pool.starmap(Combine, arg)        
    return

def Distribution(parameterlist):
        
    job_list = find(parameterlist)

    print("Distribution\n\n")
    print("------------------------------------------------------\n\n")
    print("tot:")
    tot=len(job_list)
    print(tot)
    print("Running:")
    job_list = list(filter(lambda n: "RUNNING" in n[3],job_list)) 
    run=len(job_list)
    print(run)
    print("Pending:")  
    print(tot-run)      

def getNodeStatus():
    b = os.popen("sinfo -N -o \"%N %T %C %m %G\"")
    b = list(b)
    del b[0] 
    b = [s.split(" ")[:3] for s in b]

    for s in b:
        s[-1] = s[-1].split("/")[1]

    nodelist = {}
    for s in b:
        if s[0][:-2] not in nodelist:
            nodelist[s[0][:-2]] = []
        nodelist[s[0][:-2]].append(s)
    return nodelist

def getIdleNode():
    nodelist = getNodeStatus()
    return nodelist

def showNodeStatus():
    nodelist = getNodeStatus()
    for key, value in nodelist.items():
        print(f"Node: {key}")
        for v in value:
            print(v)
    print("\n\n")
    
def bestNode():
    nodelist = getNodeStatus()
    idleNode = []
    for key, value in nodelist.items():
        for v in value:
            if v[1] == "idle":
                idleNode.append(v[0])
    if len(idleNode) == 0:
        print("No idle node found.")
        return None
    else:
        print(f"Idle nodes: {idleNode}")
        return idleNode[0]  # Return the first idle node found
    

def getPartitionStatus():
    # os.system('sinfo -o "%P %C"')
    partitionlsit = os.popen('sinfo -o "%P %C"')
    partitionlsit = list(partitionlsit)
    del partitionlsit[0]
    
    partitionlsit = [str(v.replace("\n","")) for v in partitionlsit]

    partitionlsit = [v.split(" ") for v in partitionlsit]
    
    partitionlsit = [(i+1,v[0],int(v[1].split("/")[1])) for i,v in enumerate(partitionlsit)]
    # print(f"partitionlsit:{partitionlsit}")
    partitionDict = {}
    for key, value in enumerate(partitionlsit):
        partitionDict[value[0]] = [str(value[1]), str(value[2])]
    # print(f"partitionDict:{partitionDict}")
    # partitionlsit = [v for v in partitionlsit if "v100" not in v[0]]
    # partitionlsit = [v for v in partitionlsit if "a100" not in v[0]]
    
    # [print(v[0]) for v in partitionlsit]
    return partitionDict

def get_partition_info_list():
    # 執行 sinfo 指令
    result = subprocess.run(
        ["sinfo", "-o", "%30P %20C %10l"],
        stdout=subprocess.PIPE,
        text=True
    )

    lines = result.stdout.strip().split('\n')
    info_list = []

    # 第 0 格為標題列
    header = f"{'No.':<4} {'Partition':<30} {'CPU(A/I/O/T)':<20} {'TimeLimit':<10}"
    info_list.append(header)

    # 從第 1 行開始讀取資料
    for idx, line in enumerate(lines[1:], start=1):
        partition = line[:30].strip().rstrip('*')
        cpu_info  = line[30:50].strip()
        time_lim  = line[50:].strip()

        row = f"{idx:<4} {partition:<30} {cpu_info:<20} {time_lim:<10}"
        info_list.append(row)

    return info_list

        
def showPartitionStatus():
    nodelist = getNodeStatus()
    for key, value in nodelist.items():
        status = f"partition : {key}:\n"
        for i, v in enumerate(value):
            if v[1] == "idle":
                status += f"{v[0]} {v[1]} {v[2]};\n"
            else:
                pass
        print(status)
    print("\n\n")

def main():
    
    tasks = ["submit","show","cancel","change","dis","check","collect","a","b","c","d","e","f","g"]
    task = ""

    while task not in tasks:
        task = input("What is the task? (a)submit, (b)show, (c)cancel Jobs, (d)change (e)distribution: (f)check: (g)collect: \n")
        if task == "a":
            task = "submit"
        elif task == "b":
            task = "show"
        elif task == "c":
            task = "cancel"
        elif task == "d":
            task = "change"
        elif task == "e":
            task = "dis"    
        elif task == "f":
            task = "check"    
        elif task == "g":
            task = "collect"    

    os.system("sinfo")

    nt=datetime.datetime.now()

    print("---------------------------"+str(nt.now())+"---------------------------")

    print("key in parameter in the following format : \n\
    ex : Spin, L1, L2, delta_L, J1, J2, delta_J, D1, D2, delta_D, Pdis, chi, initialSampleNumber, finalSampleNumber, sampleDelta, check_Or_Not\n\
    ex : 15(Spin) 64(L) 1.1(J) 0.1(D) 10(Pdis) 40(chi) 1(initialSampleNumber) 20(finalSampleNumber) 5(sampleDelta), Y(check_Or_Not)\n")

    # task = sys.argv[1]
    # nodeDict =getNodeStatus()
    # partitionDict = getPartitionStatus()

    # showPartitionStatus()
    partitionlist = get_partition_info_list()
    for i,s in enumerate(partitionlist):
        print(s)
    # [print(v) for v in partitionDict]
    # for key, value in partitionDict.items():
    #     print(f"{value[0]} : {value[1]}")
    a = scriptCreator.para(task, partitionlist)
    
    a.keyin()
    parameterlist = a.para

    print(parameterlist,"\n")
    for s in parameterlist:
        print(s," : ",parameterlist[s])

    if task == "submit" or task == "a":
        tasklist = submitPara(parameterlist, tSDRG_path)
        submit(parameterlist, tSDRG_path)
    elif task == "show" or task == "b":
        show(parameterlist)
        Distribution(parameterlist)
    elif task == "cancel" or task == "c":
        cancel(parameterlist)
    elif task == "change" or task == "d":
        psubmit = scriptCreator.para("submit", partitionlist)
        pcancel = scriptCreator.para("cancel", partitionlist)

        for key,value in psubmit.para.items():
            if key == "partition1" or key == "task":
                psubmit.para[key] = parameterlist["partition2"]
                psubmit.para["task"] = "submit"
            else:
                psubmit.para[key] = parameterlist[key]
        for key,value in pcancel.para.items():
            if key == "partition1" or key == "task":
                pcancel.para[key] = parameterlist["partition1"]
                pcancel.para["task"] = "cancel"
            else:
                pcancel.para[key] = parameterlist[key]
        
        tasklist=get(pcancel.para)
        cancel(pcancel.para)
        mydict = parameterlist['S']
        found = any("skip" in str(v) for v in mydict.values() if isinstance(v, str))
        if found == True:
            submit(psubmit.para, tSDRG_path, tasklist)
        else:
            submit(psubmit.para, tSDRG_path)
    elif task == "dis" or task == "e":
        Distribution(parameterlist)
    elif task == "check" or task == "f":
        Distribution(parameterlist)
    elif task == "collect" or task == "g":
        tasklist = submitPara(parameterlist, tSDRG_path)
        submit(parameterlist, tSDRG_path)
    elif task == "average" or task == "h":
        tasklist = submitPara(parameterlist, tSDRG_path)
        submit(parameterlist, tSDRG_path)
    return

if __name__ == '__main__' :
    main()

