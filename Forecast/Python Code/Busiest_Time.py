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
plt.rcParams['font.size'] = 10

print("=" * 80)
print("BUSIEST TIMES FOR BUS TERMINAL STAGING FACILITIES 2026-2030")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD DATA AND GENERATE FORECAST
# ============================================================================

df = pd.read_csv('FinalDataset.csv')
df['Week_Date'] = pd.to_datetime(df['Week_Date'])

# Aggregate weekly data
weekly_data = df.groupby('Week_Date').agg({
    'Passenger_Departures': 'sum'
}).reset_index()

ts_data = weekly_data.set_index('Week_Date')['Passenger_Departures']

print("\nGenerating SARIMAX forecast...")

# Fit SARIMAX model
model = SARIMAX(ts_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 52))
results = model.fit(disp=False)

# Generate 260-week forecast
forecast_result = results.get_forecast(steps=260)
forecast_mean = forecast_result.predicted_mean
forecast_ci = forecast_result.conf_int(alpha=0.05)

# Create forecast dataframe
last_date = ts_data.index[-1]
forecast_dates = pd.date_range(start=last_date + pd.Timedelta(weeks=1), periods=260, freq='W')

forecast_df = pd.DataFrame({
    'Week_Date': forecast_dates,
    'Forecasted_Passengers': forecast_mean.values,
    'Lower_Bound': forecast_ci.iloc[:, 0].values,
    'Upper_Bound': forecast_ci.iloc[:, 1].values
})

forecast_df['Year'] = forecast_df['Week_Date'].dt.year
forecast_df['Month'] = forecast_df['Week_Date'].dt.month
forecast_df['Month_Name'] = forecast_df['Week_Date'].dt.strftime('%B')
forecast_df['Week_of_Year'] = forecast_df['Week_Date'].dt.isocalendar().week
forecast_df['Quarter'] = forecast_df['Week_Date'].dt.quarter

# Filter for 2026-2030
forecast_2026_2030 = forecast_df[forecast_df['Year'].between(2026, 2030)].copy()

print("✓ Forecast generated")

# ============================================================================
# STEP 2: IDENTIFY BUSIEST PERIODS
# ============================================================================

print("\n" + "=" * 80)
print("BUSIEST PERIODS ANALYSIS")
print("=" * 80)

# Busiest weeks
busiest_weeks = forecast_2026_2030.nlargest(20, 'Forecasted_Passengers')[
    ['Week_Date', 'Forecasted_Passengers', 'Year', 'Month_Name', 'Week_of_Year']
].copy()

print("\nTop 20 Busiest Weeks (2026-2030):")
print("-" * 80)
print(f"{'Rank':<6} {'Week Starting':<15} {'Year':<6} {'Month':<12} {'Passengers':>15}")
print("-" * 80)
for idx, (i, row) in enumerate(busiest_weeks.iterrows(), 1):
    print(f"{idx:<6} {row['Week_Date'].strftime('%Y-%m-%d'):<15} {row['Year']:<6} "
          f"{row['Month_Name']:<12} {row['Forecasted_Passengers']:>15,.0f}")

# Busiest months
monthly_avg = forecast_2026_2030.groupby(['Year', 'Month', 'Month_Name']).agg({
    'Forecasted_Passengers': ['mean', 'sum', 'count']
}).reset_index()

monthly_avg.columns = ['Year', 'Month', 'Month_Name', 'Avg_Weekly', 'Total_Monthly', 'Weeks']
monthly_avg = monthly_avg.sort_values('Avg_Weekly', ascending=False)

print("\n\nTop 10 Busiest Months (by average weekly passengers):")
print("-" * 80)
print(f"{'Rank':<6} {'Year-Month':<15} {'Avg Weekly':>15} {'Total Monthly':>15} {'Weeks':>8}")
print("-" * 80)
for idx, (i, row) in enumerate(monthly_avg.head(10).iterrows(), 1):
    print(f"{idx:<6} {int(row['Year'])}-{row['Month_Name']:<10} "
          f"{row['Avg_Weekly']:>15,.0f} {row['Total_Monthly']:>15,.0f} {int(row['Weeks']):>8}")

