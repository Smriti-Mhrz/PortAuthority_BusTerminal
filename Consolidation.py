import pandas as pd
import numpy as np
from datetime import datetime
import os
import re

# =========================================================
# CONFIG
# =========================================================
EXCEL_FILE = "Project 1_Bus Terminal Passenger Prediction Data Fall 2025.xlsx"
OUTPUT_FOLDER = "project1_Bus_Terminal"
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "final_dataset.csv")

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# All weekly sheets to extract (2020-2025)
WEEKLY_SHEETS_2020 = ["Dec 7-11", "Dec. 14-18", "Dec. 21-25", "Dec. 28-Jan 1"]

WEEKLY_SHEETS_2021 = [
    "Jan 4-8", "Jan. 11-15", "Jan. 18-22", "Jan. 25-29",
    "Feb. 1-5", "Feb. 8-12", "Feb 15-19", "Feb 22-26",
    "March 1-5", "March 8-12", "March 15-19", "March 22-26", "March 29-April 2",
    "April 5-9", "April 12-16", "April 19-23", "April 26-30",
    "May 3-7", "May 10-14", "May 17-21", "May 24-28",  "May 31-June 4",
    "June 7-11", "June 14-18", "June 21-25", "June 28-July 2",
    "July 5-9", "July 12-16", "July 19-23", "July 26-30",
    "Aug 2-6", "Aug 9-13", "Aug 16-20", "Aug 23-27", "Aug 30-Sept 3",
    "Sept 7-10", "Sept 13-17", "Sept 20-24", "Sept 27-Oct 1",
    "Oct 4-8", "Oct 11-15", "Oct 18-22", "Oct 25-29",
    "Nov 1-5", "Nov 8-12", "Nov 15-19", "Nov 22-26",
    "Nov 29-Dec 3", "Dec 6-10", "Dec 13-17", "Dec 20-24", "Dec 27-31",
]

WEEKLY_SHEETS_2023 = [
    "Mar 27-31", "April 10-14", "April 24-28", "May 8-12", "May 22-26",
    "June 5-9", "June 19-23", "July 3-7", "July 17-21", "July 31 - Aug 4",
    "August 14-18", "Aug 28 - Sept 1", "Sept 11-15", "Sept 25-29",
    "Oct 9-13", "Oct 23-27", "Nov 6-10", "Nov 13-17", "Dec 4-8", "Dec. 18-22",
]

WEEKLY_SHEETS_2024 = [
    "Jan 2-5", "Jan 15-19", "Jan 29 - Feb 2", "Feb 12-16", "Feb 26 - March 1",
    "March 11-15", "March 25-29", "April 8-12", "April 22-26",
    "May 6-10", "May 20-24", "June 3-7", "June 17-21",
    "July 1-5", "July 15-19", "July 29 - Aug 2",
    "Aug 12-16", "Aug 26-30", "Sept 9-13", "Sept 23-27",
    "Oct 7-11", "Oct 21-25", "Nov 4-8", "Nov 18-22", "Dec 2-6", "Dec 16-20",
]

WEEKLY_SHEETS_2025 = [
    "Jan 6-10, 2025", "Jan 20-24, 2025", "Feb 3-7, 2025", "Feb 17-21, 2025",
    "March 3-7, 2025", "March 17-21, 2025", "March 31-April 4, 2025",
    "April 14-18, 2025", "April 28-May 2, 2025", "May 12-16, 2025",
    "May 26-30, 2025", "June 9-13, 2025", "June 23-27, 2025",
    "July 7-11, 2025", "July 21-25, 2025",
]

CARRIER_NAMES = [
    "Academy", "Greyhound", "Martz", "NJ Transit", "Lakeland", "Trailways",
    "Coach USA", "TransBridge", "Peter Pan/Bonanza", "C & J Bus Lines",
    "HCEE - Community", "Total"
]

CARRIER_FULL_NAMES = {
    "Academy": "Academy Bus",
    "Greyhound": "Greyhound Lines",
    "Martz": "Martz Trailways",
    "NJ Transit": "NJ Transit",
    "Lakeland": "Lakeland Bus",
    "Trailways": "Trailways",
    "Coach USA": "Coach USA Inc",
    "TransBridge": "TransBridge Lines",
    "Peter Pan/Bonanza": "Peter Pan/Bonanza",
    "C & J Bus Lines": "C&J Bus Lines (Ceased)",
    "HCEE - Community": "HCEE Community Coach",
    "Total": "All Carriers Total",
}

