import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("COMPREHENSIVE FACTOR IMPORTANCE ANALYSIS")
print("Senior Data Analyst Level - Bus Terminal Passenger Forecasting")
print("=" * 80)

# Load data
df = pd.read_csv('FinalDataset.csv')
df['Week_Date'] = pd.to_datetime(df['Week_Date'])

# ============================================================================
# FEATURE ENGINEERING: CREATE ADDITIONAL PREDICTIVE FACTORS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 1: FEATURE ENGINEERING")
print("=" * 80)

# Aggregate weekly data with comprehensive factors
weekly_data = df.groupby('Week_Date').agg({
    'Passenger_Departures': 'sum',
    # Service Factors
    'Bus_Departures': 'sum',
    'Passengers_Per_Bus': 'mean',
    # Calendar/Time Factors
    'Year': 'first',
    'Month': 'first',
    'Quarter': 'first',
    'Week_of_Year': 'first',
    'Is_Holiday': 'max',
    'Is_Holiday_Season': 'max',
    'Is_Tourism_Peak': 'max',
    # Weather Factors
    'Is_Severe_Weather': 'max',
    'Is_Snow_Week': 'max',
    'Is_Hot_Week': 'max',
    'Is_Cold_Week': 'max',
    'Avg_Temp_F': 'mean',
    'Precipitation_Inches': 'sum',
    'Snow_Inches': 'sum',
    # Economic Factors
    'Is_High_Inflation': 'max',
    # COVID/Recovery Factors
    'Is_COVID_Period': 'max',
    'Days_Since_Pandemic_Start': 'mean',
    # Recovery Metrics
    'Passenger_Recovery_Percent': 'mean',
    'Bus_Recovery_Percent': 'mean',
    'Baseline_2019_Passengers': 'first'
}).reset_index()

# Sort by date
weekly_data = weekly_data.sort_values('Week_Date').reset_index(drop=True)

print(f"✓ Base features extracted: {len(weekly_data)} weeks")

# Create lagged features
weekly_data['Passengers_Lag1'] = weekly_data['Passenger_Departures'].shift(1)
weekly_data['Passengers_Lag4'] = weekly_data['Passenger_Departures'].shift(4)  # Month ago
weekly_data['Passengers_MA4'] = weekly_data['Passenger_Departures'].rolling(window=4).mean()
weekly_data['Passengers_MA12'] = weekly_data['Passenger_Departures'].rolling(window=12).mean()

# Week-over-week change
weekly_data['Passenger_WoW_Change'] = weekly_data['Passenger_Departures'].pct_change()

# Year-over-year growth (if data available)
weekly_data['Week_Year'] = weekly_data['Week_Date'].dt.isocalendar().week
weekly_data = weekly_data.sort_values(['Year', 'Week_Year'])
weekly_data['Passenger_YoY_Growth'] = weekly_data.groupby('Week_Year')['Passenger_Departures'].pct_change()

# Recovery rate (vs 2019 baseline)
weekly_data['Recovery_Rate'] = (weekly_data['Passenger_Departures'] / weekly_data['Baseline_2019_Passengers']) * 100

# Seasonal indicators
weekly_data['Is_Q1'] = (weekly_data['Quarter'] == 1).astype(int)
weekly_data['Is_Q2'] = (weekly_data['Quarter'] == 2).astype(int)
weekly_data['Is_Q3'] = (weekly_data['Quarter'] == 3).astype(int)
weekly_data['Is_Q4'] = (weekly_data['Quarter'] == 4).astype(int)

# Summer/Winter indicators
weekly_data['Is_Summer'] = weekly_data['Month'].isin([6,7,8]).astype(int)
weekly_data['Is_Winter'] = weekly_data['Month'].isin([12,1,2]).astype(int)

print(f"✓ Engineered features added: Lags, moving averages, seasonal indicators")

# ============================================================================
# SERVICE TYPE ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: SERVICE TYPE BREAKDOWN")
print("=" * 80)

# Aggregate by service type
service_type_weekly = df.groupby(['Week_Date', 'Service_Type']).agg({
    'Passenger_Departures': 'sum'
}).reset_index()

service_pivot = service_type_weekly.pivot(index='Week_Date', columns='Service_Type', values='Passenger_Departures').fillna(0)
service_pivot.columns = [f'Passengers_{col}' for col in service_pivot.columns]
service_pivot = service_pivot.reset_index()

# Merge with weekly data
weekly_data = weekly_data.merge(service_pivot, on='Week_Date', how='left')

