USE PortAuthority_DW;
GO

-- Check if Performance_Rank column already exists
IF EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID('dbo.tbl_Carrier_Performance') 
    AND name = 'Performance_Rank'
)
BEGIN
    -- If it exists, drop and recreate the table
    DROP TABLE dbo.tbl_Carrier_Performance;
    
    CREATE TABLE dbo.tbl_Carrier_Performance (
        Carrier_Name VARCHAR(255) NOT NULL,
        Total_Passengers INT,
        Total_Buses INT,
        Avg_Passengers_Per_Bus DECIMAL(10,2),
        Performance_Rank INT,  -- Added directly in table creation
        CONSTRAINT PK_Carrier PRIMARY KEY (Carrier_Name)
    );
    
    PRINT 'Table recreated with Performance_Rank column';
END
ELSE
BEGIN
    -- If it doesn't exist, just add it
    ALTER TABLE dbo.tbl_Carrier_Performance
    ADD Performance_Rank INT;
    
    PRINT 'Performance_Rank column added';
END

-- Re-run SSIS to reload data, then run this to calculate rankings:
-- (Don't run this part yet - wait for instructions)


USE PortAuthority_DW;
GO

-- Check all tables
SELECT 'tbl_Monthly_Carrier_Summary' AS Table_Name, COUNT(*) AS Rows 
FROM dbo.tbl_Monthly_Carrier_Summary
UNION ALL
SELECT 'tbl_Quarterly_Summary', COUNT(*) 
FROM dbo.tbl_Quarterly_Summary
UNION ALL
SELECT 'tbl_COVID_Impact_Summary', COUNT(*) 
FROM dbo.tbl_COVID_Impact_Summary
UNION ALL
SELECT 'tbl_Carrier_Performance', COUNT(*) 
FROM dbo.tbl_Carrier_Performance;

-- Sample data from each table
SELECT TOP 5 * FROM dbo.tbl_Monthly_Carrier_Summary ORDER BY Year, Month;
SELECT TOP 5 * FROM dbo.tbl_Quarterly_Summary ORDER BY Year, Quarter;
SELECT * FROM dbo.tbl_COVID_Impact_Summary ORDER BY COVID_Period;
SELECT * FROM dbo.tbl_Carrier_Performance ORDER BY Performance_Rank;




USE PortAuthority_DW;
GO

-- Verify all 4 aggregate tables with data
SELECT 'tbl_Monthly_Carrier_Summary' AS Table_Name, COUNT(*) AS Rows 
FROM dbo.tbl_Monthly_Carrier_Summary
UNION ALL
SELECT 'tbl_Quarterly_Summary', COUNT(*) 
FROM dbo.tbl_Quarterly_Summary
UNION ALL
SELECT 'tbl_COVID_Impact_Summary', COUNT(*) 
FROM dbo.tbl_COVID_Impact_Summary
UNION ALL
SELECT 'tbl_Carrier_Performance', COUNT(*) 
FROM dbo.tbl_Carrier_Performance;

-- View top performers
SELECT TOP 5 
    Performance_Rank,
    Carrier_Name,
    Total_Passengers,
    Avg_Passengers_Per_Bus
FROM dbo.tbl_Carrier_Performance 
ORDER BY Performance_Rank;


USE PortAuthority_DW;
GO

-- Update Performance_Rank with calculated rankings
WITH RankedCarriers AS (
    SELECT 
        Carrier_Name,
        ROW_NUMBER() OVER (ORDER BY Avg_Passengers_Per_Bus DESC) AS Rank
    FROM dbo.tbl_Carrier_Performance
)
UPDATE c
SET c.Performance_Rank = r.Rank
FROM dbo.tbl_Carrier_Performance c
INNER JOIN RankedCarriers r ON c.Carrier_Name = r.Carrier_Name;

-- Verify - should now show ranks 1, 2, 3, 4, 5...
SELECT 
    Performance_Rank,
    Carrier_Name,
    Total_Passengers,
    Avg_Passengers_Per_Bus
FROM dbo.tbl_Carrier_Performance 
ORDER BY Performance_Rank;
