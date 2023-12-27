# mortgage-analytics
This repo is to be used to download Fannie Mae single family public data from their website and save it to a Snowflake database table.

## Requirements
- Snowflake
- AWS EC2 and S3
- Credentials for Fannie Mae public data
- Github account

## AWS Setup
Create IAM role `snowflake_role` with a policy `snowflake_access` found in this repo.
Create S3 bucket `s3://fnma_data`

## Snowflake setup
Create database FNMA
Create table `fnma` using `create_table_fnma.sql`
Run `create_stage.sql`

## Update database
Update `config.yaml` with your Snowflake user, password, account, region, and AWS storage_aws_arn

Spin up EC2 instance with 1,000 GB storage, access to S3, and allow inbound from own IP
SSH into your EC2 instance and run the following commands:

```
sudo yum install git
git clone https://oauth2:<github-account-code>@github.com/<username>/mortgage-analytics.git
sudo yum -y install python-pip
cd mortgage-analytics
pip3 install -r requirements.txt
export CLIENTID_CLIENTSECRET=<secret-code-from-fannie-mae>

bash download.sh
```