SERVICE_TYPES = {
    "NJ Transit": "Regional",
    "Greyhound": "Intercity",
    "Peter Pan/Bonanza": "Intercity",
    "Trailways": "Intercity",
    "Coach USA": "Commuter",
    "Martz": "Regional",
    "Academy": "Regional",
    "TransBridge": "Regional",
    "Lakeland": "Commuter",
    "C & J Bus Lines": "Intercity",
    "HCEE - Community": "Commuter",
    "Total": "Aggregate",
}

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def parse_week_ending_date(sheet_name: str, year: int) -> datetime:
    """Parse week ending date from sheet name"""
    s = sheet_name.strip().replace("Jan.", "Jan").replace("Feb.", "Feb")
    s = s.replace("Mar.", "Mar").replace("Apr.", "Apr").replace("Sept.", "Sept")
    s = s.replace("Oct.", "Oct").replace("Nov.", "Nov").replace("Dec.", "Dec")
    
    months = {
        "Jan": 1, "January": 1, "Feb": 2, "February": 2, "Mar": 3, "March": 3,
        "Apr": 4, "April": 4, "May": 5, "Jun": 6, "June": 6,
        "Jul": 7, "July": 7, "Aug": 8, "August": 8,
        "Sep": 9, "Sept": 9, "September": 9,
        "Oct": 10, "October": 10, "Nov": 11, "November": 11,
        "Dec": 12, "December": 12,
    }
    
    try:
        if "-" in s:
            parts = s.split("-")
            ending_part = parts[-1].strip()
            first_part = parts[0].strip()
            
            # Check if month in ending part
            month_in_ending = any(m in ending_part for m in months)
            
            if month_in_ending:
                m = re.search(r"([A-Za-z]+)\s+(\d+)", ending_part)
                if m:
                    month_str = m.group(1)
                    day_num = int(m.group(2))
                    month_num = months.get(month_str, 1)
                else:
                    return datetime(year, 1, 1)
            else:
                m = re.search(r"([A-Za-z]+)\s+(\d+)", first_part)
                if m:
                    month_str = m.group(1)
                    month_num = months.get(month_str, 1)
                    day_num = int(ending_part.split(',')[0].strip())
                else:
                    return datetime(year, 1, 1)
            
            return datetime(year, month_num, day_num)
    except:
        pass
    return datetime(year, 1, 1)


def get_season(month: int) -> str:
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"


def extract_sheet_data(sheet_name: str, year: int) -> pd.DataFrame:
    """Extract data from one weekly sheet"""
    try:
        df_raw = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=None)
        
        # Find header row
        start_row = None
        for idx in range(min(40, len(df_raw))):
            row_str = " ".join(str(x) for x in df_raw.iloc[idx].dropna())
            if any(c in row_str for c in CARRIER_NAMES):
                start_row = idx
                break
        
        if start_row is None:
            return pd.DataFrame()
        
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=start_row)
        
        # Find carrier column
        carrier_col = None
        for col in df.columns[:10]:
            col_vals = df[col].astype(str)
            if any(k in v for v in col_vals for k in ["NJ Transit", "Martz", "Total", "Academy"]):
                carrier_col = col
                break
        
        if carrier_col is None:
            return pd.DataFrame()
        
        df_f = df[df[carrier_col].isin(CARRIER_NAMES)].copy()
        if df_f.empty:
            return pd.DataFrame()
        
        df_f = df_f.rename(columns={carrier_col: "Carrier_Name"})
        
        # Find bus and passenger columns
        bus_col = None
        pax_col = None
        for col in df_f.columns:
            cs = str(col).lower()
            if bus_col is None and "bus" in cs:
                bus_col = col
            if pax_col is None and "passenger" in cs:
                pax_col = col
        
        if bus_col is None or pax_col is None:
            return pd.DataFrame()
        
        week_end = parse_week_ending_date(sheet_name, year)
        
        # Build enriched dataset with all 34 columns
        df_f["Carrier_Full_Name"] = df_f["Carrier_Name"].map(CARRIER_FULL_NAMES)
        df_f["Service_Type"] = df_f["Carrier_Name"].map(SERVICE_TYPES)
        df_f["Week_Label"] = sheet_name
        df_f["Week_Date"] = week_end.strftime("%m/%d/%Y")
        df_f["Year"] = year
        df_f["Month"] = week_end.month
        df_f["Month_Name"] = week_end.strftime("%B")
        df_f["Week_of_Year"] = week_end.isocalendar()[1]
        df_f["Quarter"] = (week_end.month - 1) // 3 + 1
        df_f["Season"] = get_season(week_end.month)
        df_f["Fiscal_Year"] = year if week_end.month >= 7 else year - 1
        df_f["Day_of_Week"] = week_end.strftime("%A")
        
        df_f["Bus_Departures"] = pd.to_numeric(df_f[bus_col], errors="coerce")
        df_f["Passenger_Departures"] = pd.to_numeric(df_f[pax_col], errors="coerce")
        df_f["Passengers_Per_Bus"] = np.where(
            df_f["Bus_Departures"] > 0,
            df_f["Passenger_Departures"] / df_f["Bus_Departures"],
            np.nan
        )
        
        df_f["Baseline_2019_Buses"] = np.nan
        df_f["Baseline_2019_Passengers"] = np.nan
        df_f["Bus_Recovery_Percent"] = np.nan
        df_f["Passenger_Recovery_Percent"] = np.nan
        
        # Weather placeholders (would need actual weather API data)
        df_f["Avg_Temp_F"] = 50.0
        df_f["Precipitation_Inches"] = 0.1
        df_f["Snow_Inches"] = 0.0
        df_f["Weather_Condition"] = "Normal"
        df_f["Major_Weather_Event"] = np.nan
        
        # Status and flags
        if year == 2020:
            df_f["Status"] = "Lockdown"
        elif year in [2021, 2022, 2023]:
            df_f["Status"] = "Recovery"
        else:
            df_f["Status"] = "Normal"
        
        df_f["Is_Holiday"] = False
        df_f["Is_Summer_Peak"] = (week_end.month in [7, 8])
        df_f["Is_Holiday_Season"] = (week_end.month == 12)
        df_f["Is_Severe_Weather"] = False
        df_f["Is_Snow_Week"] = (week_end.month in [12, 1, 2, 3])
        df_f["Is_Hot_Week"] = (week_end.month in [7, 8])
        df_f["Is_Cold_Week"] = (week_end.month in [12, 1, 2])
        
        df_f["Notes"] = np.nan
        
        return df_f[[
            "Carrier_Name", "Carrier_Full_Name", "Service_Type", "Week_Label", "Week_Date",
            "Year", "Month", "Month_Name", "Week_of_Year", "Quarter", "Season",
            "Fiscal_Year", "Day_of_Week",
            "Bus_Departures", "Passenger_Departures", "Passengers_Per_Bus",
            "Baseline_2019_Buses", "Baseline_2019_Passengers",
            "Bus_Recovery_Percent", "Passenger_Recovery_Percent",
            "Avg_Temp_F", "Precipitation_Inches", "Snow_Inches", "Weather_Condition",
            "Major_Weather_Event", "Status", "Is_Holiday", "Is_Summer_Peak",
            "Is_Holiday_Season", "Is_Severe_Weather", "Is_Snow_Week",
            "Is_Hot_Week", "Is_Cold_Week", "Notes"
        ]]
    
    except Exception as e:
        print(f"   ERROR {sheet_name}: {e}")
        return pd.DataFrame()


