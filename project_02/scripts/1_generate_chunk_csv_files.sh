#!/bin/bash

CSV_FILE="../csv/products_0-200000.csv"
CHUNK_SIZE=20000
OUT_DIR="../csv/chunks"

mkdir -p $OUT_DIR

header=$(head -n 1 "$CSV_FILE")

tail -n +2 "$CSV_FILE" | sort -n | split -l $CHUNK_SIZE -d --additional-suffix=.csv - "$OUT_DIR/chunk_"