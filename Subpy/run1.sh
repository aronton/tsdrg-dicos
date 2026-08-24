#!/bin/bash
#SBATCH --job-name=replace1
#SBATCH --ntasks=replace2
#SBATCH --partition=replace3
#SBATCH --cpus-per-task=1
#SBATCH --output=replace4
#SBATCH --requeue


source ~/.bashrc

date

FILE=$1
outputPath="replace4"

# 原始腳本絕對路徑
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"

# 保留原本傳進來的參數
ORIG_ARGS=("$@")

#!/bin/bash

scopionPath="/home/aronton/tSDRG_random"
dicosPath="/ceph/work/NTHU-qubit/LYT/tSDRG_random"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1


if [ -d "${scopionPath}/tSDRG/Main_15" ]; then
    tSDRGpath="${scopionPath}"
    cd "${tSDRGpath}/tSDRG/Main_15"
    echo "working on scopion"

elif [ -d "${dicosPath}/tSDRG/Main_15" ]; then
    tSDRGpath="${dicosPath}"
    cd "${tSDRGpath}/tSDRG/Main_15"
    echo "working on dicos"
else
    echo "❌ 找不到 Main_15 目錄！"
    exit 1
fi
echo "📁 當前工作路徑：$(pwd)"
# 讀取 eee 檔案並解析 s1, s2, ds
while IFS=: read -r key value; do
    value=$(echo "$value" | xargs)  # 去除前後空白
    if [[ "$key" == "s1" ]]; then
        s1=$value
    elif [[ "$key" == "s2" ]]; then
        s2=$value
    elif [[ "$key" == "ds" ]]; then
        ds=$value
    fi
done < "$FILE"

echo "parameterfile : $FILE"
echo "The working directory : $PWD"

if [[ -n "${3:-}" ]]; then
    restart_round="$3"
else
    restart_round=0
fi

echo "restart_round=$restart_round"

# 全域變數控制是否使用 Slurm 排程、是否印出指令
use_slurm=$2
use_slurm="true"
if [ "$use_slurm" == true ]; then
    echo "use_slurm : $use_slurm"
fi
run_and_print() {
    local cmd=("$@")  # 將傳入的所有參數組成陣列

    if $use_slurm; then
        srun --ntasks=1 --nodes=1 --cpus-per-task=1 --exclusive "${cmd[@]}"
        if $print_cmd; then
            echo "[執行指令] srun --ntasks=1 --nodes=1 --cpus-per-task=1 --exclusive ${cmd[*]}"
        fi
    else
        "${cmd[@]}"
        if $print_cmd; then
            echo "[執行指令] ${cmd[*]}"
        fi
    fi
}

