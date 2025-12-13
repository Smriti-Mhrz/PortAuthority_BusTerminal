# Port Authority Bus Terminal Passenger Analytics

## Project Overview
End-to-end business intelligence solution analyzing passenger traffic patterns at Port Authority Bus Terminal (2020-2025), including COVID-19 impact analysis, carrier performance metrics, and forecasting through 2030.

## Technologies Used
- **ETL:** SQL Server Integration Services (SSIS)
- **Database:** Microsoft SQL Server
- **Data Warehousing:** Star Schema Design
- **Forecasting:** R / Python (time series analysis)
- **BI Tools:** Power BI (dashboard development)

## Project Components

### 1. Data Warehouse Architecture
- **Database:** PortAuthority_DW
- **Schema:** Star Schema
- **Tables:** 4 Dimensions + 1 Fact + 4 Analytical Aggregates

### 2. ETL Pipeline
- **Package 1:** 01_LoadDataWarehouse.dtsx (loads star schema)
- **Package 2:** 02_Load_Analytical_Aggregates.dtsx (creates summary tables)

### 3. Data Coverage
- **Time Period:** January 2020 - November 2025
- **Records:** 1,000+ weekly observations
- **Carriers:** 12 bus carriers tracked
- **Metrics:** Passenger departures, bus departures, efficiency ratios

## Key Features
✅ COVID-19 impact segmentation (Pre/During/Post/Recovery)
✅ Seasonal pattern analysis
✅ Carrier performance rankings
✅ Monthly and quarterly trend analysis
✅ 2026-2030 passenger forecasting

## Database Schema

### Dimension Tables
- `dim.Dim_Date` - Date/time attributes
- `dim.Dim_Carrier` - Bus carrier information
- `dim.Dim_Weather` - Weather categorization
- `dim.Dim_COVID_Status` - COVID period classification
- `dim.Dim_Event' - Events in Newyork
- `dim.Dim_Service_Type' - 

### Fact Table
- `dbo.Fact_Passenger_Departures` - Core metrics (grain: weekly/carrier)

### Aggregate Tables
- `tbl_Monthly_Carrier_Summary` - Monthly trends by carrier
- `tbl_Quarterly_Summary` - Quarterly aggregates
- `tbl_COVID_Impact_Summary` - COVID period comparison
- `tbl_Carrier_Performance` - Carrier efficiency rankings

## Installation & Setup

### Prerequisites
- SQL Server 2019 or later
- Visual Studio with SSIS extensions
- SQL Server Management Studio (SSMS)

### Database Setup
1. Run `SQL_Scripts/01_Create_Database.sql`
2. Run `SQL_Scripts/02_Create_Schema.sql`
3. Run `SQL_Scripts/03_Create_Dimension_Tables.sql`
4. Run `SQL_Scripts/04_Create_Fact_Table.sql`
5. Run `SQL_Scripts/05_Create_Aggregate_Tables.sql`

### ETL Execution
1. Open `ETL_SSIS/PortAuthority_ETL.sln` in Visual Studio
2. Configure connection manager to your SQL Server instance
3. Run `01_LoadDataWarehouse.dtsx`
4. Run `02_Load_Analytical_Aggregates.dtsx`

## Project Insights

### COVID-19 Impact
- 68% passenger decline during lockdown period
- Full recovery to pre-COVID levels by Q4 2023
- Greyhound and Coach USA showed fastest recovery rates

### Carrier Performance
- **Top Performer:** Coach USA (28.57 passengers/bus)
- **Most Passengers:** HCEE - Community (981K total)
- **Growth Leader:** DeCamp (+15% YoY 2024-2025)

### Forecast (2026-2030)
- Projected 8% CAGR through 2030
- Expected peak: Summer 2029 (45K passengers/week)
- Busiest months: July, August, December

## Author
[Your Name]  
[Your Email]  
[LinkedIn Profile]

## License
This project is for academic/portfolio purposes.
