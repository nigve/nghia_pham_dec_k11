#!/bin/bash
# set -x

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

mkdir -p ./raw_data_from_other_servers/

for server in "${servers[@]}"; do
  if [[ "$server" == "local" ]]; then
    echo "Skipping local server"
  else
    sftp ubuntu@"$server" <<EOF
cd UG/tiki/scripts/
get -r raw_data/ ./raw_data_from_other_servers/$server/
exit
EOF
  echo "Downloaded raw_data from $server"
  fi
done    