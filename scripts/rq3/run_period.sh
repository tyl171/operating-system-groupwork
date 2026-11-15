#!/bin/bash
# Run PERIOD (DBDS) on one CVE program and save full logs (RQ3 / overhead measurement).
# Usage: bash scripts/rq3/run_period.sh <CVE-dir> <binary-name> [reps]
# Example: bash scripts/rq3/run_period.sh CVE-2016-7911 2016-7911 3
# Paths (inside the PERIOD container) can be overridden: ROOT=... RESULTS=...
#
# FIX vs. the first version: schedules were counted with  '^test [0-9]+:'  which misses the
# lines "test 0010 for prefix [[1]]: ..." and therefore UNDER-counted schedules for programs
# whose exploration uses prefixes (CVE-2011-2183, 2013-1792, 2016-1972, 2016-1973).
# The count now accepts both forms, and the tool's own summary (Round / Time) is logged too.
DIR=$1
BIN=$2
REPS=${3:-3}
ROOT=${ROOT:-/workdir/PERIOD}
BASE=$ROOT/evaluation/ConVul-CVE-Benchmarks
OUT=${RESULTS:-/results}/RQ3/$DIR
mkdir -p $OUT
LOG=$OUT/period_runs.log

export Con_PATH=$BASE/$DIR/ConConfig.${BIN}
cd $BASE/$DIR

echo "[$(date '+%F %T')] PERIOD run: $DIR / $BIN, reps=$REPS, depth=3" | tee -a $LOG
for i in $(seq 1 $REPS); do
  S=$(date +%s.%N)
  timeout 1800 $ROOT/tool/DBDS/run_PDS.py -y -d 3 ./$BIN > $OUT/period_run${i}.log 2>&1
  E=$(date +%s.%N)
  T=$(echo "$E - $S" | bc)
  CLEAN=$(sed 's/\x1b\[[0-9;]*m//g' $OUT/period_run${i}.log)
  TESTS=$(echo "$CLEAN" | grep -cE '^[[:space:]]*test [0-9]+')
  ROUNDS=$(echo "$CLEAN" | awk '/^Round/{print $3}' | tail -1)
  TOOLTIME=$(echo "$CLEAN" | awk '/^Time/{print $3}' | tail -1)
  ERRS=$(grep -c "Error Found" $OUT/period_run${i}.log)
  TMO=$(grep -c "\[Timeout" $OUT/period_run${i}.log)
  echo "run$i: wall=$T s, schedules=$TESTS, bugs_found=$ERRS, tool_rounds=${ROUNDS:-NA}, tool_time=${TOOLTIME:-NA}, timeouts=$TMO" | tee -a $LOG
done
echo "---" | tee -a $LOG
