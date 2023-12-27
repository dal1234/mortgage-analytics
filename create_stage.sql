CREATE STORAGE INTEGRATION s3_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::671181835860:role/snowflake_role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://fnma-data/');

DESC INTEGRATION s3_integration;

grant create stage on schema public to role ACCOUNTADMIN;

grant usage on integration s3_integration to role ACCOUNTADMIN;

use schema fnma.public;

-- drop stage my_s3_stage;
create stage my_s3_stage
  storage_integration = s3_integration
  url = 's3://fnma-data/'
  file_format = (type = csv field_delimiter = '|' skip_header = 0);
