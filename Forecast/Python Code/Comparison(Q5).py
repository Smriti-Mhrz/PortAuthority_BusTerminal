import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

print("=" * 80)
print("2019 BASELINE COMPARISON ANALYSIS")
print("How Current Usage Compares to Pre-COVID 2019 Baseline")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD DATA AND ESTABLISH 2019 BASELINE
# ============================================================================

df = pd.read_csv('FinalDataset.csv')
df['Week_Date'] = pd.to_datetime(df['Week_Date'])

print("\n" + "=" * 80)
print("STEP 1: ESTABLISHING 2019 PRE-COVID BASELINE")
print("=" * 80)

# Get 2019 baseline from the Baseline_2019_Passengers column
# This represents the weekly average from 2019
baseline_2019_weekly = df['Baseline_2019_Passengers'].iloc[0]  # Should be consistent
baseline_2019_annual = baseline_2019_weekly * 52

print(f"\n2019 PRE-COVID BASELINE (Last Normal Year Before Pandemic):")
print(f"  Average weekly passengers: {baseline_2019_weekly:,.0f}")
print(f"  Estimated annual total: {baseline_2019_annual:,.0f}")
print(f"  Source: Baseline_2019_Passengers field in dataset")

# ============================================================================
# STEP 2: CURRENT USAGE ANALYSIS (2020-2025)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: HISTORICAL COMPARISON (2020-2025 vs 2019)")
print("=" * 80)

# Aggregate weekly data
weekly_data = df.groupby('Week_Date').agg({
    'Passenger_Departures': 'sum',
    'Year': 'first',
    'Baseline_2019_Passengers': 'first'
}).reset_index()

# Yearly comparison
yearly_comparison = []

for year in sorted(weekly_data['Year'].unique()):
    year_data = weekly_data[weekly_data['Year'] == year]
    
    total_passengers = year_data['Passenger_Departures'].sum()
    weeks_count = len(year_data)
    avg_weekly = total_passengers / weeks_count if weeks_count > 0 else 0
    
    # Recovery percentage vs 2019
    recovery_pct = (avg_weekly / baseline_2019_weekly * 100) if baseline_2019_weekly > 0 else 0
    
    # Absolute difference
    diff_from_2019 = avg_weekly - baseline_2019_weekly
    pct_change = ((avg_weekly - baseline_2019_weekly) / baseline_2019_weekly * 100)
    
    yearly_comparison.append({
        'Year': year,
        'Total_Passengers': total_passengers,
        'Weeks': weeks_count,
        'Avg_Weekly': avg_weekly,
        'Recovery_%': recovery_pct,
        'Diff_from_2019': diff_from_2019,
        'Pct_Change': pct_change,
        'Status': 'Recovered ✓' if recovery_pct >= 100 else 'Below 2019 ✗'
    })

comparison_df = pd.DataFrame(yearly_comparison)

print(f"\n{'Year':<6} {'Total Annual':>15} {'Weeks':>7} {'Avg Weekly':>15} {'Recovery':>10} {'Change':>12} {'Status':>15}")
print("-" * 95)

for idx, row in comparison_df.iterrows():
    print(f"{int(row['Year']):<6} {row['Total_Passengers']:>15,.0f} {int(row['Weeks']):>7} "
          f"{row['Avg_Weekly']:>15,.0f} {row['Recovery_%']:>9.1f}% {row['Pct_Change']:>11.1f}% {row['Status']:>15}")

# ============================================================================
# STEP 3: GENERATE 2026-2030 FORECAST
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: FORECASTING 2026-2030 vs 2019 BASELINE")
print("=" * 80)

# Prepare time series
ts_data = weekly_data.set_index('Week_Date')['Passenger_Departures']

# Fit SARIMAX
print("\nFitting SARIMAX model...")
model = SARIMAX(ts_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 52))
results = model.fit(disp=False)

# Generate forecast
forecast_result = results.get_forecast(steps=260)
forecast_mean = forecast_result.predicted_mean

# Create forecast dates
last_date = ts_data.index[-1]
forecast_dates = pd.date_range(start=last_date + pd.Timedelta(weeks=1), periods=260, freq='W')

forecast_df = pd.DataFrame({
    'Week_Date': forecast_dates,
    'Forecasted_Passengers': forecast_mean.values
})

forecast_df['Year'] = forecast_df['Week_Date'].dt.year
forecast_2026_2030 = forecast_df[forecast_df['Year'] >= 2026].copy()

# Calculate forecast vs 2019
forecast_yearly = []