time_to_seconds() {
    local t="$1"
    local d=0 h=0 m=0 s=0

    if [[ -z "$t" || "$t" == "NOT_SET" ]]; then
        echo 0
        return
    fi

    if [[ "$t" == "UNLIMITED" ]]; then
        echo -1
        return
    fi

    if [[ "$t" == *-* ]]; then
        d=${t%%-*}
        t=${t#*-}
    fi

    IFS=: read -r h m s <<< "$t"

    echo $((10#$s + 60*(10#$m + 60*(10#$h + 24*10#$d))))
}


# 檢查是否提供了檔案名稱作為參數
if [ -z "$1" ]; then
    echo "請提供要讀取的 .txt 檔案名稱作為參數。"
    echo "用法：$0 檔案名稱.txt"
    exit 1
fi

# 檢查指定的檔案是否存在
if [ ! -f "$FILE" ]; then
    echo "檔案 '$FILE' 不存在。"
    exit 1
fi

# 逐行讀取並顯示檔案內容
task=""

while IFS= read -r line || [ -n "$line" ]; do
    IFS=':' read -r part1 part2 <<< "$line"

    echo "$line"

    if [ "$part1" == "task" ]; then
        task="$part2"
        echo "✅ 偵測到 'task'，設定 task=$task"
    fi

done < "$FILE"



# 確保變數都有值
if [[ -z "$s1" || -z "$s2" || -z "$ds" ]]; then
    echo "錯誤: s1, s2, ds 讀取失敗！"
    exit 1
fi

# 計算分組數量
cols=$(((s2 - s1 + 1) / ds ))
echo "s1: $s1, s2: $s2, ds: $ds, cols: $cols"
# 定義行數與列數
rows=$ds
# cols=$((s2/ds))
echo
echo -e "$rows"
echo -e "$cols"
# 初始化二維陣列（用一維陣列模擬）
# array=()
if [ "$task" == "submit" ]; then
    # === 一次 srun 並行（非 MPI），每輪只一個 step，所有輸出進 #SBATCH --output ===
    round_times=()          # 每一輪花費時間
    total_time=0            # 總時間
    current_round=-1        # 目前正在跑第幾輪
    last_completed_round=-1 # 已完成到第幾輪

    for ((i=restart_round; i<cols; i++)); do

        current_round=$i

        # 用「已完成輪次」來算平均
        if (( i > 0 )); then
            avg_time=$(( total_time / i ))
        else
            avg_time=0
        fi

        remaining_time=$(squeue -h -j "$SLURM_JOB_ID" -o "%L")
        remaining_sec=$(time_to_seconds "$remaining_time")

        # 若查不到剩餘時間，可自行決定要不要直接停
        if (( remaining_sec < 0 )); then
            echo "Warning: 無法取得剩餘時間，停止開新輪次。"
            break
        fi

        required_time=$(( avg_time + 600 ))   # 平均時間 + 10 分鐘 buffer

        echo "Round${i}: remaining_sec=${remaining_sec}, remaining_time=${remaining_time}s, avg_time=${avg_time}s, required_time=${required_time}s"

        # 第 0 輪沒有平均值，可選擇直接跑；從第 1 輪開始嚴格檢查
        if (( i > 0 && remaining_sec <= required_time )); then
            echo "剩餘時間不足，不再啟動下一輪。"
            # 避免 export 設定被污染
            export SLURM_EXPORT_ENV=ALL
            sbatch --export=ALL \
                "$SCRIPT_PATH" "$FILE" "$use_slurm" "$current_round"

            rc=$?
            # sbatch --export=ALL \
            #     "$SCRIPT_PATH" "${ORIG_ARGS[@]}" "${current_round}"
            echo "last_completed_round=$last_completed_round"

            if (( rc != 0 )); then
                echo "Error: 重新提交失敗，sbatch rc=$rc" >&2
                exit $rc
            fi

            echo "重新提交成功，當前 job 結束。"
            exit 0
        fi

        start=$SECONDS
        echo -e "Round${i} start ${start}\n"

        start_idx=$(( s1 + i*rows ))
        end_idx=$(( start_idx + rows - 1 ))
        if (( end_idx > s2 )); then
            end_idx=$s2
        fi
        GROUP_SIZE=$(( end_idx - start_idx + 1 ))

        # 傳遞給子任務
        export FILE start_idx

        srun --mpi=none -n "${GROUP_SIZE}" -c 1 --cpu-bind=cores --distribution=block:block --mem-bind=local bash -lc '
        p=$(( start_idx + SLURM_PROCID ))
        exec ./spin15_run160316.exe "$FILE" "$p" "$p"
        '


        python "${tSDRGpath}/Subpy/combine.py" "${FILE}" "${start_idx}" "${end_idx}"
        python "${tSDRGpath}/Subpy/ave.py"     "${FILE}" "${start_idx}" "${end_idx}"

        elapsed=$(( SECONDS - start ))
        round_times[i]=$elapsed
        total_time=$(( total_time + elapsed ))
        last_completed_round=$i

        echo -e "Round${i} elapsed: $elapsed seconds"
        echo -e "current_round=$current_round, last_completed_round=$last_completed_round\n$(date)\n"

    done

    avg_time=$(awk "BEGIN {printf \"%.2f\", $total_time / $last_completed_round}")

    # if $s1 != 1
    #     python "${tSDRGpath}/Subpy/combine.py" "${FILE}" 1 "${s2}"
    python "${tSDRGpath}/Subpy/ave.py" "${FILE}" 1 "${s2}"

else
    # 否則，執行這段
    # run_and_print python ${tSDRGpath}/Subpy/combine.py "${FILE}" 1 "${s2}"
    # run_and_print python ${tSDRGpath}/Subpy/ave.py "${FILE}" 1 "${s2}"

    python ${tSDRGpath}/Subpy/combine.py "${FILE}" 1 "${s2}"
    python ${tSDRGpath}/Subpy/ave.py "${FILE}" 1 "${s2}"
fi
# python /dicos_ui_home/aronton/tSDRG_random/Subpy/combine.py ${FILE}

echo "Job finished $(date)"
