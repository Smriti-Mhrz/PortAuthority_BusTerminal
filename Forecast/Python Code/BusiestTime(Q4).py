import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import os
warnings.filterwarnings('ignore')

print("=" * 80)
print("CARRIER-LEVEL PASSENGER FORECAST 2026-2030")
print("Port Authority Bus Terminal - Individual Carrier Projections")
print("=" * 80)

# Load data
df = pd.read_csv('FinalDataset.csv')
df['Week_Date'] = pd.to_datetime(df['Week_Date'])

# ============================================================================
# STEP 1: IDENTIFY ALL CARRIERS
# ============================================================================

carriers = df['Carrier_Name'].unique()
print(f"\nTotal carriers in dataset: {len(carriers)}")
print("\nCarriers:")
for i, carrier in enumerate(carriers, 1):
    total_passengers = df[df['Carrier_Name'] == carrier]['Passenger_Departures'].sum()
    print(f"  {i}. {carrier}: {total_passengers:,.0f} total passengers (2020-2025)")

# ============================================================================
# STEP 2: FORECAST EACH CARRIER INDIVIDUALLY
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: FITTING SARIMAX MODELS FOR EACH CARRIER")
print("=" * 80)

carrier_forecasts = {}

for carrier in carriers:
    print(f"\n{'='*70}")
    print(f"Processing: {carrier}")
    print(f"{'='*70}")
    
    # Get carrier-specific weekly data
    carrier_data = df[df['Carrier_Name'] == carrier].groupby('Week_Date').agg({
        'Passenger_Departures': 'sum'
    }).reset_index()
    
    # Check if enough data points
    if len(carrier_data) < 52:
        print(f"  ⚠️  Insufficient data ({len(carrier_data)} weeks) - Skipping")
        continue
    
    # Set index
    carrier_ts = carrier_data.set_index('Week_Date')['Passenger_Departures']
    
    print(f"  Data points: {len(carrier_ts)} weeks")
    print(f"  Date range: {carrier_ts.index.min()} to {carrier_ts.index.max()}")
    print(f"  Average weekly: {carrier_ts.mean():,.0f} passengers")
    
    try:
        # Fit SARIMAX model for this carrier
        if len(carrier_ts) < 100:
            model = SARIMAX(carrier_ts, order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))
        else:
            model = SARIMAX(carrier_ts, order=(1, 1, 1), seasonal_order=(1, 1, 1, 52))
        
        results = model.fit(disp=False, maxiter=200)
        
        # Generate 260-week forecast (5 years)
        forecast_result = results.get_forecast(steps=260)
        forecast_mean = forecast_result.predicted_mean
        forecast_ci = forecast_result.conf_int(alpha=0.05)
        
        # Store results
        carrier_forecasts[carrier] = {
            'forecast': forecast_mean,
            'lower_ci': forecast_ci.iloc[:, 0],
            'upper_ci': forecast_ci.iloc[:, 1],
            'model': results
        }
        
        print(f"  ✓ Forecast completed successfully")
        print(f"  Model AIC: {results.aic:.2f}")
        
    except Exception as e:
        print(f"  ✗ Forecast failed: {str(e)[:50]}")
        continue

print(f"\n✓ Successfully forecasted {len(carrier_forecasts)} out of {len(carriers)} carriers")

# ============================================================================
# STEP 3: COMPILE FORECASTS INTO DATAFRAMES
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: COMPILING CARRIER FORECASTS")
print("=" * 80)

# Create forecast dates
last_date = df['Week_Date'].max()
forecast_dates = pd.date_range(start=last_date + pd.Timedelta(weeks=1), periods=260, freq='W')

# Create master forecast dataframe
all_forecasts = []

for carrier, forecast_data in carrier_forecasts.items():
    carrier_df = pd.DataFrame({
        'Week_Date': forecast_dates,
        'Carrier_Name': carrier,
        'Forecasted_Passengers': forecast_data['forecast'].values,
        'Lower_Bound_95': forecast_data['lower_ci'].values,
        'Upper_Bound_95': forecast_data['upper_ci'].values
    })
    
    carrier_df['Year'] = carrier_df['Week_Date'].dt.year
    carrier_df['Month'] = carrier_df['Week_Date'].dt.month
    
    all_forecasts.append(carrier_df)

# Combine all carriers
forecast_df = pd.concat(all_forecasts, ignore_index=True)
forecast_2026_2030 = forecast_df[forecast_df['Year'] >= 2026].copy()

print(f"✓ Compiled forecasts for {forecast_2026_2030['Carrier_Name'].nunique()} carriers")

# ============================================================================
# STEP 4: ANNUAL PROJECTIONS BY CARRIER
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: ANNUAL PASSENGER PROJECTIONS BY CARRIER (2026-2030)")
print("=" * 80)

annual_by_carrier = forecast_2026_2030.groupby(['Carrier_Name', 'Year']).agg({
    'Forecasted_Passengers': 'sum',
    'Lower_Bound_95': 'sum',
    'Upper_Bound_95': 'sum'
}).reset_index()

