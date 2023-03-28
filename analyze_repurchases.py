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


def create_quarterly_repurchase_curves(repurchase_curves, originations):
    repurchase_qtr_curves = repurchase_curves.groupby(['ORIG_QUARTER', 'REPURCHASE_QUARTER', 'LOAN_AGE_QTR']) \
        [['LOAN_COUNT', 'REPURCHASE_UPB', 'ORIG_UPB_AT_TERMINAL']].sum().reset_index() \
        .merge(originations.groupby('ORIG_QUARTER')[['ORIG_LOAN_COUNT', 'ORIG_UPB']].sum(), on = 'ORIG_QUARTER')

    repurchase_qtr_curves['repurchase_rate'] = repurchase_qtr_curves['LOAN_COUNT'] / repurchase_qtr_curves['ORIG_LOAN_COUNT']
    repurchase_qtr_curves['cum_repurchase_rate'] = repurchase_qtr_curves.groupby('ORIG_QUARTER')['repurchase_rate'].cumsum()

    repurchase_qtr_curves['repurchase_upb_rate'] = repurchase_qtr_curves['REPURCHASE_UPB'] / repurchase_qtr_curves['ORIG_UPB']
    repurchase_qtr_curves['cum_repurchase_upb_rate'] = repurchase_qtr_curves.groupby('ORIG_QUARTER')['repurchase_upb_rate'].cumsum()

    repurchase_qtr_curves['orig_upb_at_terminal_rate'] = repurchase_qtr_curves['ORIG_UPB_AT_TERMINAL'] / repurchase_qtr_curves['ORIG_UPB']
    repurchase_qtr_curves['cum_orig_upb_at_terminal_rate'] = repurchase_qtr_curves.groupby('ORIG_QUARTER')['orig_upb_at_terminal_rate'].cumsum()

    return repurchase_qtr_curves


def create_quarterly_trailing_repurchase_rates(repurchase_qtr_curves):

    df_sorted = repurchase_qtr_curves.sort_values(['REPURCHASE_QUARTER', 'LOAN_AGE_QTR'])
    df_sorted[['CUM_LOAN_COUNT', 'CUM_ORIG_LOAN_COUNT']] = df_sorted.groupby(['REPURCHASE_QUARTER'])[['LOAN_COUNT', 'ORIG_LOAN_COUNT']].cumsum()
    df_sorted_filtered = df_sorted[df_sorted['LOAN_AGE_QTR'].isin([7,9,11])]
    df_sorted_filtered['rate'] = round(df_sorted_filtered['CUM_LOAN_COUNT'] / df_sorted_filtered['CUM_ORIG_LOAN_COUNT'] * 100, 3)
    df_sorted_filtered_recent = df_sorted_filtered[df_sorted_filtered['REPURCHASE_QUARTER'] >= datetime.date(2020,12,1)]

    df_sorted_filtered_recent['REPURCHASE_QUARTER'] = pd.to_datetime(df_sorted_filtered_recent['REPURCHASE_QUARTER'], errors='coerce').dt.to_period('Q')

    df_sorted_filtered_recent_pivot = pd.pivot(df_sorted_filtered_recent, index='REPURCHASE_QUARTER', columns='LOAN_AGE_QTR', values='rate').reset_index()

    df_sorted_filtered_recent_pivot.columns.values[1] = "qtr8"
    df_sorted_filtered_recent_pivot.columns.values[2] = "qtr10"
    df_sorted_filtered_recent_pivot.columns.values[3] = "qtr12"

    return df_sorted_filtered_recent_pivot
    

def expand_grid(data_dict):
    rows = itertools.product(*data_dict.values())
    return pd.DataFrame.from_records(rows, columns=data_dict.keys())


