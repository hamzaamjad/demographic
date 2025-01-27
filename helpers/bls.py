#!/usr/bin/env python3
"""API client implementations."""

from datetime import datetime

from .web import SessionManager

# -- API Objects ----------------------------------------------------------------------------


# -- Exceptions ---------------------------------------------------------------------------
class BLSError(Exception):
    """Raised when BLS API client runs into an error."""
    pass

# -- BLS ----------------------------------------------------------------------------------
class BLS:
    def __init__(
        self, 
        api_key: str = ''
        ) -> None:
        """Initialize the BLS interface.
        
        Args:
            api_key: BLS API Key
            
        Raises:
            Not configured at this time.
        """
        self.session = SessionManager().create_session()
        self.headers = {
            'Content-type': 'application/json'
            }
        # self.api_key = api_key
        self.api_key = 'cb0055340ae345fd92fa9a6954d4f6b0'
        self.api_url = {
            'base_url' : 'https://api.bls.gov/publicAPI/v2/',
            'endpoints' : {
                'timeseries' : [
                    'timeseries/data',
                    'timeseries/popular'
                ],
                'surveys' : [
                    'surveys'
                ]
            }
        }
        """
        Set the end_year to the current year by default
        Set the start_year to 10 or 20 years in the past based on the presence of an API key
            Registered Users can request up to 20 years per query
            Unregistered users may request up to 10 years per query
        """
        self.start_year = str(int(datetime.strftime(datetime.now(),"%Y")) - 10 if api_key == '' else 20)
        self.end_year = str(int(datetime.strftime(datetime.now(),"%Y")))

    def generate_laus(self, fips_state):
        '''
        Provided a state FIPS code, generates the state's LAUS Series IDs 
        >>> generate_laus('06')
        {'laus': ['LASST060000000000003',
            'LASST060000000000004',
            'LASST060000000000005',
            'LASST060000000000006',
            'LASST060000000000007',
            'LASST060000000000008']}
        '''
        fips_state = str(fips_state)
        if len(fips_state) < 2:
            fips_state = '0' + fips_state
        else:
            fips_state = fips_state # just in case...

        response = {
            'laus' : [
                f'LASST{fips_state}0000000000003', # Unemployment Rate
                f'LASST{fips_state}0000000000004', # Unemployment
                f'LASST{fips_state}0000000000005', # Employment
                f'LASST{fips_state}0000000000006', # Labor Force
                f'LASST{fips_state}0000000000007', # Employment-Populatio Ratio
                f'LASST{fips_state}0000000000008', # Labor Force Participation Rate
            ]
        }
        
        return(response)

    def generate_ces(self, fips_state):
        '''
        Provided a state FIPS code, generates the state's CES Series IDs 
        >>> generate_ces('06')
        {'ces': ['LASST060000000000003',
            'LASST060000000000004'
            ]}
        '''
        fips_state = str(fips_state)
        if len(fips_state) < 2:
            fips_state = '0' + fips_state

        response = {
            'ces' : [
                f'SMS{fips_state}000000000000001', # Total Nonfarm, All Employees, In Thousands, Seasonally Adjusted
                f'SMS{fips_state}000000500000001', # Total Private, All Employees, In Thousands, Seasonally Adjusted
                f'SMS{fips_state}000000600000001', # Goods Producing, All Employees, In Thousands, Seasonally Adjusted
                f'SMS{fips_state}000000700000001', # Service-Providing, All Employees, In Thousands, Seasonally Adjusted
                f'SMS{fips_state}000000800000001', # Private Service Providing, All Employees, In Thousands, Seasonally Adjusted
                f'SMS{fips_state}000001000000001', # Mining/Logging, All Employees, In Thousands, Seasonally Adjusted
                f'SMS{fips_state}000001500000001', # Mining/Logging/Construction, All Employees, In Thousands, Seasonally Adjusted
                f'SMS{fips_state}000002000000001', # Construction, All Employees, In Thousands, Seasonally Adjusted
                f'SMS{fips_state}000001500000001', # Mining/Logging/Construction, All Employees, In Thousands, Seasonally Adjusted
            ]
        }
        
        return(response)

    def get_series(self, series_list : list, start_year = None, end_year = None):
        """Retrieve values from multiple series.
        
        Args:
            series_list -- list of series IDs
            start_year -- start year for data pull, defaults to ten years in the past
            end_year -- end year for data pull, defaults to today's year
            
        Raises:
            Not configured at this time.
        """

        if len(series_list) > 50:
            raise BLSError(f"Maximum of 50 series allowed per query. Attempted to query for {len(series_list)} series. Please retry with less series.")

        if start_year is None:
            start_year = self.start_year
        else:
            start_year = str(start_year)
        if end_year is None:
            end_year = self.end_year
        else:
            start_year = str(end_year)
        
        data = {
            "seriesid": series_list,
            "startyear": start_year,
            "endyear": end_year,
            "catalog": False,
            "calculations" : False,
            "annualaverage" : False,
            "aspects": False,
            "registrationkey" : self.api_key
            }

        request_url = f"{self.api_url['base_url']}{self.api_url['endpoints']['timeseries'][0]}"
        
        response = self.session.post(
            request_url,
            json=data,
            headers=self.headers
        )

        series_data = ''

        try:
            json_data = response.json()
            bls_response = json_data['status']

            if bls_response == 'REQUEST_NOT_PROCESSED':
                print(json_data['status'])
                print(json_data['message'])
                series_data = json_data
            elif bls_response == "REQUEST_SUCCEEDED":
                bls_series = json_data['Results']['series']

                """
                2025.01.26 -- Hamza Amjad
                Note to self -- not including any period validation
                Python example on https://www.bls.gov/developers/api_python.htm
                Includes the following validation
                if 'M01' <= period <= 'M12':
                    x.add_row([seriesId,year,period,value,footnotes[0:-1]])
                """
                series_data = [
                    {
                        "series_id": series["seriesID"],
                        "year": data["year"],
                        "period": data["period"],
                        "value": data["value"],
                        "footnotes": data["footnotes"] if data["footnotes"] else "",
                    }
                    for series in bls_series
                    for data in series["data"]
                ]
            return(series_data)
        except:
            """
            2025.01.26 -- Hamza Amjad
            Note to self -- For any unhandled errors
            Return the response for manual checking
            """
            series_data = response
            return(series_data)