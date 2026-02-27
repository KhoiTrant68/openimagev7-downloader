#!/bin/bash

SCRIPT_NAME="download.py"
TOTAL_SAMPLES=30
STEP=5
VAL_TOTAL=10   
echo "🚀 Starting sequential download in chunks of $STEP..."

for (( start=0; start<TOTAL_SAMPLES; start+=STEP ))
do
    end=$(( start + STEP ))
    echo "------------------------------------------"
    echo "Processing Train Chunk: $start to $end"
    
    python "$SCRIPT_NAME" --train-range "$start:$end" --val-range "0:0"
done

echo "------------------------------------------"
echo "Processing Validation Range: 0 to $VAL_TOTAL"
python "$SCRIPT_NAME" --train-range "0:0" --val-range "0:$VAL_TOTAL"

echo "✅ All batches complete!"