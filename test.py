# %%

import snowflake.connector
import pandas as pd
import itertools
import datetime
import yaml


def execute_query(file_name):
    fd = open(file_name, 'r')
    script = fd.read()
    fd.close()
    cur = con.cursor()
    query_output = cur.execute(script)
    df = pd.DataFrame.from_records(iter(query_output), columns=[x[0] for x in query_output.description])
    return df

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

repurchase_curves = execute_query('repurchases_by_dates_seller.sql')
originations = execute_query('orig_by_dates.sql')

# %%

repurchase_count_by_quarter_seller = repurchase_curves.groupby(['REPURCHASE_QUARTER', 'SELLER'])[['LOAN_COUNT']].sum().reset_index()

# %%
def expand_grid(data_dict):
    rows = itertools.product(*data_dict.values())
    return pd.DataFrame.from_records(rows, columns=data_dict.keys())

quarter_seller_grid = expand_grid({'REPURCHASE_QUARTER': repurchase_count_by_quarter['REPURCHASE_QUARTER'].unique(), 
                            'SELLER': repurchase_count_by_quarter['SELLER'].unique()})

repurchase_count_by_quarter_seller = quarter_seller_grid.merge(repurchase_count_by_quarter, on = ['REPURCHASE_QUARTER', 'SELLER'], how='outer') \
    .fillna(0)

# %%
# repurchase_count_by_quarter_seller[repurchase_count_by_quarter_seller['SELLER'] == 'CrossCountry Mortgage, LLC']

repurchase_count_by_quarter_seller.to_csv('C:\\Users\\DavidLeonard\\Documents\\d3\\repurchase_count_by_quarter_seller.csv')