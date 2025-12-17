"""
Port Authority Bus Terminal Data Consolidation
Purpose: Extract and merge 150+ Excel worksheets into single dataset
Author: Data Analytics Team
Date: December 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==================================================
# STEP 1: LOAD EXCEL FILE
# ==================================================

print("=" * 60)
print("PORT AUTHORITY DATA CONSOLIDATION SCRIPT")
print("=" * 60)

# File path
excel_file = 'Project-1_Bus-Terminal-Passenger-Prediction-Data-Fall-2025.xlsx'

print(f"\n📂 Loading file: {excel_file}")

# Get all sheet names
xl_file = pd.ExcelFile(excel_file)
all_sheets = xl_file.sheet_names

print(f"✅ Found {len(all_sheets)} worksheets")
print(f"   First few sheets: {all_sheets[:5]}")

# ==================================================
# STEP 2: READ AND CONSOLIDATE ALL SHEETS
# ==================================================

print("\n🔄 Processing sheets...")

# Initialize empty list to store dataframes
all_data = []

# Counter for progress
sheet_count = 0
skipped_sheets = []

for sheet_name in all_sheets:
    try:
        # Read each sheet
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Skip if sheet is empty
        if df.empty:
            skipped_sheets.append(sheet_name)
            continue
        
        # Add source sheet name for tracking
        df['Source_Sheet'] = sheet_name
        
        # Append to list
        all_data.append(df)
        
        sheet_count += 1
        
        # Progress indicator
        if sheet_count % 20 == 0:
            print(f"   Processed {sheet_count} sheets...")
        
    except Exception as e:
        print(f"   ⚠️ Error reading sheet '{sheet_name}': {str(e)}")
        skipped_sheets.append(sheet_name)
        continue

print(f"\n✅ Successfully processed {sheet_count} sheets")
if skipped_sheets:
    print(f"⚠️  Skipped {len(skipped_sheets)} sheets (empty or errors)")

# ==================================================
# STEP 3: CONCATENATE ALL DATA
# ==================================================

print("\n🔗 Merging all sheets...")

# Combine all dataframes
merged_df = pd.concat(all_data, ignore_index=True)

print(f"✅ Merged dataset shape: {merged_df.shape[0]} rows × {merged_df.shape[1]} columns")

# ==================================================
# STEP 4: DATA CLEANING & TRANSFORMATION
# ==================================================

print("\n🧹 Cleaning and transforming data...")

# Standardize column names
merged_df.columns = merged_df.columns.str.strip().str.replace(' ', '_')

# Display current columns
print(f"\n📋 Columns found: {list(merged_df.columns)}")

# Convert date columns (adjust column names as needed)
date_columns = ['Week_Date', 'Date', 'Week_Ending']  # Try common date column names

for col in merged_df.columns:
    if any(date_term in col for date_term in date_columns):
        try:
            merged_df[col] = pd.to_datetime(merged_df[col], errors='coerce')
            print(f"   ✅ Converted '{col}' to datetime")
        except:
            pass

# Handle missing values
print(f"\n📊 Missing values before cleaning:")
print(merged_df.isnull().sum())

# Drop rows where ALL values are missing
merged_df = merged_df.dropna(how='all')

# Drop duplicate rows
initial_rows = len(merged_df)
merged_df = merged_df.drop_duplicates()
duplicates_removed = initial_rows - len(merged_df)

if duplicates_removed > 0:
    print(f"\n🗑️  Removed {duplicates_removed} duplicate rows")

# ==================================================
# STEP 5: ADD CALCULATED FIELDS
# ==================================================

print("\n➕ Adding calculated fields...")

# If you have passenger and bus columns, calculate efficiency
if 'Passenger_Departures' in merged_df.columns and 'Bus_Departures' in merged_df.columns:
    merged_df['Passengers_Per_Bus'] = (
        merged_df['Passenger_Departures'] / merged_df['Bus_Departures']
    ).round(2)
    print("   ✅ Added 'Passengers_Per_Bus' calculation")

# Extract date components if date column exists
if 'Week_Date' in merged_df.columns:
    merged_df['Year'] = merged_df['Week_Date'].dt.year
    merged_df['Month'] = merged_df['Week_Date'].dt.month
    merged_df['Quarter'] = merged_df['Week_Date'].dt.quarter
    merged_df['Week_of_Year'] = merged_df['Week_Date'].dt.isocalendar().week
    print("   ✅ Added Year, Month, Quarter, Week_of_Year")

# ==================================================
# STEP 6: SORT AND REORDER COLUMNS
# ==================================================

print("\n📑 Organizing columns...")

# Preferred column order (adjust based on your actual columns)
preferred_order = [
    'Week_Date',
    'Year', 
    'Month',
    'Quarter',
    'Week_of_Year',
    'Carrier',
    'Passenger_Departures',
    'Bus_Departures',
    'Passengers_Per_Bus',
    'Season',
    'COVID_Period',
    'Is_Severe_Weather',
    'Source_Sheet'
]

# Reorder columns (only include columns that exist)
available_columns = [col for col in preferred_order if col in merged_df.columns]
other_columns = [col for col in merged_df.columns if col not in available_columns]
final_column_order = available_columns + other_columns

merged_df = merged_df[final_column_order]

# Sort by date if available
if 'Week_Date' in merged_df.columns:
    merged_df = merged_df.sort_values('Week_Date').reset_index(drop=True)
    print("   ✅ Sorted by Week_Date")

# ==================================================
# STEP 7: DATA QUALITY CHECKS
# ==================================================

print("\n🔍 Data Quality Summary:")
print("=" * 60)
print(f"Total Records:        {len(merged_df):,}")
print(f"Date Range:           ", end="")

if 'Week_Date' in merged_df.columns:
    min_date = merged_df['Week_Date'].min()
    max_date = merged_df['Week_Date'].max()
    print(f"{min_date.date()} to {max_date.date()}")
else:
    print("No date column found")

if 'Carrier' in merged_df.columns:
    print(f"Unique Carriers:      {merged_df['Carrier'].nunique()}")
    
if 'Passenger_Departures' in merged_df.columns:
    print(f"Total Passengers:     {merged_df['Passenger_Departures'].sum():,}")
    print(f"Average per Week:     {merged_df['Passenger_Departures'].mean():,.0f}")

# ==================================================
# STEP 8: EXPORT TO CSV
# ==================================================

output_file = 'FinalDataset.csv'

print(f"\n💾 Exporting to {output_file}...")

merged_df.to_csv(output_file, index=False)

print(f"✅ SUCCESS! File saved as '{output_file}'")
print(f"   Final dataset: {merged_df.shape[0]} rows × {merged_df.shape[1]} columns")

# ==================================================
# STEP 9: DISPLAY PREVIEW
# ==================================================

print("\n👀 Preview of Final Dataset (first 10 rows):")
print("=" * 60)
print(merged_df.head(10).to_string())

print("\n" + "=" * 60)
print("DATA CONSOLIDATION COMPLETE ✅")
print("=" * 60)

# ==================================================
# OPTIONAL: GENERATE DATA SUMMARY REPORT
# ==================================================

print("\n📊 Generating Summary Statistics...")

summary_file = 'Data_Summary_Report.txt'

with open(summary_file, 'w') as f:
    f.write("PORT AUTHORITY BUS TERMINAL DATA SUMMARY\n")
    f.write("=" * 60 + "\n\n")
    
    f.write(f"Data Source: {excel_file}\n")
    f.write(f"Consolidation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Total Sheets Processed: {sheet_count}\n\n")
    
    f.write("DATASET OVERVIEW:\n")
    f.write(f"Total Records: {len(merged_df):,}\n")
    f.write(f"Total Columns: {len(merged_df.columns)}\n\n")
    
    f.write("COLUMN NAMES:\n")
    for i, col in enumerate(merged_df.columns, 1):
        f.write(f"{i}. {col}\n")
    
    f.write("\n" + "=" * 60 + "\n")
    f.write("DESCRIPTIVE STATISTICS:\n")
    f.write("=" * 60 + "\n")
    f.write(merged_df.describe().to_string())

print(f"✅ Summary report saved as '{summary_file}'")

print("\n✨ All tasks completed successfully! ✨\n")