# Busiest years
yearly_stats = forecast_2026_2030.groupby('Year').agg({
    'Forecasted_Passengers': ['sum', 'mean', 'max', 'min']
}).reset_index()

yearly_stats.columns = ['Year', 'Total_Annual', 'Avg_Weekly', 'Peak_Week', 'Min_Week']

print("\n\nAnnual Summary (2026-2030):")
print("-" * 90)
print(f"{'Year':<6} {'Total Annual':>15} {'Avg Weekly':>15} {'Peak Week':>15} {'Min Week':>15}")
print("-" * 90)
for idx, row in yearly_stats.iterrows():
    print(f"{int(row['Year']):<6} {row['Total_Annual']:>15,.0f} {row['Avg_Weekly']:>15,.0f} "
          f"{row['Peak_Week']:>15,.0f} {row['Min_Week']:>15,.0f}")

# ============================================================================
# STEP 3: SAVE ANALYSIS RESULTS
# ============================================================================

busiest_weeks.to_csv('Busiest_Weeks_2026_2030.csv', index=False)
monthly_avg.to_csv('Busiest_Months_2026_2030.csv', index=False)
yearly_stats.to_csv('Annual_Summary_2026_2030.csv', index=False)

print("\n✓ Analysis files saved")

# ============================================================================
# VISUALIZATION 1: WEEKLY FORECAST WITH PEAKS HIGHLIGHTED
# ============================================================================

print("\n" + "=" * 80)
print("CREATING VISUALIZATIONS")
print("=" * 80)

fig, ax = plt.subplots(figsize=(16, 8))

# Plot weekly forecast
ax.plot(forecast_2026_2030['Week_Date'], forecast_2026_2030['Forecasted_Passengers'], 
        color='#2E86AB', linewidth=2, label='Weekly Forecast')

# Fill confidence interval
ax.fill_between(forecast_2026_2030['Week_Date'], 
                forecast_2026_2030['Lower_Bound'], 
                forecast_2026_2030['Upper_Bound'],
                alpha=0.2, color='#2E86AB', label='95% Confidence Interval')

# Highlight top 10 busiest weeks
top_10_weeks = forecast_2026_2030.nlargest(10, 'Forecasted_Passengers')
ax.scatter(top_10_weeks['Week_Date'], top_10_weeks['Forecasted_Passengers'],
           color='red', s=100, zorder=5, label='Top 10 Busiest Weeks', alpha=0.7)

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Passengers per Week', fontsize=12, fontweight='bold')
ax.set_title('Bus Terminal Weekly Passenger Forecast 2026-2030\nBusiest Weeks Highlighted', 
             fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)

# Format y-axis
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))

plt.tight_layout()
plt.savefig('Weekly_Forecast_with_Peaks.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Weekly_Forecast_with_Peaks.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: BUSIEST WEEKS BY YEAR
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

# Get top 5 busiest weeks per year
top_weeks_by_year = forecast_2026_2030.groupby('Year').apply(
    lambda x: x.nlargest(5, 'Forecasted_Passengers')
).reset_index(drop=True)

# Create grouped bar chart
years = top_weeks_by_year['Year'].unique()
x = np.arange(len(years))
width = 0.15

for i in range(5):
    week_data = []
    for year in years:
        year_data = top_weeks_by_year[top_weeks_by_year['Year'] == year]
        if len(year_data) > i:
            week_data.append(year_data.iloc[i]['Forecasted_Passengers'])
        else:
            week_data.append(0)
    
    ax.bar(x + i*width, week_data, width, label=f'Week #{i+1}', alpha=0.8)

ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Passengers', fontsize=12, fontweight='bold')
ax.set_title('Top 5 Busiest Weeks Per Year (2026-2030)', fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x + width * 2)
ax.set_xticklabels([int(y) for y in years])
ax.legend(title='Busiest Weeks', fontsize=9)
ax.grid(True, alpha=0.3, axis='y')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))

plt.tight_layout()
plt.savefig('Busiest_Weeks_by_Year.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Busiest_Weeks_by_Year.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: MONTHLY HEATMAP
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 6))