def create_annual_repurchase_curves(repurchase_curves, originations):

    # Create grid of all origination years and loan ages
    max_loan_age_by_orig_year = repurchase_curves.groupby('ORIG_YEAR').agg({'LOAN_AGE': 'max'}) \
        .reset_index() \
            .rename(columns={'LOAN_AGE': 'LOAN_AGE_MAX'})
    year_age_grid = expand_grid({'ORIG_YEAR': repurchase_curves['ORIG_YEAR'].unique(), 
                                'LOAN_AGE': range(int(max(repurchase_curves['LOAN_AGE'])))})
    year_age_grid = year_age_grid[year_age_grid['LOAN_AGE'] != 0]
    year_age_grid = year_age_grid.merge(max_loan_age_by_orig_year)
    year_age_grid = year_age_grid[year_age_grid['LOAN_AGE'] <= year_age_grid['LOAN_AGE_MAX']]
    
    # Create cumulative metrics
    annual_repurchase_curves = repurchase_curves.groupby(['ORIG_YEAR', 'LOAN_AGE'])[['LOAN_COUNT', 'REPURCHASE_UPB', 'ORIG_UPB_AT_TERMINAL']].sum().reset_index()
    annual_repurchase_curves = annual_repurchase_curves.sort_values(['ORIG_YEAR', 'LOAN_AGE'])
    annual_repurchase_curves['CUM_COUNT'] = annual_repurchase_curves.groupby(['ORIG_YEAR'])['LOAN_COUNT'].cumsum()
    annual_repurchase_curves['CUM_UPB'] = annual_repurchase_curves.groupby(['ORIG_YEAR'])['REPURCHASE_UPB'].cumsum()
    annual_repurchase_curves['CUM_ORIG_UPB_AT_TERMINAL'] = annual_repurchase_curves.groupby(['ORIG_YEAR'])['ORIG_UPB_AT_TERMINAL'].cumsum()

    cum_annual_repurchase_curves = year_age_grid.merge(annual_repurchase_curves, on = ['ORIG_YEAR', 'LOAN_AGE'], how = 'left')
    cum_annual_repurchase_curves[['CUM_COUNT', 'CUM_UPB', 'CUM_ORIG_UPB_AT_TERMINAL']] = \
        cum_annual_repurchase_curves.groupby('ORIG_YEAR')[['CUM_COUNT', 'CUM_UPB', 'CUM_ORIG_UPB_AT_TERMINAL']].fillna(method='ffill')

    # Create summary by origination year
    orig_year_summary = repurchase_curves.groupby(['ORIG_YEAR']) \
        [['LOAN_COUNT', 'REPURCHASE_UPB', 'ORIG_UPB_AT_TERMINAL']].sum().reset_index() \
        .merge(originations.groupby('ORIG_YEAR')[['ORIG_LOAN_COUNT', 'ORIG_UPB']].sum(), on = 'ORIG_YEAR')
            
    orig_year_summary = orig_year_summary.rename(columns = {'LOAN_COUNT': 'ULT_REPURCHASE_LOAN_COUNT',
                                                        'REPURCHASE_UPB': 'ULT_REPURCHASE_UPB',
                                                'ORIG_UPB_AT_TERMINAL': 'ULT_ORIG_UPB_AT_TERMINAL'})

    # Merge cumulative metrics and summary by origination year
    tmp = orig_year_summary.merge(cum_annual_repurchase_curves.drop(['LOAN_COUNT'], axis=1), on = 'ORIG_YEAR')

    # Calculate rates
    tmp['ult_repurch_rate'] = round(tmp['ULT_REPURCHASE_LOAN_COUNT'] / tmp['ORIG_LOAN_COUNT'] * 100, 3)
    tmp['age_repurch_rate'] = round(tmp['CUM_COUNT'] / tmp['ORIG_LOAN_COUNT'] * 100, 3)
    tmp['age_ult_diff'] = tmp['ult_repurch_rate'] - tmp['age_repurch_rate']
    tmp['ult_repurch_upb_rate'] = round(tmp['ULT_ORIG_UPB_AT_TERMINAL'] / tmp['ORIG_UPB'] * 100, 3)
    tmp['age_repurch_upb_rate'] = round(tmp['CUM_UPB'] / tmp['ORIG_UPB'] * 100, 3)
    tmp['age_ult_upb_diff'] = tmp['ult_repurch_upb_rate'] - tmp['age_repurch_upb_rate']
    tmp['age_repurch_orig_upb_at_terminal_rate'] = round(tmp['CUM_ORIG_UPB_AT_TERMINAL'] / tmp['ORIG_UPB'] * 100, 3)

    # Fill in gaps
    periods = [6,12,24,36,48,54,63,72]
    df = expand_grid({'ORIG_YEAR': tmp['ORIG_YEAR'].unique(), 'LOAN_AGE': periods})
    tmp = df.merge(tmp, on = ['ORIG_YEAR', 'LOAN_AGE'], how = 'outer')

    # Clean up
    tmp.sort_values(['ORIG_YEAR', 'LOAN_AGE'], inplace=True)
    tmp = tmp.astype({'LOAN_AGE':'int'})

    return tmp


if __name__ == "__main__":

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

repurchase_curves = execute_query('repurchases_by_dates.sql')
originations = execute_query('orig_by_dates.sql')

repurchase_qtr_curves = create_quarterly_repurchase_curves(repurchase_curves, originations)
repurchase_qtr_curves_recent = repurchase_qtr_curves[repurchase_qtr_curves['ORIG_QUARTER'] >= datetime.date(2020,6,1)]
repurchase_qtr_curves_recent.to_csv('C:\\Users\\DavidLeonard\\Documents\\d3\\repurchase_qtr_curves_recent.csv') # matches

quarterly_trailing_repurchase = create_quarterly_trailing_repurchase_rates(repurchase_qtr_curves)
quarterly_trailing_repurchase.to_csv('C:\\Users\\DavidLeonard\\Documents\\d3\\quarterly_trailing_repurchase.csv')

repurchase_count_by_quarter = repurchase_qtr_curves.groupby('REPURCHASE_QUARTER')['LOAN_COUNT'].sum().reset_index()
repurchase_count_by_quarter.to_csv('C:\\Users\\DavidLeonard\\Documents\\d3\\repurchase_count_by_quarter.csv')

annual_repurchase_curves = create_annual_repurchase_curves(repurchase_curves, originations)
annual_repurchase_curves.to_csv('C:\\Users\\DavidLeonard\\Documents\\d3\\annual_repurchase_curves.csv')
