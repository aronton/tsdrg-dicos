#!/bin/bash
#SBATCH --job-name=replace1
#SBATCH --ntasks=replace2
#SBATCH --partition=replace3
#SBATCH --cpus-per-task=1
#SBATCH --output=replace4
#SBATCH --requeue

set -o pipefail

source ~/.bashrc

echo "Job started: $(date)"

# ============================================================
# 讀取命令列參數
#
# $1：參數檔
# $2：是否使用 Slurm，預設 true
# $3：從第幾輪繼續，預設 0
# ============================================================

if [[ -z "${1:-}" ]]; then
    echo "錯誤：請提供參數檔。" >&2
    echo "用法：$0 parameter.txt [true|false] [restart_round]" >&2
    exit 1
fi

if [[ ! -f "$1" ]]; then
    echo "錯誤：參數檔 '$1' 不存在。" >&2
    exit 1
fi

# 必須在 cd 前轉成絕對路徑
FILE="$(readlink -f "$1")"

use_slurm="${2:-true}"
restart_round="${3:-0}"

case "$use_slurm" in
    true|false)
        ;;
    *)
        echo "錯誤：use_slurm 必須是 true 或 false，目前為：$use_slurm" >&2
        exit 1
        ;;
esac

if ! [[ "$restart_round" =~ ^[0-9]+$ ]]; then
    echo "錯誤：restart_round 必須是非負整數，目前為：$restart_round" >&2
    exit 1
fi

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"

echo "parameter file : $FILE"
echo "use_slurm      : $use_slurm"
echo "restart_round  : $restart_round"

# ============================================================
# 判斷執行環境
# ============================================================

scopionPath="/home/aronton/tSDRG_random"
dicosPath="/ceph/work/NTHU-qubit/LYT/tSDRG_random"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

if [[ -d "${scopionPath}/tSDRG/Main_15" ]]; then
    tSDRGpath="$scopionPath"
    cluster_name="scopion"
elif [[ -d "${dicosPath}/tSDRG/Main_15" ]]; then
    tSDRGpath="$dicosPath"
    cluster_name="dicos"
else
    echo "錯誤：找不到 tSDRG/Main_15 目錄。" >&2
    exit 1
fi

if ! cd "${tSDRGpath}/tSDRG/Main_15"; then
    echo "錯誤：無法進入 ${tSDRGpath}/tSDRG/Main_15" >&2
    exit 1
fi

echo "working on       : $cluster_name"
echo "working directory: $PWD"

# ============================================================
# 讀取參數檔
# ============================================================

s1=""
s2=""
ds=""
task=""

while IFS=: read -r key value || [[ -n "$key" ]]; do
    # 移除 key/value 前後空白
    key="$(echo "$key" | xargs)"
    value="$(echo "${value:-}" | xargs)"

    case "$key" in
        s1)
            s1="$value"
            ;;
        s2)
            s2="$value"
            ;;
        ds)
            ds="$value"
            ;;
        task)
            task="$value"
            ;;
    esac
done < "$FILE"

if [[ -z "$s1" || -z "$s2" || -z "$ds" ]]; then
    echo "錯誤：s1、s2 或 ds 讀取失敗。" >&2
    echo "讀取結果：s1='$s1', s2='$s2', ds='$ds'" >&2
    exit 1
fi

if ! [[ "$s1" =~ ^[0-9]+$ &&
        "$s2" =~ ^[0-9]+$ &&
        "$ds" =~ ^[1-9][0-9]*$ ]]; then
    echo "錯誤：s1、s2 必須是非負整數，ds 必須是正整數。" >&2
    echo "目前數值：s1=$s1, s2=$s2, ds=$ds" >&2
    exit 1
fi

if (( s2 < s1 )); then
    echo "錯誤：s2=$s2 小於 s1=$s1。" >&2
    exit 1
fi

# sample 總數
sample_count=$((s2 - s1 + 1))

