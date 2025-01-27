from helpers.bls import BLS
import pandas as pd

bls = BLS()

bls_series_the_employment_situation = {
    'Unemployment Rate (Seasonally Adjusted)' : 'LNS14000000',
    'Total Nonfarm Employmen - Seasonally Adjusted' : 'CES0000000001'
}

series = bls.get_series(list(bls_series_the_employment_situation.values()))
series_df = pd.DataFrame.from_dict(series)
series_df.to_csv('bls_test_multiple_series.csv', index=False)