for year in sorted(forecast_2026_2030['Year'].unique()):
    year_forecast = forecast_2026_2030[forecast_2026_2030['Year'] == year]
    
    total_forecast = year_forecast['Forecasted_Passengers'].sum()
    weeks_count = len(year_forecast)
    avg_weekly_forecast = total_forecast / weeks_count
    
    recovery_pct = (avg_weekly_forecast / baseline_2019_weekly * 100)
    diff_from_2019 = avg_weekly_forecast - baseline_2019_weekly
    pct_change = ((avg_weekly_forecast - baseline_2019_weekly) / baseline_2019_weekly * 100)
    
    forecast_yearly.append({
        'Year': year,
        'Total_Passengers': total_forecast,
        'Weeks': weeks_count,
        'Avg_Weekly': avg_weekly_forecast,
        'Recovery_%': recovery_pct,
        'Diff_from_2019': diff_from_2019,
        'Pct_Change': pct_change,
        'Status': 'Above 2019 ✓' if recovery_pct >= 100 else 'Below 2019 ✗'
    })

forecast_comparison_df = pd.DataFrame(forecast_yearly)

print("\nFORECASTED COMPARISON (2026-2030 vs 2019):")
print(f"\n{'Year':<6} {'Total Annual':>15} {'Weeks':>7} {'Avg Weekly':>15} {'Recovery':>10} {'Change':>12} {'Status':>15}")
print("-" * 95)

for idx, row in forecast_comparison_df.iterrows():
    print(f"{int(row['Year']):<6} {row['Total_Passengers']:>15,.0f} {int(row['Weeks']):>7} "
          f"{row['Avg_Weekly']:>15,.0f} {row['Recovery_%']:>9.1f}% {row['Pct_Change']:>11.1f}% {row['Status']:>15}")

# ============================================================================
# STEP 4: COMBINED ANALYSIS (2020-2030)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: COMPLETE TIMELINE (2020-2030 vs 2019 BASELINE)")
print("=" * 80)

# Combine historical and forecast
combined_df = pd.concat([comparison_df, forecast_comparison_df], ignore_index=True)

print(f"\n{'Year':<8} {'Type':<12} {'Avg Weekly':>15} {'vs 2019':>15} {'Recovery %':>12} {'Status':>15}")
print("-" * 80)

for idx, row in combined_df.iterrows():
    year_type = "Historical" if row['Year'] <= 2025 else "Forecast"
    print(f"{int(row['Year']):<8} {year_type:<12} {row['Avg_Weekly']:>15,.0f} "
          f"{row['Diff_from_2019']:>15,.0f} {row['Recovery_%']:>11.1f}% {row['Status']:>15}")

# ============================================================================
# STEP 5: KEY INSIGHTS
# ============================================================================

print("\n" + "=" * 80)
print("KEY INSIGHTS: HOW CURRENT USAGE COMPARES TO 2019")
print("=" * 80)

# Latest actual year
latest_actual = comparison_df[comparison_df['Year'] == comparison_df['Year'].max()].iloc[0]
latest_year = int(latest_actual['Year'])

print(f"\n1. CURRENT STATUS ({latest_year}):")
print(f"   2019 Baseline: {baseline_2019_weekly:,.0f} passengers/week")
print(f"   {latest_year} Average: {latest_actual['Avg_Weekly']:,.0f} passengers/week")
print(f"   Recovery Rate: {latest_actual['Recovery_%']:.1f}% of 2019 levels")
print(f"   Difference: {latest_actual['Diff_from_2019']:+,.0f} passengers/week ({latest_actual['Pct_Change']:+.1f}%)")

if latest_actual['Recovery_%'] >= 100:
    print(f"   ✓ FULLY RECOVERED - Exceeding pre-COVID levels")
else:
    print(f"   ✗ NOT RECOVERED - Still below pre-COVID levels")

# Recovery trajectory
print(f"\n2. RECOVERY TRAJECTORY (2020-{latest_year}):")
years_to_recovery = None
for idx, row in comparison_df.iterrows():
    if row['Recovery_%'] >= 100 and years_to_recovery is None:
        years_to_recovery = int(row['Year'])
        print(f"   First year to exceed 2019: {years_to_recovery}")
        print(f"   Time to recovery: {years_to_recovery - 2019} years after 2019")
        break

if years_to_recovery is None:
    print(f"   ⚠️  Has not yet recovered to 2019 levels")

# Growth from lowest point
lowest_recovery = comparison_df['Recovery_%'].min()
lowest_year = comparison_df[comparison_df['Recovery_%'] == lowest_recovery].iloc[0]['Year']
print(f"\n   Lowest point: {int(lowest_year)} at {lowest_recovery:.1f}% of 2019")
print(f"   Growth since lowest: {latest_actual['Recovery_%'] - lowest_recovery:+.1f} percentage points")

# Forecast insights
forecast_2030 = forecast_comparison_df[forecast_comparison_df['Year'] == 2030].iloc[0]