# Create pivot table for heatmap
monthly_pivot = forecast_2026_2030.groupby(['Year', 'Month'])['Forecasted_Passengers'].mean().reset_index()
heatmap_data = monthly_pivot.pivot(index='Month', columns='Year', values='Forecasted_Passengers')

# Create heatmap
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', 
            cbar_kws={'label': 'Average Weekly Passengers'},
            linewidths=0.5, ax=ax)

ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Month', fontsize=12, fontweight='bold')
ax.set_title('Average Weekly Passengers by Month and Year (2026-2030)\nHeatmap', 
             fontsize=14, fontweight='bold', pad=20)

# Set month labels
month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ax.set_yticklabels(month_labels, rotation=0)

plt.tight_layout()
plt.savefig('Monthly_Heatmap_2026_2030.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Monthly_Heatmap_2026_2030.png")
plt.close()

# ============================================================================
# VISUALIZATION 4: MONTHLY SEASONALITY PATTERN
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 7))

# Calculate average by month across all years
monthly_pattern = forecast_2026_2030.groupby('Month').agg({
    'Forecasted_Passengers': ['mean', 'std', 'min', 'max']
}).reset_index()

monthly_pattern.columns = ['Month', 'Mean', 'Std', 'Min', 'Max']

months = monthly_pattern['Month'].values
means = monthly_pattern['Mean'].values
stds = monthly_pattern['Std'].values

# Plot with error bars
ax.plot(months, means, marker='o', linewidth=2.5, markersize=8, 
        color='#2E86AB', label='Average Weekly Passengers')
ax.fill_between(months, means - stds, means + stds, alpha=0.3, color='#2E86AB')

# Highlight peak and low months
peak_month = monthly_pattern.loc[monthly_pattern['Mean'].idxmax(), 'Month']
low_month = monthly_pattern.loc[monthly_pattern['Mean'].idxmin(), 'Month']

ax.axvline(peak_month, color='red', linestyle='--', alpha=0.5, linewidth=2, label=f'Peak Month: {month_labels[int(peak_month)-1]}')
ax.axvline(low_month, color='blue', linestyle='--', alpha=0.5, linewidth=2, label=f'Low Month: {month_labels[int(low_month)-1]}')

ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Average Weekly Passengers', fontsize=12, fontweight='bold')
ax.set_title('Monthly Seasonality Pattern (2026-2030)\nAverage Across All Years', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(months)
ax.set_xticklabels(month_labels)
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))

plt.tight_layout()
plt.savefig('Monthly_Seasonality_Pattern.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Monthly_Seasonality_Pattern.png")
plt.close()

# ============================================================================
# VISUALIZATION 5: ANNUAL COMPARISON
# ============================================================================

fig, ax = plt.subplots(figsize=(12, 7))

# Annual totals
annual_totals = yearly_stats.copy()
years_list = annual_totals['Year'].astype(int).tolist()
totals = annual_totals['Total_Annual'].tolist()

bars = ax.bar(years_list, totals, color=['#06A77D', '#2E86AB', '#A23B72', '#F18F01', '#C73E1D'],
              edgecolor='black', linewidth=1.5, alpha=0.8)

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, totals)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val/1e6:.2f}M',
            ha='center', va='bottom', fontweight='bold', fontsize=11)

ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Total Annual Passengers', fontsize=12, fontweight='bold')
ax.set_title('Annual Passenger Forecast (2026-2030)\nTotal Passengers per Year', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(years_list)
ax.grid(True, alpha=0.3, axis='y')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1e6)}M'))

plt.tight_layout()
plt.savefig('Annual_Comparison_2026_2030.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Annual_Comparison_2026_2030.png")
plt.close()

# ============================================================================
# VISUALIZATION 6: QUARTERLY ANALYSIS
# ============================================================================

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Quarterly averages
quarterly_avg = forecast_2026_2030.groupby(['Year', 'Quarter'])['Forecasted_Passengers'].mean().reset_index()

# Plot 1: Line chart by quarter
for year in quarterly_avg['Year'].unique():
    year_data = quarterly_avg[quarterly_avg['Year'] == year]
    axes[0].plot(year_data['Quarter'], year_data['Forecasted_Passengers'], 
                 marker='o', linewidth=2.5, markersize=8, label=f'{int(year)}')

axes[0].set_xlabel('Quarter', fontsize=11, fontweight='bold')
axes[0].set_ylabel('Average Weekly Passengers', fontsize=11, fontweight='bold')
axes[0].set_title('Quarterly Passenger Trends (2026-2030)', fontsize=13, fontweight='bold')
axes[0].set_xticks([1, 2, 3, 4])
axes[0].set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])
axes[0].legend(title='Year', fontsize=9)
axes[0].grid(True, alpha=0.3)
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))

