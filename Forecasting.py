import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# For time series forecasting
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet

# For machine learning
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Set plot style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 80)
print("PORT AUTHORITY BUS TERMINAL PASSENGER FORECASTING")
print("2026-2030 Projections for Temporary Staging Facilities")
print("=" * 80)
print()

# ============================================================================
# STEP 1: LOAD AND PREPARE DATA
# ============================================================================

print("STEP 1: Loading FinalDataset...")
df = pd.read_csv('FinalDataset.csv')

# Convert Week_Date to datetime
df['Week_Date'] = pd.to_datetime(df['Week_Date'])

# Sort by date
df = df.sort_values('Week_Date')

print(f"✓ Loaded {len(df):,} records from {df['Week_Date'].min().date()} to {df['Week_Date'].max().date()}")
print(f"✓ Carriers: {df['Carrier_Name'].nunique()}")
print(f"✓ Date range: {(df['Week_Date'].max() - df['Week_Date'].min()).days} days")
print()

# ============================================================================
# STEP 2: EXPLORATORY DATA ANALYSIS
# ============================================================================

print("STEP 2: Analyzing Historical Patterns...")

# 2019 Baseline (Pre-COVID)
df_2019 = df[df['Year'] == 2019]
baseline_2019_total = df_2019['Passenger_Departures'].sum()
baseline_2019_weekly_avg = df_2019['Passenger_Departures'].mean()

print(f"\n2019 BASELINE (Pre-COVID):")
print(f"  Total Annual Passengers: {baseline_2019_total:,.0f}")
print(f"  Weekly Average: {baseline_2019_weekly_avg:,.0f}")
print(f"  Carriers in 2019: {df_2019['Carrier_Name'].nunique()}")

# Current Status (Latest available data)
df_latest_year = df[df['Year'] == df['Year'].max()]
latest_total = df_latest_year['Passenger_Departures'].sum()
latest_avg = df_latest_year['Passenger_Departures'].mean()
recovery_pct = (latest_total / baseline_2019_total * 100) if baseline_2019_total > 0 else 0

print(f"\nCURRENT STATUS ({df['Year'].max()}):")
print(f"  Total Passengers YTD: {latest_total:,.0f}")
print(f"  Weekly Average: {latest_avg:,.0f}")
print(f"  Recovery vs 2019: {recovery_pct:.1f}%")
print()

# ============================================================================
# STEP 3: IDENTIFY MOST IMPORTANT PREDICTIVE FACTORS
# ============================================================================

print("STEP 3: Identifying Most Important Predictive Factors...")
print("Using Random Forest Feature Importance Analysis")
print()

# Prepare features for ML model
df_ml = df.copy()

# Create features
df_ml['Month_Num'] = df_ml['Week_Date'].dt.month
df_ml['Week_Num'] = df_ml['Week_of_Year']
df_ml['Is_Summer'] = (df_ml['Season'] == 'Summer').astype(int)
df_ml['Is_Winter'] = (df_ml['Season'] == 'Winter').astype(int)
df_ml['Year_Num'] = df_ml['Year']

# Select features for model
feature_columns = [
    'Year_Num', 'Quarter', 'Month_Num', 'Week_Num',
    'Avg_Temp_F', 'Precipitation_Inches', 'Is_Severe_Weather',
    'Is_Holiday', 'Is_Tourism_Peak', 'Days_Since_Pandemic_Start',
    'Is_COVID_Period', 'Is_High_Inflation',
    'Is_Summer', 'Is_Winter', 'Baseline_2019_Passengers'
]

# Prepare training data (filter complete records)
df_ml_clean = df_ml.dropna(subset=feature_columns + ['Passenger_Departures'])

X = df_ml_clean[feature_columns]
y = df_ml_clean['Passenger_Departures']

# Train Random Forest
print("Training Random Forest model...")
rf_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
rf_model.fit(X, y)

