import pandas as pd
import pickle
import pycountry

# load the dataset
df = pd.read_csv("life_expectancy.csv")
# remove leading and trailing spaces from column names
df.columns = df.columns.str.strip()
# remove leading and trailing spaces from all string values in df
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# deal with missing value
# drop 10 countries without life expectancy 
rows_with_nan = df[df['Life expectancy'].isna()].index
df = df.drop(index=rows_with_nan)

# for other missing values, impute data by country
countries = df.Country.unique()
na_cols = [col for col in df.columns if df[col].isna().any()]
for country in countries:
    # interpolate missing values for each country
    df.loc[df['Country'] == country, na_cols] = df.loc[df['Country'] == country, na_cols].interpolate()

# For countries with more than 8 missing years for any column, we choose not to analyze this country for corresponding columns.
# Function to check and report countries with more than 8 missing years for any column
def report_missing_values(df):
    # dictionary: key=country, values=column names
    report_dict = {}
    grouped = df.groupby('Country')
    
    for country, group in grouped:
        cols_to_check = group.columns.drop(['Country', 'Year'])  # Assuming 'Country' and 'Year' should not be checked for missing values
        
        for col in cols_to_check:
            # count NaNs in the current column for the current country
            missing_count = group[col].isna().sum()
            
            if missing_count > 8:
                if country not in report_dict:
                    report_dict[country] = []
                report_dict[country].append(col)
                
    return report_dict

report = report_missing_values(df)
for country, cols in report.items():
    print(f"Country: {country} has more than 8 missing years in columns: {', '.join(cols)}")

pickle_file_path = "missing_values_report.pkl"
# save the dictionary to a file using pickle
with open(pickle_file_path, 'wb') as pickle_file:
    pickle.dump(report, pickle_file)
print(f"Report saved to {pickle_file_path}")

# add column country code as mapping to Country
country_names = df['Country'].unique()

# get the ISO Alpha-3 code for a given country name
def get_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except LookupError:
        # Handle cases where the country name does not match exactly
        # Implement any specific name adjustments here if necessary
        return None

# Map each country name to its ISO Alpha-3 code
country_codes = [get_country_code(name) for name in country_names]

# Create a DataFrame from the mapping
country_code_mapping = pd.DataFrame({
    'Country': country_names,
    'country-code': country_codes
})

# Merge this mapping back into your original DataFrame
df = df.merge(country_code_mapping, on='Country', how='left')

# Load the dictionary back from the pickle file
#with open(pickle_file_path, 'rb') as pickle_file:
#    loaded_report = pickle.load(pickle_file)

#print(loaded_report)

df.to_csv('life_expectancy_clean.csv')


