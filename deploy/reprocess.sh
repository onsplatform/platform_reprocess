#!/bin/bash
timestamp=`date +%Y/%m/%d-%H:%M:%S`
echo "System path is $PATH at $timestamp"

python reprocess/reprocess_executor.py