# Feature importance
feature_importance = pd.DataFrame({
    'Feature': feature_columns,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nTOP 10 MOST IMPORTANT PREDICTIVE FACTORS:")
print("=" * 60)
for idx, row in feature_importance.head(10).iterrows():
    print(f"{row['Feature']:30s} {row['Importance']:.4f} {'█' * int(row['Importance'] * 100)}")
print()

# Save feature importance
feature_importance.to_csv('Feature_Importance_Analysis.csv', index=False)
print("✓ Saved: Feature_Importance_Analysis.csv")
print()

# ============================================================================
# STEP 4: FORECAST 2026-2030 - OVERALL PASSENGERS
# ============================================================================

print("STEP 4: Forecasting Overall Passengers 2026-2030...")
print()

# Aggregate weekly data
df_weekly_total = df.groupby('Week_Date').agg({
    'Passenger_Departures': 'sum',
    'Bus_Departures': 'sum'
}).reset_index()

# Use Prophet for forecasting (handles seasonality well)
prophet_df = df_weekly_total.rename(columns={
    'Week_Date': 'ds',
    'Passenger_Departures': 'y'
})

# Initialize Prophet with yearly and weekly seasonality
model_prophet = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    changepoint_prior_scale=0.5
)

# Fit model
print("Training Prophet forecasting model...")
model_prophet.fit(prophet_df)

# Create future dataframe (weekly from last date to end of 2030)
last_date = prophet_df['ds'].max()
periods = 52 * 6  # 6 years of weekly forecasts
future = model_prophet.make_future_dataframe(periods=periods, freq='W')

# Generate forecast
forecast = model_prophet.predict(future)

# Filter forecast for 2026-2030
forecast_future = forecast[forecast['ds'] > last_date].copy()
forecast_future['Year'] = forecast_future['ds'].dt.year
forecast_future['Month'] = forecast_future['ds'].dt.month
forecast_future['Week'] = forecast_future['ds'].dt.isocalendar().week

# Annual projections
annual_forecast = forecast_future.groupby('Year').agg({
    'yhat': 'sum',
    'yhat_lower': 'sum',
    'yhat_upper': 'sum'
}).reset_index()

annual_forecast.columns = ['Year', 'Projected_Passengers', 'Lower_Bound', 'Upper_Bound']

print("\nOVERALL PASSENGER PROJECTIONS (2026-2030):")
print("=" * 80)
print(f"{'Year':<8} {'Projected':>15} {'Lower Bound':>15} {'Upper Bound':>15} {'vs 2019':>12}")
print("-" * 80)

for _, row in annual_forecast.iterrows():
    vs_2019 = ((row['Projected_Passengers'] / baseline_2019_total) - 1) * 100 if baseline_2019_total > 0 else 0
    print(f"{int(row['Year']):<8} {row['Projected_Passengers']:>15,.0f} {row['Lower_Bound']:>15,.0f} {row['Upper_Bound']:>15,.0f} {vs_2019:>11.1f}%")

print()

# Save overall forecast
annual_forecast.to_csv('Annual_Passenger_Forecast_2026_2030.csv', index=False)
print("✓ Saved: Annual_Passenger_Forecast_2026_2030.csv")

# Save detailed weekly forecast
forecast_future[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'Year', 'Month', 'Week']].to_csv(
    'Weekly_Passenger_Forecast_2026_2030.csv', index=False
)
print("✓ Saved: Weekly_Passenger_Forecast_2026_2030.csv")
print()

# ============================================================================
# STEP 5: FORECAST BY INDIVIDUAL CARRIER
# ============================================================================

print("STEP 5: Forecasting by Individual Carrier...")
print()

carriers = df['Carrier_Name'].unique()
carrier_forecasts = []