print(f"\n3. PROJECTED 2030 vs 2019:")
print(f"   2030 Forecast: {forecast_2030['Avg_Weekly']:,.0f} passengers/week")
print(f"   Recovery Rate: {forecast_2030['Recovery_%']:.1f}% of 2019 levels")
print(f"   Difference: {forecast_2030['Diff_from_2019']:+,.0f} passengers/week ({forecast_2030['Pct_Change']:+.1f}%)")

# ============================================================================
# SAVE RESULTS
# ============================================================================

comparison_df.to_csv('Historical_vs_2019_Comparison.csv', index=False)
forecast_comparison_df.to_csv('Forecast_vs_2019_Comparison.csv', index=False)
combined_df.to_csv('Complete_2020_2030_vs_2019.csv', index=False)

print("\n✓ Saved analysis files:")
print("  - Historical_vs_2019_Comparison.csv")
print("  - Forecast_vs_2019_Comparison.csv")
print("  - Complete_2020_2030_vs_2019.csv")

# ============================================================================
# VISUALIZATION 1: RECOVERY TIMELINE
# ============================================================================

print("\n" + "=" * 80)
print("CREATING VISUALIZATIONS")
print("=" * 80)

fig, ax = plt.subplots(figsize=(16, 8))

# Plot data
years_hist = comparison_df['Year'].values
recovery_hist = comparison_df['Recovery_%'].values

years_forecast = forecast_comparison_df['Year'].values
recovery_forecast = forecast_comparison_df['Recovery_%'].values

# Historical line
ax.plot(years_hist, recovery_hist, marker='o', linewidth=3, markersize=10,
        color='#2E86AB', label='Historical (2020-2025)', zorder=3)

# Forecast line
ax.plot(years_forecast, recovery_forecast, marker='s', linewidth=3, markersize=10,
        color='#F18F01', linestyle='--', label='Forecast (2026-2030)', zorder=3)

# 2019 baseline reference
ax.axhline(100, color='green', linestyle='-', linewidth=2.5, alpha=0.7, 
           label='2019 Baseline (100%)', zorder=2)

# Shade recovery zone
ax.fill_between(combined_df['Year'], 0, 100, alpha=0.1, color='red', label='Below 2019')
ax.fill_between(combined_df['Year'], 100, combined_df['Recovery_%'].max() + 10, 
                alpha=0.1, color='green', label='Above 2019')

# Annotations
for year, recovery in zip(years_hist, recovery_hist):
    ax.annotate(f'{recovery:.0f}%', xy=(year, recovery), 
                xytext=(0, 10), textcoords='offset points',
                ha='center', fontsize=9, fontweight='bold')

for year, recovery in zip(years_forecast, recovery_forecast):
    ax.annotate(f'{recovery:.0f}%', xy=(year, recovery),
                xytext=(0, 10), textcoords='offset points',
                ha='center', fontsize=9, fontweight='bold', color='#F18F01')

ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Recovery Rate (% of 2019 Baseline)', fontsize=13, fontweight='bold')
ax.set_title('Bus Terminal Recovery Timeline: 2020-2030 vs 2019 Pre-COVID Baseline', 
             fontsize=15, fontweight='bold', pad=20)
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xticks(combined_df['Year'].unique())
ax.set_xticklabels([int(y) for y in combined_df['Year'].unique()])

plt.tight_layout()
plt.savefig('Recovery_Timeline_vs_2019.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Recovery_Timeline_vs_2019.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: ABSOLUTE COMPARISON
# ============================================================================

fig, ax = plt.subplots(figsize=(16, 8))

# Weekly averages
avg_weekly_hist = comparison_df['Avg_Weekly'].values
avg_weekly_forecast = forecast_comparison_df['Avg_Weekly'].values

# Bar chart
width = 0.7
x_hist = np.arange(len(years_hist))
x_forecast = np.arange(len(years_forecast)) + len(years_hist)

bars1 = ax.bar(x_hist, avg_weekly_hist, width, label='Historical', 
               color='#2E86AB', alpha=0.8, edgecolor='black')
bars2 = ax.bar(x_forecast, avg_weekly_forecast, width, label='Forecast',
               color='#F18F01', alpha=0.8, edgecolor='black')

# 2019 baseline line
ax.axhline(baseline_2019_weekly, color='green', linestyle='--', linewidth=2.5,
           label=f'2019 Baseline ({baseline_2019_weekly:,.0f}/week)', zorder=3)

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height/1000:.0f}K',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

for bar in bars2:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height/1000:.0f}K',
            ha='center', va='bottom', fontsize=9, fontweight='bold', color='#F18F01')

ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Average Weekly Passengers', fontsize=13, fontweight='bold')
ax.set_title('Weekly Passenger Volume: 2020-2030 vs 2019 Baseline', 
             fontsize=15, fontweight='bold', pad=20)
