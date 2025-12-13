/*============================================================
  ETL SCRIPT 1: SETUP STAGING ENVIRONMENT
  Purpose: Prepare staging table for data import
  Author: [Your Name]
  Date: 2025-12-10
  Database: PortAuthority_DW
============================================================*/

USE PortAuthority_DW;
GO

PRINT '========================================';
PRINT 'ETL STEP 1: STAGING SETUP';
PRINT 'Started: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '========================================';
GO

-- Drop existing staging table if exists
IF OBJECT_ID('dbo.FinalDataset_Staging', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.FinalDataset_Staging;
    PRINT '✓ Old staging table dropped';
END
GO

-- Create fresh staging table
CREATE TABLE dbo.FinalDataset_Staging (
    -- Date attributes
    Week_Date DATE,
    Year INT,
    Quarter INT,
    Month INT,
    Month_Name VARCHAR(20),
    Week_of_Year INT,
    Season VARCHAR(20),
    
    -- Carrier attributes
    Carrier_Name VARCHAR(100),
    Carrier_Full_Name VARCHAR(200),
    Service_Type VARCHAR(50),
    
    -- Facts/Metrics
    Bus_Departures INT,
    Passenger_Departures INT,
    Passengers_Per_Bus DECIMAL(10,2),
    
    -- Baseline metrics
    Baseline_2019_Buses INT,
    Baseline_2019_Passengers INT,
    Bus_Recovery_Percent DECIMAL(10,2),
    Passenger_Recovery_Percent DECIMAL(10,2),
    
    -- Trend metrics
    Bus_WoW_Change DECIMAL(10,2),
    Passenger_WoW_Change DECIMAL(10,2),
    Bus_4wk_MA DECIMAL(10,2),
    Passenger_4wk_MA DECIMAL(10,2),
    Bus_12wk_MA DECIMAL(10,2),
    Passenger_12wk_MA DECIMAL(10,2),
    
    -- Weather attributes
    Avg_Temp_F DECIMAL(5,2),
    Precipitation_Inches DECIMAL(5,2),
    Snow_Inches DECIMAL(5,2),
    Weather_Condition VARCHAR(50),
    Is_Severe_Weather VARCHAR(10),
    
    -- COVID attributes
    COVID_Period VARCHAR(50),
    Economic_Period VARCHAR(50),
    Is_COVID_Period VARCHAR(10),
    Is_High_Inflation VARCHAR(10),
    Days_Since_Pandemic_Start INT,
    
    -- Event attributes
    Is_Holiday VARCHAR(10),
    Is_Tourism_Peak VARCHAR(10),
    NYC_Event VARCHAR(200),
    
    -- ETL metadata
    ETL_Load_Date DATETIME DEFAULT GETDATE()
);
GO

PRINT '✓ Staging table created: dbo.FinalDataset_Staging';
GO

-- Copy data from existing FinalDataset to staging
INSERT INTO dbo.FinalDataset_Staging
SELECT 
    Week_Date, Year, Quarter, Month, Month_Name, Week_of_Year, Season,
    Carrier_Name, Carrier_Full_Name, Service_Type,
    Bus_Departures, Passenger_Departures, Passengers_Per_Bus,
    Baseline_2019_Buses, Baseline_2019_Passengers,
    Bus_Recovery_Percent, Passenger_Recovery_Percent,
    Bus_WoW_Change, Passenger_WoW_Change,
    Bus_4wk_MA, Passenger_4wk_MA, Bus_12wk_MA, Passenger_12wk_MA,
    Avg_Temp_F, Precipitation_Inches, Snow_Inches, Weather_Condition, Is_Severe_Weather,
    COVID_Period, Economic_Period, Is_COVID_Period, Is_High_Inflation, Days_Since_Pandemic_Start,
    Is_Holiday, Is_Tourism_Peak, NYC_Event,
    GETDATE() AS ETL_Load_Date
FROM dbo.FinalDataset;

PRINT '✓ Data copied to staging: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- Data quality checks on staging
PRINT '--- Staging Data Quality Checks ---';

DECLARE @NullDates INT, @NullCarriers INT, @TotalRows INT;

SELECT @TotalRows = COUNT(*) FROM dbo.FinalDataset_Staging;
SELECT @NullDates = COUNT(*) FROM dbo.FinalDataset_Staging WHERE Week_Date IS NULL;
SELECT @NullCarriers = COUNT(*) FROM dbo.FinalDataset_Staging WHERE Carrier_Name IS NULL;

PRINT 'Total rows: ' + CAST(@TotalRows AS VARCHAR(10));
PRINT 'NULL dates: ' + CAST(@NullDates AS VARCHAR(10));
PRINT 'NULL carriers: ' + CAST(@NullCarriers AS VARCHAR(10));

IF @NullDates > 0 OR @NullCarriers > 0
BEGIN
    PRINT '⚠ WARNING: Data quality issues detected!';
END
ELSE
BEGIN
    PRINT '✓ Staging data quality checks passed';
END

PRINT '========================================';
PRINT 'ETL STEP 1: COMPLETE';
PRINT 'Completed: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '========================================';
GO
