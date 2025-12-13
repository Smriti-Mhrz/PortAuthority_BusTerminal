/*============================================================
  ETL SCRIPT 2: LOAD DIMENSION TABLES
  Purpose: Extract and load dimension tables from staging
  Author: [Your Name]
  Date: 2025-12-10
  Database: PortAuthority_DW
============================================================*/

USE PortAuthority_DW;
GO

PRINT '========================================';
PRINT 'ETL STEP 2: LOADING DIMENSIONS';
PRINT 'Started: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '========================================';
GO

-- Clear existing dimension data
BEGIN TRY
    TRUNCATE TABLE dim.Dim_Date;
    TRUNCATE TABLE dim.Dim_Carrier;
    TRUNCATE TABLE dim.Dim_Weather;
    TRUNCATE TABLE dim.Dim_COVID_Status;
    TRUNCATE TABLE dim.Dim_Event;
    TRUNCATE TABLE dim.Dim_Service_Type;
    PRINT '✓ Dimension tables cleared';
END TRY
BEGIN CATCH
    PRINT '⚠ Error clearing dimensions: ' + ERROR_MESSAGE();
    THROW;
END CATCH
GO

-- ============================================================
-- DIMENSION 1: DIM_DATE
-- ============================================================
PRINT '--- Loading dim.Dim_Date ---';

INSERT INTO dim.Dim_Date (
    Date_Key, Week_Date, Year, Quarter, Month, Month_Name,
    Week_of_Year, Season, Is_Holiday, Is_Tourism_Peak
)
SELECT DISTINCT
    CAST(FORMAT(CAST(Week_Date AS DATE), 'yyyyMMdd') AS INT) AS Date_Key,
    CAST(Week_Date AS DATE) AS Week_Date,
    Year,
    Quarter,
    Month,
    Month_Name,
    Week_of_Year,
    Season,
    CASE WHEN Is_Holiday = 'True' THEN 1 ELSE 0 END AS Is_Holiday,
    CASE WHEN Is_Tourism_Peak = 'True' THEN 1 ELSE 0 END AS Is_Tourism_Peak
FROM dbo.FinalDataset_Staging
WHERE Week_Date IS NOT NULL 
  AND Year IS NOT NULL
ORDER BY Week_Date;

PRINT '✓ dim.Dim_Date loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- DIMENSION 2: DIM_CARRIER
-- ============================================================
PRINT '--- Loading dim.Dim_Carrier ---';

INSERT INTO dim.Dim_Carrier (Carrier_Name, Carrier_Full_Name)
SELECT DISTINCT 
    Carrier_Name, 
    Carrier_Full_Name
FROM dbo.FinalDataset_Staging
WHERE Carrier_Name IS NOT NULL
ORDER BY Carrier_Name;

PRINT '✓ dim.Dim_Carrier loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- DIMENSION 3: DIM_WEATHER
-- ============================================================
PRINT '--- Loading dim.Dim_Weather ---';

INSERT INTO dim.Dim_Weather (
    Avg_Temp_F, Precipitation_Inches, Snow_Inches, 
    Weather_Condition, Is_Severe_Weather
)
SELECT DISTINCT
    Avg_Temp_F,
    Precipitation_Inches,
    Snow_Inches,
    Weather_Condition,
    CASE WHEN Is_Severe_Weather = 'True' THEN 1 ELSE 0 END AS Is_Severe_Weather
FROM dbo.FinalDataset_Staging
WHERE Avg_Temp_F IS NOT NULL
ORDER BY Avg_Temp_F;

PRINT '✓ dim.Dim_Weather loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- DIMENSION 4: DIM_COVID_STATUS
-- ============================================================
PRINT '--- Loading dim.Dim_COVID_Status ---';

INSERT INTO dim.Dim_COVID_Status (
    COVID_Period, Economic_Period, Is_COVID_Period, 
    Is_High_Inflation, Days_Since_Pandemic_Start
)
SELECT DISTINCT
    COVID_Period,
    Economic_Period,
    CASE WHEN Is_COVID_Period = 'True' THEN 1 ELSE 0 END AS Is_COVID_Period,
    CASE WHEN Is_High_Inflation = 'True' THEN 1 ELSE 0 END AS Is_High_Inflation,
    Days_Since_Pandemic_Start
FROM dbo.FinalDataset_Staging
WHERE COVID_Period IS NOT NULL
ORDER BY Days_Since_Pandemic_Start;

PRINT '✓ dim.Dim_COVID_Status loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- DIMENSION 5: DIM_EVENT
-- ============================================================
PRINT '--- Loading dim.Dim_Event ---';

INSERT INTO dim.Dim_Event (Is_Holiday, NYC_Event, Is_Tourism_Peak)
SELECT DISTINCT
    CASE WHEN Is_Holiday = 'True' THEN 1 ELSE 0 END AS Is_Holiday,
    ISNULL(NYC_Event, 'None') AS NYC_Event,
    CASE WHEN Is_Tourism_Peak = 'True' THEN 1 ELSE 0 END AS Is_Tourism_Peak
FROM dbo.FinalDataset_Staging;

PRINT '✓ dim.Dim_Event loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- DIMENSION 6: DIM_SERVICE_TYPE
-- ============================================================
PRINT '--- Loading dim.Dim_Service_Type ---';

INSERT INTO dim.Dim_Service_Type (Service_Type, Service_Description)
SELECT DISTINCT 
    Service_Type,
    Service_Type + ' transportation service' AS Service_Description
FROM dbo.FinalDataset_Staging
WHERE Service_Type IS NOT NULL
ORDER BY Service_Type;

PRINT '✓ dim.Dim_Service_Type loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

PRINT '========================================';
PRINT 'ETL STEP 2: COMPLETE';
PRINT 'All 6 dimensions loaded successfully!';
PRINT 'Completed: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '========================================';
GO
