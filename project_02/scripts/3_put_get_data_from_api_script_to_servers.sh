#!/bin/bash
# set -x

SCRIPT_FILE="get_data_from_api.sh"

declare -a servers=(
  "local"
  "3.27.245.146" #nig_1
  "3.107.78.96" #nig_2
  "3.27.254.12" #nig_3
  "52.62.105.138" #nig_4
  "13.239.24.153" #nig_5
  "3.106.59.36" #nig_6
  "3.27.206.78" #nig_7
  "3.106.54.4" #nig_8
  "3.106.114.50" #nig_9
)

for server in "${servers[@]}"; do
  if [[ "$server" == "local" ]]; then
    echo "Skipping local server"
  else
    echo "Copying $SCRIPT_FILE to $server..."
    sftp ubuntu@"$server" <<EOF
mkdir UG
mkdir UG/tiki
mkdir UG/tiki/scripts
cd UG/tiki/scripts
put "$SCRIPT_FILE"
exit
EOF
  echo "Uploaded $SCRIPT_FILE to $server"  
  fi 
done