# 向上取整，確保最後不足 ds 個 samples 的輪次不會漏掉
cols=$(((sample_count + ds - 1) / ds))
rows=$ds

echo "task=$task"
echo "s1=$s1, s2=$s2, ds=$ds"
echo "sample_count=$sample_count"
echo "total_rounds=$cols"

if (( restart_round >= cols )); then
    echo "restart_round=$restart_round 已超過總輪數 $cols，沒有工作需要執行。"
    exit 0
fi

# ============================================================
# Slurm 剩餘時間轉成秒
#
# 支援：
#   MM:SS
#   HH:MM:SS
#   D-HH:MM:SS
#   UNLIMITED
# ============================================================

time_to_seconds() {
    local time_string="$1"
    local days=0
    local hours=0
    local minutes=0
    local seconds=0
    local part_count

    if [[ -z "$time_string" || "$time_string" == "NOT_SET" ||
          "$time_string" == "N/A" ]]; then
        echo -2
        return
    fi

    if [[ "$time_string" == "UNLIMITED" ]]; then
        echo -1
        return
    fi

    if [[ "$time_string" == *-* ]]; then
        days="${time_string%%-*}"
        time_string="${time_string#*-}"
    fi

    part_count=$(awk -F: '{print NF}' <<< "$time_string")

    case "$part_count" in
        3)
            IFS=: read -r hours minutes seconds <<< "$time_string"
            ;;
        2)
            IFS=: read -r minutes seconds <<< "$time_string"
            ;;
        1)
            seconds="$time_string"
            ;;
        *)
            echo -2
            return
            ;;
    esac

    echo $(
        (10#$seconds) +
        60 * (
            (10#$minutes) +
            60 * (
                (10#$hours) +
                24 * (10#$days)
            )
        )
    )
}

# ============================================================
# 執行
# ============================================================

if [[ "$task" == "submit" ]]; then

    total_time=0
    completed_in_this_job=0
    last_completed_round=$((restart_round - 1))

    for ((i=restart_round; i<cols; i++)); do

        # 只有本次 job 已完成至少一輪，才使用平均時間
        if (( completed_in_this_job > 0 )); then
            avg_time=$((total_time / completed_in_this_job))
        else
            avg_time=0
        fi

        # 有 SLURM_JOB_ID 才能查詢剩餘時間
        if [[ -n "${SLURM_JOB_ID:-}" ]]; then
            remaining_time="$(
                squeue -h -j "$SLURM_JOB_ID" -o "%L" 2>/dev/null |
                head -n 1
            )"
            remaining_sec="$(time_to_seconds "$remaining_time")"
        else
            remaining_time="NOT_IN_SLURM"
            remaining_sec=-2
        fi

        required_time=$((avg_time + 600))

        echo
        echo "================================================"
        echo "Round $i / $((cols - 1))"
        echo "remaining_time=$remaining_time"
        echo "remaining_sec=$remaining_sec"
        echo "avg_time=$avg_time"
        echo "required_time=$required_time"
        echo "================================================"

        # remaining_sec == -1 代表 UNLIMITED，不需要續投
        # remaining_sec == -2 代表查詢失敗，保守停止並續投
        should_resubmit=false

        if (( completed_in_this_job > 0 )); then
            if (( remaining_sec == -2 )); then
                echo "警告：無法取得 Slurm 剩餘時間，準備續投。"
                should_resubmit=true
            elif (( remaining_sec >= 0 &&
                    remaining_sec <= required_time )); then
                echo "剩餘時間不足，不再啟動 Round $i。"
                should_resubmit=true
            fi
        fi

        if [[ "$should_resubmit" == "true" ]]; then

            export SLURM_EXPORT_ENV=ALL

            submit_output="$(
                sbatch --export=ALL \
                    "$SCRIPT_PATH" \
                    "$FILE" \
                    "$use_slurm" \
                    "$i" 2>&1
            )"
            rc=$?

            echo "$submit_output"
            echo "last_completed_round=$last_completed_round"
            echo "next_restart_round=$i"

            if (( rc != 0 )); then
                echo "錯誤：重新提交失敗，sbatch rc=$rc" >&2
                exit "$rc"
            fi

            echo "重新提交成功，目前 job 正常結束。"
            exit 0
        fi

        start_time=$SECONDS

        start_idx=$((s1 + i * rows))
        end_idx=$((start_idx + rows - 1))

        if (( end_idx > s2 )); then
            end_idx=$s2
        fi

        group_size=$((end_idx - start_idx + 1))

        echo "Round $i started: $(date)"
        echo "sample range: $start_idx-$end_idx"
        echo "group_size=$group_size"

        export FILE
        export start_idx

        if [[ "$use_slurm" == "true" ]]; then

            srun --mpi=none \
                --ntasks="$group_size" \
                --cpus-per-task=1 \
                --cpu-bind=cores \
                --distribution=block:block \
                bash -lc '
                    p=$((start_idx + SLURM_PROCID))
                    exec ./spin15_run160316.exe "$FILE" "$p" "$p"
                '

            run_rc=$?

        else
            run_rc=0

            for ((p=start_idx; p<=end_idx; p++)); do
                ./spin15_run160316.exe "$FILE" "$p" "$p" &
            done

            wait || run_rc=$?
        fi

        if (( run_rc != 0 )); then
            echo "錯誤：Round $i 計算失敗，rc=$run_rc。" >&2
            echo "這一輪不會標記成已完成。" >&2
            exit "$run_rc"
        fi

        python "${tSDRGpath}/Subpy/combine.py" \
            "$FILE" "$start_idx" "$end_idx"
        combine_rc=$?

        if (( combine_rc != 0 )); then
            echo "錯誤：Round $i combine.py 執行失敗。" >&2
            exit "$combine_rc"
        fi

        python "${tSDRGpath}/Subpy/ave.py" \
            "$FILE" "$start_idx" "$end_idx"
        ave_rc=$?

        if (( ave_rc != 0 )); then
            echo "錯誤：Round $i ave.py 執行失敗。" >&2
            exit "$ave_rc"
        fi

        elapsed=$((SECONDS - start_time))
        total_time=$((total_time + elapsed))
        completed_in_this_job=$((completed_in_this_job + 1))
        last_completed_round=$i

        echo "Round $i completed."
        echo "elapsed=${elapsed}s"
        echo "last_completed_round=$last_completed_round"
        echo "finished at $(date)"
    done

    if (( completed_in_this_job > 0 )); then
        avg_time=$((total_time / completed_in_this_job))
        echo "本次 job 完成輪數：$completed_in_this_job"
        echo "本次 job 平均每輪時間：${avg_time}s"
    fi

    # 全部輪次完成後，重新對完整範圍取平均
    python "${tSDRGpath}/Subpy/ave.py" "$FILE" "$s1" "$s2"
    final_ave_rc=$?

    if (( final_ave_rc != 0 )); then
        echo "錯誤：最終 ave.py 執行失敗。" >&2
        exit "$final_ave_rc"
    fi

else
    echo "task='$task'，不執行 spin 計算，只進行後處理。"

    python "${tSDRGpath}/Subpy/combine.py" "$FILE" "$s1" "$s2"
    combine_rc=$?

    if (( combine_rc != 0 )); then
        echo "錯誤：combine.py 執行失敗。" >&2
        exit "$combine_rc"
    fi

    python "${tSDRGpath}/Subpy/ave.py" "$FILE" "$s1" "$s2"
    ave_rc=$?

    if (( ave_rc != 0 )); then
        echo "錯誤：ave.py 執行失敗。" >&2
        exit "$ave_rc"
    fi
fi

echo "Job finished: $(date)"