print(f"✓ Service type breakdown added:")
for col in service_pivot.columns:
    if col != 'Week_Date':
        print(f"  - {col}")

# ============================================================================
# CARRIER ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: MAJOR CARRIER ANALYSIS")
print("=" * 80)

# Top carriers by volume
top_carriers = df.groupby('Carrier_Name')['Passenger_Departures'].sum().nlargest(5).index.tolist()

for carrier in top_carriers:
    carrier_weekly = df[df['Carrier_Name'] == carrier].groupby('Week_Date')['Passenger_Departures'].sum()
    carrier_col = f'Passengers_{carrier.replace(" ", "_").replace("/", "_")}'
    weekly_data = weekly_data.merge(
        carrier_weekly.rename(carrier_col).reset_index(),
        on='Week_Date',
        how='left'
    )
    weekly_data[carrier_col] = weekly_data[carrier_col].fillna(0)

print(f"✓ Top 5 carrier volumes added:")
for carrier in top_carriers:
    print(f"  - {carrier}")

# ============================================================================
# CORRELATION ANALYSIS - ALL FACTORS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: COMPREHENSIVE CORRELATION ANALYSIS")
print("=" * 80)

# Drop rows with NaN (from lagged features)
analysis_data = weekly_data.dropna()

# Define all potential predictors
predictor_columns = [
    # Service Factors
    'Bus_Departures', 'Passengers_Per_Bus',
    
    # Time/Recovery Factors
    'Days_Since_Pandemic_Start', 'Recovery_Rate',
    'Passenger_Recovery_Percent', 'Bus_Recovery_Percent',
    
    # Lagged/Trend Factors
    'Passengers_Lag1', 'Passengers_Lag4',
    'Passengers_MA4', 'Passengers_MA12',
    'Passenger_WoW_Change',
    
    # Calendar/Seasonal Factors
    'Month', 'Quarter', 'Week_of_Year',
    'Is_Q1', 'Is_Q2', 'Is_Q3', 'Is_Q4',
    'Is_Summer', 'Is_Winter',
    'Is_Holiday', 'Is_Holiday_Season', 'Is_Tourism_Peak',
    
    # Weather Factors
    'Avg_Temp_F', 'Precipitation_Inches', 'Snow_Inches',
    'Is_Severe_Weather', 'Is_Snow_Week', 'Is_Hot_Week', 'Is_Cold_Week',
    
    # Economic Factors
    'Is_High_Inflation',
    
    # COVID Factors
    'Is_COVID_Period'
]

# Add service type columns
service_cols = [col for col in analysis_data.columns if col.startswith('Passengers_') and col != 'Passenger_Departures']
predictor_columns.extend(service_cols)

# Calculate correlations
correlations = []
for col in predictor_columns:
    if col in analysis_data.columns:
        try:
            # Skip if constant values
            if analysis_data[col].std() == 0:
                continue
            corr, p_value = pearsonr(analysis_data[col], analysis_data['Passenger_Departures'])
            correlations.append({
                'Factor': col,
                'Correlation': corr,
                'P_Value': p_value,
                'Abs_Correlation': abs(corr),
                'Significant': p_value < 0.05
            })
        except:
            continue

corr_df = pd.DataFrame(correlations)
corr_df = corr_df.sort_values('Abs_Correlation', ascending=False)

# ============================================================================
# CATEGORIZE FACTORS
# ============================================================================

def categorize_factor(factor_name):
    if factor_name in ['Bus_Departures', 'Passengers_Per_Bus']:
        return 'Service Capacity'
    elif factor_name in ['Days_Since_Pandemic_Start', 'Recovery_Rate', 'Passenger_Recovery_Percent', 
                         'Bus_Recovery_Percent', 'Is_COVID_Period']:
        return 'Recovery/Trend'
    elif factor_name in ['Passengers_Lag1', 'Passengers_Lag4', 'Passengers_MA4', 'Passengers_MA12', 
                         'Passenger_WoW_Change', 'Passenger_YoY_Growth']:
        return 'Historical/Lagged'
    elif factor_name in ['Month', 'Quarter', 'Week_of_Year', 'Is_Q1', 'Is_Q2', 'Is_Q3', 'Is_Q4',
                         'Is_Summer', 'Is_Winter', 'Is_Holiday', 'Is_Holiday_Season', 'Is_Tourism_Peak']:
        return 'Calendar/Seasonal'
    elif factor_name in ['Avg_Temp_F', 'Precipitation_Inches', 'Snow_Inches', 'Is_Severe_Weather',
                         'Is_Snow_Week', 'Is_Hot_Week', 'Is_Cold_Week']:
        return 'Weather'
    elif factor_name in ['Is_High_Inflation']:
        return 'Economic'
    elif 'Passengers_Commuter' in factor_name or 'Passengers_Intercity' in factor_name or 'Passengers_Regional' in factor_name:
        return 'Service Type'
    elif 'Passengers_' in factor_name:
        return 'Carrier-Specific'
    else:
        return 'Other'

