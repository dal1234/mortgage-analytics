#!/bin/bash

access_token=$(curl -X POST \
  https://auth.pingone.com/4c2b23f9-52b1-4f8f-aa1f-1d477590770c/as/token \
  -H "Authorization: Basic $CLIENTID_CLIENTSECRET" \
  -H 'Content-type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials' | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

s3Uri=$(curl -X GET \
  https://api.fanniemae.com/v1/sf-loan-performance-data/primary-dataset \
  -H 'Content-Type: application/json' \
  -H "x-public-access-token: $access_token" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['s3Uri'])")

wget -O Performance_All.zip $s3Uri
sudo unzip Performance_All.zip -d csv_files
aws s3 mb s3://fnma-data
aws s3 sync csv_files s3://fnma-data
python3 copy_data_to_snowflake.py
python3 analyze_repurchases.py
aws s3 mb s3://fnma-repurchases-dev
aws s3 sync web-app s3://fnma-repurchases-dev