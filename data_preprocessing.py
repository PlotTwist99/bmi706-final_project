import pandas as pd

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
    df.loc[df['Country'] == country, na_cols] = df.loc[df['Country'] == country, na_cols].interpolate()
df.dropna(inplace=True)
df.to_csv('life_expectancy_clean.csv')
print(df.head())


