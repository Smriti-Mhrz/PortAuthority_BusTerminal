import pandas as pd

# Load your historical data
df = pd.read_csv('FinalDataset.csv')
df['Week_Date'] = pd.to_datetime(df['Week_Date'])

# Check data completeness by year
data_coverage = df.groupby('Year').agg({
    'Week_Date': ['min', 'max', 'count'],
    'Passenger_Departures': 'sum'
}).reset_index()

print("Data Coverage by Year:")
print(data_coverage)

# Check if 2025 is incomplete
weeks_2025 = df[df['Year'] == 2025]['Week_Date'].nunique()
print(f"\nWeeks of data in 2025: {weeks_2025} out of 52")

# If 2025 is partial, calculate what full year would be
if weeks_2025 < 52:
    partial_2025 = df[df['Year'] == 2025]['Passenger_Departures'].sum()
    projected_full_2025 = (partial_2025 / weeks_2025) * 52
    print(f"2025 Partial Year Total: {partial_2025:,.0f}")
    print(f"2025 Projected Full Year: {projected_full_2025:,.0f}")
