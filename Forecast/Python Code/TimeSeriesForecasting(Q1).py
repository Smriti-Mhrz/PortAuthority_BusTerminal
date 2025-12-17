import pandas as pd

# Load forecast data
forecast_df = pd.read_csv('Weekly_Passenger_Forecast_2026_2030.csv')

# Convert date column
forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])
forecast_df['Year'] = forecast_df['ds'].dt.year

# Calculate annual totals for 2026-2030
annual = forecast_df.groupby('Year').agg({
    'yhat': 'sum',
    'yhat_lower': 'sum',
    'yhat_upper': 'sum'
}).reset_index()

annual.columns = ['Year', 'Total_Passengers', 'Lower_Bound', 'Upper_Bound']

# 2019 BASELINE (from your FinalDataset)
baseline_2019_annual = 125398 * 52  # Weekly baseline × 52 weeks = 6,520,696

# Calculate Growth vs 2019
annual['Growth_vs_2019'] = ((annual['Total_Passengers'] - baseline_2019_annual) / baseline_2019_annual * 100).round(2)

# Save corrected file
annual.to_csv('Annual_Passenger_Forecast_2026_2030_CORRECTED.csv', index=False)

print("Annual Forecast with Growth vs 2019 Baseline:")
print(annual)
print(f"\n2019 Baseline: {baseline_2019_annual:,.0f} annual passengers")
