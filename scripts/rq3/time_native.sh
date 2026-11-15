#!/bin/bash
# Measure native execution time of one CVE program (3 runs by default).
# Usage: bash /results/scripts/time_native.sh <CVE-dir> <binary-name> [reps]
# Example: bash /results/scripts/time_native.sh CVE-2016-7911 2016-7911_native 3
DIR=$1
BIN=$2
REPS=${3:-3}
OUT=${RESULTS:-/results}/RQ3/$DIR
mkdir -p $OUT
BASE=${ROOT_DIR:-/workdir/PERIOD}/evaluation/ConVul-CVE-Benchmarks
LOG=$OUT/native_runs.log

echo "[$(date '+%F %T')] native timing: $DIR / $BIN, reps=$REPS" | tee -a $LOG
for i in $(seq 1 $REPS); do
  S=$(date +%s.%N)
  timeout 60 $BASE/$DIR/./$BIN > $OUT/native_run${i}_output.txt 2>&1
  RC=$?
  E=$(date +%s.%N)
  T=$(echo "$E - $S" | bc)
  if [ $RC -eq 124 ]; then
    echo "run$i: TIMEOUT (>60s, killed) time=$T s" | tee -a $LOG
  else
    echo "run$i: exit=$RC time=$T s" | tee -a $LOG
  fi
done
echo "---" | tee -a $LOG
