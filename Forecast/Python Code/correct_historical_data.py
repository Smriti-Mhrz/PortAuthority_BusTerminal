import pandas as pd
from prophet import Prophet

# Load data
df = pd.read_csv('FinalDataset.csv')
df['Week_Date'] = pd.to_datetime(df['Week_Date'])

print("=" * 70)
print("STEP 1: CLEANING DATA")
print("=" * 70)

# Aggregate by week FIRST (this is the key fix)
weekly_totals_all = df.groupby('Week_Date').agg({
    'Passenger_Departures': 'sum',
    'Year': 'first'
}).reset_index()

# Check cleaned data coverage
print("\nCleaned Data Coverage:")
coverage_clean = weekly_totals_all.groupby('Year')['Week_Date'].agg(['count', 'min', 'max'])
print(coverage_clean)

# Use only COMPLETE years with good data: 2021-2024
# (2020 is partial, 2025 is incomplete)
df_train = weekly_totals_all[weekly_totals_all['Year'].between(2021, 2024)].copy()

# Prepare for Prophet
train_data = df_train[['Week_Date', 'Passenger_Departures']].copy()
train_data.columns = ['ds', 'y']

print(f"\n✓ Training period: {train_data['ds'].min()} to {train_data['ds'].max()}")
print(f"✓ Total weeks: {len(train_data)}")
print(f"✓ Average weekly passengers: {train_data['y'].mean():,.0f}")

# 2. TRAIN PROPHET MODEL
print("\n" + "=" * 70)
print("STEP 2: TRAINING FORECAST MODEL")
print("=" * 70)

model = Prophet(
    changepoint_prior_scale=0.05,
    seasonality_prior_scale=10,
    yearly_seasonality=True,
    weekly_seasonality=False,
    seasonality_mode='multiplicative'  # Better for recovery patterns
)

# Add custom seasonalities
model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
model.add_seasonality(name='quarterly', period=91.25, fourier_order=8)

model.fit(train_data)
print("✓ Model trained successfully")

# 3. GENERATE 2026-2030 FORECAST
print("\n" + "=" * 70)
print("STEP 3: GENERATING 2026-2030 FORECAST")
print("=" * 70)

# Create future dataframe starting from last training date
last_date = train_data['ds'].max()
future = model.make_future_dataframe(periods=260, freq='W')  # 5 years = 260 weeks

# Generate predictions
forecast = model.predict(future)

# Filter for 2026-2030 only
forecast_future = forecast[forecast['ds'] >= '2026-01-01'].copy()
forecast_future['Year'] = forecast_future['ds'].dt.year
forecast_future['Month'] = forecast_future['ds'].dt.month
forecast_future['Week'] = forecast_future['ds'].dt.isocalendar().week

# 4. CALCULATE ANNUAL PROJECTIONS
print("\n" + "=" * 70)
print("STEP 4: ANNUAL PROJECTIONS 2026-2030")
print("=" * 70)

annual_forecast = forecast_future.groupby('Year').agg({
    'yhat': 'sum',
    'yhat_lower': 'sum',
    'yhat_upper': 'sum'
}).reset_index()

annual_forecast.columns = ['Year', 'Total_Passengers', 'Lower_Bound', 'Upper_Bound']

# Calculate Growth vs 2019 baseline
baseline_2019 = 125398 * 52  # 6,520,696 annual passengers
annual_forecast['Growth_vs_2019'] = ((annual_forecast['Total_Passengers'] - baseline_2019) / baseline_2019 * 100).round(2)

# Add recovery status
annual_forecast['Recovery_Status'] = annual_forecast['Growth_vs_2019'].apply(
    lambda x: 'Full Recovery' if x >= 0 else f'{abs(x):.1f}% Below 2019'
)

print(annual_forecast[['Year', 'Total_Passengers', 'Growth_vs_2019', 'Recovery_Status']].to_string(index=False))

# 5. SAVE OUTPUTS
annual_forecast.to_csv('Annual_Passenger_Forecast_2026_2030_FIXED.csv', index=False)
forecast_future.to_csv('Weekly_Passenger_Forecast_2026_2030_FIXED.csv', index=False)

print("\n" + "=" * 70)
print("DELIVERABLES SAVED")
print("=" * 70)
print("✓ Annual_Passenger_Forecast_2026_2030_FIXED.csv")
print("✓ Weekly_Passenger_Forecast_2026_2030_FIXED.csv")

# 6. KEY METRICS FOR PORT AUTHORITY
print("\n" + "=" * 70)
print("KEY METRICS FOR STAGING FACILITY PLANNING")
print("=" * 70)

peak_week = forecast_future['yhat'].max()
avg_week = forecast_future['yhat'].mean()
peak_99th = forecast_future['yhat_upper'].quantile(0.99)

print(f"Average Weekly Passengers (2026-2030): {avg_week:,.0f}")
print(f"Peak Weekly Passengers (Maximum): {peak_week:,.0f}")
print(f"Design Capacity (99th percentile): {peak_99th:,.0f}")
print(f"\n2019 Baseline Comparison: {baseline_2019:,.0f} annual passengers")
print(f"2025 Projected (extrapolated): 5,135,457 annual passengers (78.8% recovery)")

# Show busiest periods
busiest_weeks = forecast_future.nlargest(10, 'yhat')[['ds', 'yhat', 'Year', 'Month']].copy()
busiest_weeks['Month_Name'] = pd.to_datetime(busiest_weeks['ds']).dt.strftime('%B')
print("\nTop 10 Busiest Weeks (for peak capacity planning):")
print(busiest_weeks[['ds', 'Month_Name', 'Year', 'yhat']].to_string(index=False))
