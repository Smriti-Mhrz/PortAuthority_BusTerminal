/*============================================================
  ETL SCRIPT 4: DATA VALIDATION & QUALITY CHECKS
  Purpose: Validate ETL results and data quality
  Author: Smriti Maharjan
  Date: 2025-12-10
  Database: PortAuthority_DW
============================================================*/

USE PortAuthority_DW;
GO

PRINT '========================================';
PRINT 'ETL STEP 4: VALIDATION & QUALITY CHECKS';
PRINT 'Started: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '========================================';
GO

-- ============================================================
-- CHECK 1: ROW COUNT SUMMARY
-- ============================================================
PRINT '';
PRINT '--- Row Count Summary ---';

SELECT 
    'dbo.FinalDataset' AS Table_Name, 
    COUNT(*) AS Row_Count,
    'Source' AS Table_Type
FROM dbo.FinalDataset

UNION ALL

SELECT 'dim.Dim_Date', COUNT(*), 'Dimension'
FROM dim.Dim_Date

UNION ALL

SELECT 'dim.Dim_Carrier', COUNT(*), 'Dimension'
FROM dim.Dim_Carrier

UNION ALL

SELECT 'dim.Dim_Weather', COUNT(*), 'Dimension'
FROM dim.Dim_Weather

UNION ALL

SELECT 'dim.Dim_COVID_Status', COUNT(*), 'Dimension'
FROM dim.Dim_COVID_Status

UNION ALL

SELECT 'dim.Dim_Event', COUNT(*), 'Dimension'
FROM dim.Dim_Event

UNION ALL

SELECT 'dim.Dim_Service_Type', COUNT(*), 'Dimension'
FROM dim.Dim_Service_Type

UNION ALL

SELECT 'dbo.Fact_Passenger_Departures', COUNT(*), 'Fact'
FROM dbo.Fact_Passenger_Departures

ORDER BY Table_Type, Table_Name;
GO

-- ============================================================
-- CHECK 2: DATA INTEGRITY
-- ============================================================
PRINT '';
PRINT '--- Data Integrity Checks ---';

-- Check for NULL foreign keys
SELECT 
    'NULL Foreign Keys' AS Check_Type,
    COUNT(*) AS Issue_Count,
    CASE WHEN COUNT(*) = 0 THEN '✓ PASS' ELSE '✗ FAIL' END AS Status
FROM dbo.Fact_Passenger_Departures
WHERE Date_Key IS NULL OR Carrier_Key IS NULL

UNION ALL

-- Check for negative passenger counts
SELECT 
    'Negative Passenger Counts',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN '✓ PASS' ELSE '⚠ WARNING' END
FROM dbo.Fact_Passenger_Departures
WHERE Passenger_Departures < 0

UNION ALL

-- Check for negative bus counts
SELECT 
    'Negative Bus Counts',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN '✓ PASS' ELSE '⚠ WARNING' END
FROM dbo.Fact_Passenger_Departures
WHERE Bus_Departures < 0;
GO

-- ============================================================
-- CHECK 3: DATE RANGE VALIDATION
-- ============================================================
PRINT '';
PRINT '--- Date Range Validation ---';

SELECT 
    'Date Range' AS Check_Type,
    MIN(d.Week_Date) AS Earliest_Date,
    MAX(d.Week_Date) AS Latest_Date,
    DATEDIFF(DAY, MIN(d.Week_Date), MAX(d.Week_Date)) AS Days_Covered
FROM dbo.Fact_Passenger_Departures f
INNER JOIN dim.Dim_Date d ON f.Date_Key = d.Date_Key;
GO

-- ============================================================
-- CHECK 4: SAMPLE DATA PREVIEW
-- ============================================================
PRINT '';
PRINT '--- Sample Data Preview (Latest 5 Records) ---';

SELECT TOP 5
    d.Week_Date,
    d.Year,
    c.Carrier_Name,
    f.Bus_Departures,
    f.Passenger_Departures,
    f.Passengers_Per_Bus,
    CAST(f.Passenger_Recovery_Percent AS DECIMAL(5,1)) AS Recovery_Pct
FROM dbo.Fact_Passenger_Departures f
INNER JOIN dim.Dim_Date d ON f.Date_Key = d.Date_Key
INNER JOIN dim.Dim_Carrier c ON f.Carrier_Key = c.Carrier_Key
ORDER BY d.Week_Date DESC;
GO

-- ============================================================
-- CHECK 5: SUMMARY STATISTICS
-- ============================================================
PRINT '';
PRINT '--- Summary Statistics ---';

SELECT 
    'Passenger Departures' AS Metric,
    SUM(Passenger_Departures) AS Total,
    AVG(Passenger_Departures) AS Average,
    MIN(Passenger_Departures) AS Minimum,
    MAX(Passenger_Departures) AS Maximum
FROM dbo.Fact_Passenger_Departures

UNION ALL

SELECT 
    'Bus Departures',
    SUM(Bus_Departures),
    AVG(Bus_Departures),
    MIN(Bus_Departures),
    MAX(Bus_Departures)
FROM dbo.Fact_Passenger_Departures;
GO

PRINT '';
PRINT '========================================';
PRINT 'ETL STEP 4: VALIDATION COMPLETE';
PRINT 'Completed: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '========================================';
GO