ax.set_xticks(np.concatenate([x_hist, x_forecast]))
ax.set_xticklabels([int(y) for y in np.concatenate([years_hist, years_forecast])])
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3, axis='y')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))

plt.tight_layout()
plt.savefig('Weekly_Volume_vs_2019.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Weekly_Volume_vs_2019.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: DIFFERENCE FROM 2019
# ============================================================================

fig, ax = plt.subplots(figsize=(16, 8))

# Difference from baseline
diff_hist = comparison_df['Diff_from_2019'].values
diff_forecast = forecast_comparison_df['Diff_from_2019'].values

all_years = np.concatenate([years_hist, years_forecast])
all_diffs = np.concatenate([diff_hist, diff_forecast])

# Color bars based on positive/negative
colors = ['red' if d < 0 else 'green' for d in all_diffs]
colors_hist = ['red' if d < 0 else 'green' for d in diff_hist]
colors_forecast = ['orange' if d < 0 else 'lightgreen' for d in diff_forecast]

all_colors = colors_hist + colors_forecast

bars = ax.bar(all_years, all_diffs, color=all_colors, alpha=0.7, edgecolor='black')

# Zero line
ax.axhline(0, color='black', linestyle='-', linewidth=1.5)

# Add value labels
for i, (year, diff) in enumerate(zip(all_years, all_diffs)):
    ax.text(year, diff, f'{diff/1000:+.0f}K',
            ha='center', va='bottom' if diff > 0 else 'top',
            fontsize=9, fontweight='bold')

ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Difference from 2019 Baseline (Passengers/Week)', fontsize=13, fontweight='bold')
ax.set_title('Passenger Volume Change vs 2019 Pre-COVID Baseline', 
             fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='green', alpha=0.7, label='Above 2019 (Historical)'),
    Patch(facecolor='lightgreen', alpha=0.7, label='Above 2019 (Forecast)'),
    Patch(facecolor='red', alpha=0.7, label='Below 2019 (Historical)'),
    Patch(facecolor='orange', alpha=0.7, label='Below 2019 (Forecast)')
]
ax.legend(handles=legend_elements, loc='best', fontsize=10)

plt.tight_layout()
plt.savefig('Difference_from_2019_Baseline.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Difference_from_2019_Baseline.png")
plt.close()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("EXECUTIVE SUMMARY: 2019 BASELINE COMPARISON")
print("=" * 80)

print(f"\n📊 2019 PRE-COVID BASELINE:")
print(f"   Weekly: {baseline_2019_weekly:,.0f} passengers")
print(f"   Annual: {baseline_2019_annual:,.0f} passengers")

print(f"\n📈 CURRENT STATUS ({latest_year}):")
print(f"   Weekly: {latest_actual['Avg_Weekly']:,.0f} passengers")
print(f"   Recovery: {latest_actual['Recovery_%']:.1f}% of 2019")
print(f"   Change: {latest_actual['Diff_from_2019']:+,.0f} passengers/week ({latest_actual['Pct_Change']:+.1f}%)")

print(f"\n🔮 PROJECTED 2030:")
print(f"   Weekly: {forecast_2030['Avg_Weekly']:,.0f} passengers")
print(f"   Recovery: {forecast_2030['Recovery_%']:.1f}% of 2019")
print(f"   Change: {forecast_2030['Diff_from_2019']:+,.0f} passengers/week ({forecast_2030['Pct_Change']:+.1f}%)")

print(f"\n✅ CONCLUSION:")
if latest_actual['Recovery_%'] >= 100:
    print(f"   The bus terminal HAS FULLY RECOVERED from COVID-19 impact.")
    print(f"   Current usage is {latest_actual['Recovery_%'] - 100:.1f}% ABOVE 2019 levels.")
else:
    shortfall = 100 - latest_actual['Recovery_%']
    print(f"   The bus terminal has NOT fully recovered to 2019 levels.")
    print(f"   Current usage is {shortfall:.1f}% BELOW 2019 baseline.")

print(f"\n   By 2030, usage is projected to be {forecast_2030['Recovery_%']:.1f}% of 2019 baseline,")
print(f"   representing a {forecast_2030['Pct_Change']:+.1f}% change from pre-COVID levels.")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

print("\n📁 Files Generated:")
print("   CSV Files:")
print("     - Historical_vs_2019_Comparison.csv")
print("     - Forecast_vs_2019_Comparison.csv")
print("     - Complete_2020_2030_vs_2019.csv")
print("\n   Visualizations:")
print("     - Recovery_Timeline_vs_2019.png")
print("     - Weekly_Volume_vs_2019.png")
print("     - Difference_from_2019_Baseline.png")