for carrier in carriers:
    print(f"  Forecasting: {carrier}")
    
    # Filter data for carrier
    df_carrier = df[df['Carrier_Name'] == carrier].copy()
    df_carrier_agg = df_carrier.groupby('Week_Date')['Passenger_Departures'].sum().reset_index()
    
    # Prophet dataframe
    prophet_carrier = df_carrier_agg.rename(columns={
        'Week_Date': 'ds',
        'Passenger_Departures': 'y'
    })
    
    # Train model
    model_carrier = Prophet(yearly_seasonality=True, weekly_seasonality=False)
    model_carrier.fit(prophet_carrier)
    
    # Forecast
    future_carrier = model_carrier.make_future_dataframe(periods=periods, freq='W')
    forecast_carrier = model_carrier.predict(future_carrier)
    
    # Filter 2026-2030
    forecast_carrier_future = forecast_carrier[forecast_carrier['ds'] > last_date].copy()
    forecast_carrier_future['Year'] = forecast_carrier_future['ds'].dt.year
    
    # Annual summary
    annual_carrier = forecast_carrier_future.groupby('Year')['yhat'].sum().reset_index()
    annual_carrier['Carrier'] = carrier
    annual_carrier.columns = ['Year', 'Projected_Passengers', 'Carrier']
    
    carrier_forecasts.append(annual_carrier)

# Combine all carrier forecasts
all_carrier_forecasts = pd.concat(carrier_forecasts, ignore_index=True)

print()
print("CARRIER-LEVEL PROJECTIONS (2026-2030 Annual Average):")
print("=" * 70)

carrier_summary = all_carrier_forecasts.groupby('Carrier')['Projected_Passengers'].mean().sort_values(ascending=False).reset_index()
carrier_summary.columns = ['Carrier', 'Avg_Annual_Passengers']

for _, row in carrier_summary.iterrows():
    print(f"{row['Carrier']:30s} {row['Avg_Annual_Passengers']:>15,.0f}")

print()

# Save carrier forecasts
all_carrier_forecasts.to_csv('Carrier_Forecast_2026_2030.csv', index=False)
print("✓ Saved: Carrier_Forecast_2026_2030.csv")
print()

# ============================================================================
# STEP 6: IDENTIFY BUSIEST TIMES (Week, Month, Year)
# ============================================================================

print("STEP 6: Identifying Busiest Times for Staging Facilities...")
print()

# Weekly patterns
weekly_pattern = forecast_future.groupby('Week')['yhat'].mean().sort_values(ascending=False).reset_index()
weekly_pattern.columns = ['Week_of_Year', 'Avg_Passengers']

print("TOP 10 BUSIEST WEEKS (2026-2030 Average):")
print("=" * 50)
for _, row in weekly_pattern.head(10).iterrows():
    print(f"Week {int(row['Week_of_Year']):2d}  {row['Avg_Passengers']:>15,.0f}")
print()

# Monthly patterns
monthly_pattern = forecast_future.groupby('Month')['yhat'].mean().sort_values(ascending=False).reset_index()
monthly_pattern.columns = ['Month', 'Avg_Passengers']
month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
               7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
monthly_pattern['Month_Name'] = monthly_pattern['Month'].map(month_names)

print("BUSIEST MONTHS (2026-2030 Average):")
print("=" * 50)
for _, row in monthly_pattern.iterrows():
    print(f"{row['Month_Name']:12s} {row['Avg_Passengers']:>15,.0f}")
print()

# Yearly patterns (already have this)
print("BUSIEST YEARS (2026-2030):")
print("=" * 50)
for _, row in annual_forecast.iterrows():
    print(f"{int(row['Year']):4d}     {row['Projected_Passengers']:>15,.0f}")
print()

# Save busiest times
weekly_pattern.to_csv('Busiest_Weeks_2026_2030.csv', index=False)
monthly_pattern.to_csv('Busiest_Months_2026_2030.csv', index=False)

print("✓ Saved: Busiest_Weeks_2026_2030.csv")
print("✓ Saved: Busiest_Months_2026_2030.csv")
print()

# ============================================================================
# STEP 7: COMPARISON TO 2019 BASELINE
# ============================================================================

print("STEP 7: Comparing Forecasts to 2019 Baseline...")
print()