# =========================================================
# MAIN EXTRACTION
# =========================================================
print("=" * 60)
print("EXTRACTING BUS TERMINAL DATA FROM COMPANY EXCEL")
print("=" * 60)

all_dfs = []

# Extract 2020
print("\n2020...")
for sheet in WEEKLY_SHEETS_2020:
    df_s = extract_sheet_data(sheet, 2020)
    if not df_s.empty:
        all_dfs.append(df_s)
        print(f"  ✓ {sheet}: {len(df_s)} rows")

# Extract 2021
print("\n2021...")
for sheet in WEEKLY_SHEETS_2021:
    df_s = extract_sheet_data(sheet, 2021)
    if not df_s.empty:
        all_dfs.append(df_s)
        print(f"  ✓ {sheet}: {len(df_s)} rows")

# Extract 2023
print("\n2023...")
for sheet in WEEKLY_SHEETS_2023:
    df_s = extract_sheet_data(sheet, 2023)
    if not df_s.empty:
        all_dfs.append(df_s)
        print(f"  ✓ {sheet}: {len(df_s)} rows")

# Extract 2024
print("\n2024...")
for sheet in WEEKLY_SHEETS_2024:
    df_s = extract_sheet_data(sheet, 2024)
    if not df_s.empty:
        all_dfs.append(df_s)
        print(f"  ✓ {sheet}: {len(df_s)} rows")

# Extract 2025
print("\n2025...")
for sheet in WEEKLY_SHEETS_2025:
    df_s = extract_sheet_data(sheet, 2025)
    if not df_s.empty:
        all_dfs.append(df_s)
        print(f"  ✓ {sheet}: {len(df_s)} rows")

# Combine all
if all_dfs:
    df_final = pd.concat(all_dfs, ignore_index=True)
    df_final = df_final.sort_values(["Week_Date", "Carrier_Name"]).reset_index(drop=True)
    
    # Save
    df_final.to_csv(OUTPUT_FILE, index=False)
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Total rows: {len(df_final):,}")
    print(f"Total columns: {len(df_final.columns)}")
    print(f"Date range: {df_final['Week_Date'].min()} to {df_final['Week_Date'].max()}")
    print(f"Saved to: {OUTPUT_FILE}")
else:
    print("\nERROR: No data extracted!")