annual_by_carrier.columns = ['Carrier_Name', 'Year', 'Projected_Passengers', 
                              'Conservative_Estimate', 'Optimistic_Estimate']

annual_by_carrier['Projected_Passengers'] = annual_by_carrier['Projected_Passengers'].round(0)
annual_by_carrier['Conservative_Estimate'] = annual_by_carrier['Conservative_Estimate'].round(0)
annual_by_carrier['Optimistic_Estimate'] = annual_by_carrier['Optimistic_Estimate'].round(0)

# Display each carrier's forecast
for carrier in annual_by_carrier['Carrier_Name'].unique():
    print(f"\n{carrier}:")
    print("-" * 70)
    carrier_annual = annual_by_carrier[annual_by_carrier['Carrier_Name'] == carrier]
    print(carrier_annual[['Year', 'Projected_Passengers']].to_string(index=False))
    
    total_5yr = carrier_annual['Projected_Passengers'].sum()
    avg_annual = total_5yr / 5
    print(f"\n5-Year Total (2026-2030): {total_5yr:,.0f} passengers")
    print(f"Annual Average: {avg_annual:,.0f} passengers")

# ============================================================================
# STEP 5: CARRIER MARKET SHARE PROJECTIONS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: CARRIER MARKET SHARE ANALYSIS")
print("=" * 80)

total_by_year = annual_by_carrier.groupby('Year')['Projected_Passengers'].sum().reset_index()
total_by_year.columns = ['Year', 'Total_Passengers']

market_share = annual_by_carrier.merge(total_by_year, on='Year')
market_share['Market_Share_%'] = (market_share['Projected_Passengers'] / market_share['Total_Passengers'] * 100).round(2)

print("\nProjected Market Share by Carrier (2030):")
print("-" * 70)
market_2030 = market_share[market_share['Year'] == 2030].sort_values('Market_Share_%', ascending=False)
print(f"{'Carrier':<30} {'Passengers':>15} {'Market Share':>15}")
print("-" * 70)
for idx, row in market_2030.iterrows():
    print(f"{row['Carrier_Name']:<30} {row['Projected_Passengers']:>15,.0f} {row['Market_Share_%']:>14.1f}%")

# ============================================================================
# STEP 6: GROWTH RATE ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5: CARRIER GROWTH RATE ANALYSIS (2026-2030)")
print("=" * 80)

growth_analysis = []

for carrier in annual_by_carrier['Carrier_Name'].unique():
    carrier_data = annual_by_carrier[annual_by_carrier['Carrier_Name'] == carrier].sort_values('Year')
    
    if len(carrier_data) >= 2:
        passengers_2026 = carrier_data[carrier_data['Year'] == 2026]['Projected_Passengers'].values
        passengers_2030 = carrier_data[carrier_data['Year'] == 2030]['Projected_Passengers'].values
        
        if len(passengers_2026) > 0 and len(passengers_2030) > 0 and passengers_2026[0] > 0:
            cagr = ((passengers_2030[0] / passengers_2026[0]) ** (1/4) - 1) * 100
            
            growth_analysis.append({
                'Carrier': carrier,
                '2026_Passengers': passengers_2026[0],
                '2030_Passengers': passengers_2030[0],
                'CAGR_%': cagr,
                'Total_Growth_%': ((passengers_2030[0] - passengers_2026[0]) / passengers_2026[0] * 100)
            })

growth_df = pd.DataFrame(growth_analysis).sort_values('CAGR_%', ascending=False)

print(f"\n{'Carrier':<30} {'2026':>15} {'2030':>15} {'CAGR':>10} {'Total Growth':>15}")
print("-" * 95)
for idx, row in growth_df.iterrows():
    print(f"{row['Carrier']:<30} {row['2026_Passengers']:>15,.0f} {row['2030_Passengers']:>15,.0f} "
          f"{row['CAGR_%']:>9.1f}% {row['Total_Growth_%']:>14.1f}%")

# ============================================================================
# STEP 7: SAVE RESULTS (with error handling)
# ============================================================================

print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Function to safely save CSV
def safe_save_csv(dataframe, filename):
    try:
        dataframe.to_csv(filename, index=False)
        print(f"✓ Saved: {filename}")
    except PermissionError:
        alt_filename = filename.replace('.csv', '_NEW.csv')
        dataframe.to_csv(alt_filename, index=False)
        print(f"⚠️  Original file locked. Saved as: {alt_filename}")
    except Exception as e:
        print(f"✗ Failed to save {filename}: {str(e)}")

# Save all files with error handling
safe_save_csv(forecast_2026_2030, 'Carrier_Weekly_Forecast_2026_2030.csv')
safe_save_csv(annual_by_carrier, 'Carrier_Annual_Forecast_2026_2030.csv')
safe_save_csv(market_share, 'Carrier_Market_Share_Projections.csv')
safe_save_csv(growth_df, 'Carrier_Growth_Analysis.csv')

print("\n" + "=" * 80)
print("CARRIER-LEVEL FORECAST COMPLETE")
print("=" * 80)