comparison_2019 = annual_forecast.copy()
comparison_2019['Baseline_2019'] = baseline_2019_total
comparison_2019['Difference'] = comparison_2019['Projected_Passengers'] - comparison_2019['Baseline_2019']
comparison_2019['Percent_Change'] = (comparison_2019['Difference'] / comparison_2019['Baseline_2019']) * 100

print("FORECAST VS 2019 PRE-COVID BASELINE:")
print("=" * 80)
print(f"{'Year':<8} {'Forecast':>15} {'2019 Baseline':>15} {'Difference':>15} {'% Change':>12}")
print("-" * 80)

for _, row in comparison_2019.iterrows():
    sign = '+' if row['Difference'] >= 0 else ''
    print(f"{int(row['Year']):<8} {row['Projected_Passengers']:>15,.0f} {row['Baseline_2019']:>15,.0f} {row['Difference']:>15,.0f} {sign}{row['Percent_Change']:>11.1f}%")

print()

comparison_2019.to_csv('Forecast_vs_2019_Baseline.csv', index=False)
print("✓ Saved: Forecast_vs_2019_Baseline.csv")
print()

# ============================================================================
# STEP 8: CREATE VISUALIZATIONS
# ============================================================================

print("STEP 8: Creating Visualizations...")
print()

# Figure 1: Historical + Forecast
fig, ax = plt.subplots(figsize=(14, 6))
historical_monthly = df.groupby(df['Week_Date'].dt.to_period('M'))['Passenger_Departures'].sum().reset_index()
historical_monthly['Week_Date'] = historical_monthly['Week_Date'].dt.to_timestamp()

ax.plot(historical_monthly['Week_Date'], historical_monthly['Passenger_Departures'], 
        label='Historical', linewidth=2, color='#2E86AB')

forecast_monthly = forecast_future.groupby(forecast_future['ds'].dt.to_period('M'))['yhat'].sum().reset_index()
forecast_monthly['ds'] = forecast_monthly['ds'].dt.to_timestamp()

ax.plot(forecast_monthly['ds'], forecast_monthly['yhat'], 
        label='Forecast 2026-2030', linewidth=2, color='#A23B72', linestyle='--')

