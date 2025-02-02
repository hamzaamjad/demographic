import yaml
import json

from helpers.bls import BLS
import pandas as pd

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

bls = BLS(api_key=config["bls_api_key"])
# bls = BLS()

bls_series_the_employment_situation = {
    'Unemployment Rate (Seasonally Adjusted)' : 'LNS14000000',
    'Total Nonfarm Employment - Seasonally Adjusted' : 'CES0000000001'
}

series = bls.get_series(list(bls_series_the_employment_situation.values()), all_optional_params=True, return_raw_response=True)
# Convert response to JSON and write to file
json_data = series.json()
with open('bls_response.json', 'w') as f:
    json.dump(json_data, f, indent=4)


# series_df = pd.DataFrame.from_dict(series)
# series_df.to_csv('bls_test_multiple_series.csv', index=False)