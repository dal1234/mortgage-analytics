import snowflake.connector
import yaml


with open("config.yaml", "r") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

database_config = config["database"]

con = snowflake.connector.connect(
    user=database_config['user'],
    password=database_config['password'],
    account=database_config['account'],
    region=database_config['region'],
    warehouse=database_config['warehouse'],
    database=database_config['database'],
    autocommit=database_config['autocommit']
)

cur = con.cursor()

cur.execute("use schema fnma.public;")

cur.execute("TRUNCATE TABLE IF EXISTS fnma;")

cur.execute("""
    copy into fnma
    from @my_s3_stage
    file_format = (type = csv field_delimiter = '|' skip_header = 0);
    """)

con.close()