ax.axvline(x=last_date, color='red', linestyle=':', linewidth=2, label='Forecast Start')
ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Monthly Passengers', fontsize=12, fontweight='bold')
ax.set_title('Port Authority Bus Terminal: Historical Data & 2026-2030 Forecast', 
             fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Forecast_Historical_vs_Future.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Forecast_Historical_vs_Future.png")

# Figure 2: Annual Forecast with Confidence Intervals
fig, ax = plt.subplots(figsize=(12, 6))
years = annual_forecast['Year'].astype(int)
ax.plot(years, annual_forecast['Projected_Passengers'], marker='o', linewidth=3, 
        markersize=10, color='#F18F01', label='Projected')
ax.fill_between(years, annual_forecast['Lower_Bound'], annual_forecast['Upper_Bound'], 
                alpha=0.3, color='#F18F01', label='Confidence Interval')
ax.axhline(y=baseline_2019_total, color='#2E86AB', linestyle='--', linewidth=2, 
           label='2019 Baseline')
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Annual Passengers', fontsize=12, fontweight='bold')
ax.set_title('Annual Passenger Forecast 2026-2030 (with 95% Confidence Interval)', 
             fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Annual_Forecast_with_CI.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Annual_Forecast_with_CI.png")

# Figure 3: Carrier Comparison
fig, ax = plt.subplots(figsize=(14, 8))
carrier_pivot = all_carrier_forecasts.pivot(index='Year', columns='Carrier', values='Projected_Passengers')
carrier_pivot.plot(kind='bar', ax=ax, width=0.8)
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Projected Passengers', fontsize=12, fontweight='bold')
ax.set_title('Carrier-Level Passenger Forecasts 2026-2030', fontsize=14, fontweight='bold')
ax.legend(title='Carrier', fontsize=9, title_fontsize=10)
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('Carrier_Forecast_Comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Carrier_Forecast_Comparison.png")

# Figure 4: Monthly Seasonality Pattern
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(monthly_pattern['Month_Name'], monthly_pattern['Avg_Passengers'], 
       color='#C73E1D', alpha=0.8, edgecolor='black')
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Average Weekly Passengers', fontsize=12, fontweight='bold')
ax.set_title('Seasonal Pattern: Busiest Months for Staging Facilities (2026-2030 Avg)', 
             fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('Monthly_Seasonality_Pattern.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Monthly_Seasonality_Pattern.png")

print()

# ============================================================================
# STEP 9: GENERATE SUMMARY REPORT
# ============================================================================

print("=" * 80)
print("FORECASTING COMPLETE - SUMMARY REPORT")
print("=" * 80)
print()

print("KEY FINDINGS:")
print("-" * 80)
print(f"1. OVERALL FORECAST (2026-2030 Average):")
print(f"   • Average Annual Passengers: {annual_forecast['Projected_Passengers'].mean():,.0f}")
print(f"   • Peak Year: {annual_forecast.loc[annual_forecast['Projected_Passengers'].idxmax(), 'Year']:.0f}")
print(f"   • Peak Annual Volume: {annual_forecast['Projected_Passengers'].max():,.0f}")
print()

print(f"2. MOST IMPORTANT PREDICTIVE FACTORS:")
for i, row in feature_importance.head(5).iterrows():
    print(f"   {i+1}. {row['Feature']:30s} (Importance: {row['Importance']:.3f})")
print()

print(f"3. TOP 3 CARRIERS (2026-2030 Average Annual Passengers):")
for i, row in carrier_summary.head(3).iterrows():
    print(f"   {i+1}. {row['Carrier']:30s} {row['Avg_Annual_Passengers']:>15,.0f}")
print()

print(f"4. BUSIEST PERIODS FOR STAGING FACILITIES:")
print(f"   • Busiest Month: {monthly_pattern.iloc[0]['Month_Name']}")
print(f"   • Busiest Week: Week {int(weekly_pattern.iloc[0]['Week_of_Year'])}")
print(f"   • Busiest Year: {annual_forecast.loc[annual_forecast['Projected_Passengers'].idxmax(), 'Year']:.0f}")
print()

avg_vs_2019 = ((annual_forecast['Projected_Passengers'].mean() / baseline_2019_total) - 1) * 100
print(f"5. COMPARISON TO 2019 BASELINE:")
print(f"   • 2019 Total: {baseline_2019_total:,.0f}")
print(f"   • 2026-2030 Average: {annual_forecast['Projected_Passengers'].mean():,.0f}")
print(f"   • Change: {'+' if avg_vs_2019 >= 0 else ''}{avg_vs_2019:.1f}%")
print()

print("=" * 80)
print("FILES GENERATED:")
print("-" * 80)
print("CSV Files:")
print("  ✓ Feature_Importance_Analysis.csv")
print("  ✓ Annual_Passenger_Forecast_2026_2030.csv")
print("  ✓ Weekly_Passenger_Forecast_2026_2030.csv")
print("  ✓ Carrier_Forecast_2026_2030.csv")
print("  ✓ Busiest_Weeks_2026_2030.csv")
print("  ✓ Busiest_Months_2026_2030.csv")
print("  ✓ Forecast_vs_2019_Baseline.csv")
print()
print("Visualizations:")
print("  ✓ Forecast_Historical_vs_Future.png")
print("  ✓ Annual_Forecast_with_CI.png")
print("  ✓ Carrier_Forecast_Comparison.png")
print("  ✓ Monthly_Seasonality_Pattern.png")
print()
print("=" * 80)
print("NEXT STEPS:")
print("-" * 80)
print("1. Import CSV files into Power BI for interactive dashboards")
print("2. Use carrier forecasts for resource allocation planning")
print("3. Plan staging facility capacity based on busiest periods")
print("4. Monitor actual vs forecast and adjust models quarterly")
print("=" * 80)
