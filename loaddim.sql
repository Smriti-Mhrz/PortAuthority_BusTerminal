USE PortAuthority_DW;
GO

-- ============================================================
-- 1. LOAD DIM_DATE
-- ============================================================
INSERT INTO dim.Dim_Date (
    Date_Key, Week_Date, Year, Quarter, Month, Month_Name,
    Week_of_Year, Season, Is_Holiday, Is_Tourism_Peak
)
SELECT DISTINCT
    CAST(
        CAST(Year AS VARCHAR(4)) + 
        RIGHT('0' + CAST(Month AS VARCHAR(2)), 2) + 
        RIGHT('0' + CAST(DAY(CAST(Week_Date AS DATE)) AS VARCHAR(2)), 2)
    AS INT) AS Date_Key,
    CAST(Week_Date AS DATE) AS Week_Date,
    Year,
    Quarter,
    Month,
    Month_Name,
    Week_of_Year,
    Season,
    CASE WHEN Is_Holiday = 'True' THEN 1 ELSE 0 END AS Is_Holiday,
    CASE WHEN Is_Tourism_Peak = 'True' THEN 1 ELSE 0 END AS Is_Tourism_Peak
FROM dbo.FinalDataset
WHERE Week_Date IS NOT NULL AND Year IS NOT NULL;

PRINT '✓ Dim_Date loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- 2. LOAD DIM_CARRIER
-- ============================================================
INSERT INTO dim.Dim_Carrier (Carrier_Name, Carrier_Full_Name)
SELECT DISTINCT
    Carrier_Name,
    Carrier_Full_Name
FROM dbo.FinalDataset
WHERE Carrier_Name IS NOT NULL;

PRINT '✓ Dim_Carrier loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- 3. LOAD DIM_WEATHER
-- ============================================================
INSERT INTO dim.Dim_Weather (
    Avg_Temp_F, Precipitation_Inches, Snow_Inches, 
    Weather_Condition, Is_Severe_Weather
)
SELECT DISTINCT
    Avg_Temp_F,
    Precipitation_Inches,
    Snow_Inches,
    Weather_Condition,
    CASE WHEN Is_Severe_Weather = 'True' THEN 1 ELSE 0 END
FROM dbo.FinalDataset
WHERE Avg_Temp_F IS NOT NULL;

PRINT '✓ Dim_Weather loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- 4. LOAD DIM_COVID_STATUS
-- ============================================================
INSERT INTO dim.Dim_COVID_Status (
    COVID_Period, Economic_Period, Is_COVID_Period, 
    Is_High_Inflation, Days_Since_Pandemic_Start
)
SELECT DISTINCT
    COVID_Period,
    Economic_Period,
    CASE WHEN Is_COVID_Period = 'True' THEN 1 ELSE 0 END,
    CASE WHEN Is_High_Inflation = 'True' THEN 1 ELSE 0 END,
    Days_Since_Pandemic_Start
FROM dbo.FinalDataset
WHERE COVID_Period IS NOT NULL;

PRINT '✓ Dim_COVID_Status loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- 5. LOAD DIM_EVENT (CORRECTED - Removed Is_Holiday_Season)
-- ============================================================
INSERT INTO dim.Dim_Event (
    Is_Holiday, NYC_Event, Is_Tourism_Peak
)
SELECT DISTINCT
    CASE WHEN Is_Holiday = 'True' THEN 1 ELSE 0 END,
    ISNULL(NYC_Event, 'None'),  -- Handle NULL values
    CASE WHEN Is_Tourism_Peak = 'True' THEN 1 ELSE 0 END
FROM dbo.FinalDataset;

PRINT '✓ Dim_Event loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

-- ============================================================
-- 6. LOAD DIM_SERVICE_TYPE
-- ============================================================
-- First, check what service types exist in your data
SELECT DISTINCT Service_Type 
FROM dbo.FinalDataset 
WHERE Service_Type IS NOT NULL;
GO

-- Then insert them dynamically
INSERT INTO dim.Dim_Service_Type (Service_Type, Service_Description)
SELECT DISTINCT 
    Service_Type,
    Service_Type + ' service'
FROM dbo.FinalDataset
WHERE Service_Type IS NOT NULL;

PRINT '✓ Dim_Service_Type loaded: ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' rows';
GO

PRINT '========================================';
PRINT '✓✓ ALL 6 DIMENSIONS LOADED! ✓✓';
PRINT '========================================';
GO


SELECT TOP 5 * FROM dim.Dim_Date ORDER BY Week_Date DESC;
SELECT TOP 5 * FROM dim.Dim_Carrier;
SELECT TOP 5 * FROM dim.Dim_Weather;
SELECT TOP 5 * FROM dim.Dim_COVID_Status;
SELECT TOP 5 * FROM dim.Dim_Event;
SELECT TOP 5 * FROM dim.Dim_Service_Type;


SELECT 'dim.Dim_Date' AS TableName, COUNT(*) AS RowCount FROM dim.Dim_Date
UNION ALL
SELECT 'dim.Dim_Carrier', COUNT(*) FROM dim.Dim_Carrier
UNION ALL
SELECT 'dim.Dim_Weather', COUNT(*) FROM dim.Dim_Weather
UNION ALL
SELECT 'dim.Dim_COVID_Status', COUNT(*) FROM dim.Dim_COVID_Status
UNION ALL
SELECT 'dim.Dim_Event', COUNT(*) FROM dim.Dim_Event
UNION ALL
SELECT 'dim.Dim_Service_Type', COUNT(*) FROM dim.Dim_Service_Type
UNION ALL
SELECT 'dbo.FinalDataset (Source)', COUNT(*) FROM dbo.FinalDataset
ORDER BY TableName;