corr_df['Category'] = corr_df['Factor'].apply(categorize_factor)

# ============================================================================
# DISPLAY RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("TOP 20 MOST IMPORTANT FACTORS (All Categories)")
print("=" * 80)

top_20 = corr_df.head(20)

print(f"\n{'Rank':<5} {'Factor':<35} {'Category':<20} {'Correlation':>12} {'P-Value':>10} {'Sig':>5}")
print("-" * 95)

for idx, (i, row) in enumerate(top_20.iterrows(), 1):
    sig = "***" if row['P_Value'] < 0.001 else "**" if row['P_Value'] < 0.01 else "*" if row['P_Value'] < 0.05 else ""
    print(f"{idx:<5} {row['Factor']:<35} {row['Category']:<20} {row['Correlation']:>12.4f} {row['P_Value']:>10.4f} {sig:>5}")

# ============================================================================
# CATEGORY SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("FACTOR IMPORTANCE BY CATEGORY")
print("=" * 80)

categories = corr_df.groupby('Category').agg({
    'Abs_Correlation': ['mean', 'max', 'count']
}).round(4)

categories.columns = ['Avg_Correlation', 'Max_Correlation', 'Count']
categories = categories.sort_values('Max_Correlation', ascending=False)

print(f"\n{'Category':<25} {'Max Corr':>12} {'Avg Corr':>12} {'# Factors':>12}")
print("-" * 65)
for cat, row in categories.iterrows():
    print(f"{cat:<25} {row['Max_Correlation']:>12.4f} {row['Avg_Correlation']:>12.4f} {int(row['Count']):>12}")

# ============================================================================
# TOP FACTOR IN EACH CATEGORY
# ============================================================================

print("\n" + "=" * 80)
print("MOST IMPORTANT FACTOR IN EACH CATEGORY")
print("=" * 80)

for category in corr_df['Category'].unique():
    cat_data = corr_df[corr_df['Category'] == category].head(1)
    if len(cat_data) > 0:
        row = cat_data.iloc[0]
        sig = "***" if row['P_Value'] < 0.001 else "**" if row['P_Value'] < 0.01 else "*" if row['P_Value'] < 0.05 else ""
        print(f"\n{category}:")
        print(f"  Factor: {row['Factor']}")
        print(f"  Correlation: {row['Correlation']:.4f} {sig}")
        print(f"  P-value: {row['P_Value']:.4f}")

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save full correlation analysis
corr_df.to_csv('Comprehensive_Factor_Importance.csv', index=False)
print("✓ Saved: Comprehensive_Factor_Importance.csv")

# Save category summary
categories.to_csv('Factor_Category_Summary.csv')
print("✓ Saved: Factor_Category_Summary.csv")

# Save top factors only
top_20.to_csv('Top_20_Predictive_Factors.csv', index=False)
print("✓ Saved: Top_20_Predictive_Factors.csv")

# ============================================================================
# EXECUTIVE SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("EXECUTIVE SUMMARY: ANSWER TO PORT AUTHORITY'S QUESTION")
print("=" * 80)

print("\nQUESTION: What are the most important factors in predicting")
print("          the number of passengers for the bus terminal?")
print("\nANSWER:")
print("\nThe Top 5 Most Important Predictive Factors are:")

for idx, (i, row) in enumerate(corr_df.head(5).iterrows(), 1):
    print(f"\n{idx}. {row['Factor']} (Category: {row['Category']})")
    print(f"   - Correlation with passenger volume: {row['Correlation']:.4f}")
    print(f"   - Statistical significance: p < 0.001" if row['P_Value'] < 0.001 else f"   - Statistical significance: p = {row['P_Value']:.4f}")
    
    # Interpretation
    if row['Correlation'] > 0:
        print(f"   - Interpretation: Higher {row['Factor']} → Higher passenger volume")
    else:
        print(f"   - Interpretation: Higher {row['Factor']} → Lower passenger volume")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
