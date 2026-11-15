#!/bin/bash
# Build plain (non-instrumented, no ASAN) native binaries for all 10 CVE programs.
# Usage: bash /results/scripts/build_native.sh
ROOT_DIR=${ROOT_DIR:-/workdir/PERIOD}
export PATH=${ROOT_DIR}/clang+llvm/bin:${PATH}
export LD_LIBRARY_PATH=${ROOT_DIR}/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
BASE=$ROOT_DIR/evaluation/ConVul-CVE-Benchmarks

declare -A SRCS=(
  [CVE-2009-3547]=2009-3547.cpp
  [CVE-2011-2183]=2011-2183.cpp
  [CVE-2013-1792]=2013-1792.cpp
  [CVE-2015-7550]=2015-7550.cpp
  [CVE-2016-1972]=2016-1972.c
  [CVE-2016-1973]=2016-1973.cpp
  [CVE-2016-7911]=2016-7911.cpp
  [CVE-2016-9806]=2016-9806.cpp
  [CVE-2017-15265]=2017-15265.cpp
  [CVE-2017-6346]=2017-6346.cpp
)

for CVE in "${!SRCS[@]}"; do
  SRC=${SRCS[$CVE]}
  BIN=${SRC%.*}_native
  if [[ $SRC == *.c ]]; then CC=clang; else CC=clang++; fi
  echo "=== Building native: $CVE ($SRC -> $BIN) ==="
  cd $BASE/$CVE
  $CC -g ./$SRC -o ./$BIN -lpthread -ldl 2>&1 | tail -3
  if [ -f ./$BIN ]; then echo "OK: $BASE/$CVE/$BIN"; else echo "FAILED: $CVE"; fi
done
echo "ALL_NATIVE_DONE"