# Plot 2: Stacked bar chart
quarters = [1, 2, 3, 4]
bottom = np.zeros(4)

for year in sorted(quarterly_avg['Year'].unique()):
    year_data = quarterly_avg[quarterly_avg['Year'] == year].sort_values('Quarter')
    values = []
    for q in quarters:
        q_data = year_data[year_data['Quarter'] == q]
        if len(q_data) > 0:
            values.append(q_data.iloc[0]['Forecasted_Passengers'])
        else:
            values.append(0)
    
    axes[1].bar(quarters, values, bottom=bottom, label=f'{int(year)}', alpha=0.8)
    bottom += np.array(values)

axes[1].set_xlabel('Quarter', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Average Weekly Passengers (Stacked)', fontsize=11, fontweight='bold')
axes[1].set_title('Quarterly Passenger Distribution (Stacked)', fontsize=13, fontweight='bold')
axes[1].set_xticks(quarters)
axes[1].set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])
axes[1].legend(title='Year', fontsize=9)
axes[1].grid(True, alpha=0.3, axis='y')
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))

plt.tight_layout()
plt.savefig('Quarterly_Analysis_2026_2030.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Quarterly_Analysis_2026_2030.png")
plt.close()

# ============================================================================
# SUMMARY DASHBOARD
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY: BUSIEST TIMES FOR STAGING FACILITIES")
print("=" * 80)

print("\n📊 KEY FINDINGS:")
print("-" * 80)

# Busiest year
busiest_year = yearly_stats.loc[yearly_stats['Total_Annual'].idxmax()]
print(f"\n1. BUSIEST YEAR: {int(busiest_year['Year'])}")
print(f"   Total passengers: {busiest_year['Total_Annual']:,.0f}")
print(f"   Average weekly: {busiest_year['Avg_Weekly']:,.0f}")

# Busiest month pattern
busiest_month_num = monthly_pattern.loc[monthly_pattern['Mean'].idxmax(), 'Month']
busiest_month_avg = monthly_pattern.loc[monthly_pattern['Mean'].idxmax(), 'Mean']
print(f"\n2. BUSIEST MONTH (on average): {month_labels[int(busiest_month_num)-1]}")
print(f"   Average weekly: {busiest_month_avg:,.0f} passengers")

# Peak week
peak_week = forecast_2026_2030.loc[forecast_2026_2030['Forecasted_Passengers'].idxmax()]
print(f"\n3. SINGLE BUSIEST WEEK: {peak_week['Week_Date'].strftime('%B %d, %Y')}")
print(f"   Expected passengers: {peak_week['Forecasted_Passengers']:,.0f}")

# Design capacity recommendation
design_capacity = forecast_2026_2030['Upper_Bound'].quantile(0.95)
print(f"\n4. RECOMMENDED STAGING FACILITY CAPACITY:")
print(f"   Design for: {design_capacity:,.0f} passengers/week (95th percentile)")
print(f"   This ensures adequate capacity for peak demand periods")

print("\n" + "=" * 80)
print("✓ ALL VISUALIZATIONS AND ANALYSIS COMPLETE")
print("=" * 80)

print("\nFiles Created:")
print("  CSV Files:")
print("    - Busiest_Weeks_2026_2030.csv")
print("    - Busiest_Months_2026_2030.csv")
print("    - Annual_Summary_2026_2030.csv")
print("\n  Visualizations:")
print("    - Weekly_Forecast_with_Peaks.png")
print("    - Busiest_Weeks_by_Year.png")
print("    - Monthly_Heatmap_2026_2030.png")
print("    - Monthly_Seasonality_Pattern.png")
print("    - Annual_Comparison_2026_2030.png")
print("    - Quarterly_Analysis_2026_2030.png")
