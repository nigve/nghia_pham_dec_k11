#!/bin/bash

CSV_FILE="../csv/chunk_to_process/$(basename $(ls ../csv/chunk_to_process/*.csv))"
PRODUCT_API_ENDPOINT="https://api.tiki.vn/product-detail/api/v1/products/"
SLEEP=60

mkdir -p "./raw_data"
mkdir -p "./raw_data/jsons"
touch "./raw_data/log.txt"
touch "./raw_data/404_log.txt"
touch "./raw_data/err_log.txt"

rm -f ./raw_data/jsons/*.json
> ./raw_data/log.txt
> ./raw_data/404_log.txt
> ./raw_data/err_log.txt

fetch_url() {
  product_id=$1
  url=("$PRODUCT_API_ENDPOINT$product_id")
  file_name="./raw_data/jsons/product_info_${product_id}.json"
  http_status=0

  while true; do
    http_status=$(curl -s -o "$file_name" -w "%{http_code}" "$url")

    if [ "$http_status" -eq 200 ]; then
      echo "Product $product_id fetched" >> "./raw_data/log.txt"
      break
    elif [ "$http_status" -eq 404 ]; then
      echo "Product $product_id not found (404)" >> "./raw_data/404_log.txt"
      rm -f "$file_name" 
      break
    elif [ "$http_status" -eq 429 ]; then
      # echo "Rate limit exceeded, sleeping for $SLEEP seconds..."
      sleep $SLEEP
    else
      echo "Failed to fetch $url ($http_status)" >> "./raw_data/err_log.txt"
      break
    fi
  done
}

line=0

while IFS= read -r product_id; do
  product_id=$(echo "$product_id" | tr -d '\r' | xargs)
  fetch_url "$product_id"
  line=$((line + 1))
  if [ "$line" -eq 1 ]; then
    echo "$line line processed..."
  else 
    echo "$line lines processed..."
  fi  

done < "$CSV_FILE"