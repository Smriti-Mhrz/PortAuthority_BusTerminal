USE PortAuthority_DW;
GO

-- Table 1: Monthly Carrier Summary
CREATE TABLE dbo.tbl_Monthly_Carrier_Summary (
    Year INT NOT NULL,
    Month INT NOT NULL,
    Carrier_Name NVARCHAR(255) NOT NULL,
    Total_Passengers INT,
    Total_Buses INT,
    Avg_Passengers_Per_Bus DECIMAL(10,2),
    CONSTRAINT PK_Monthly_Carrier PRIMARY KEY (Year, Month, Carrier_Name)
);

-- Table 2: Quarterly Summary
CREATE TABLE dbo.tbl_Quarterly_Summary (
    Year INT NOT NULL,
    Quarter INT NOT NULL,
    Total_Passengers INT,
    Total_Buses INT,
    Avg_Passengers_Per_Bus DECIMAL(10,2),
    Unique_Carriers INT,
    CONSTRAINT PK_Quarterly PRIMARY KEY (Year, Quarter)
);

-- Table 3: COVID Impact Summary
CREATE TABLE dbo.tbl_COVID_Impact_Summary (
    COVID_Period NVARCHAR(50) NOT NULL,
    Total_Passengers INT,
    Avg_Weekly_Passengers INT,
    Total_Weeks INT,
    CONSTRAINT PK_COVID PRIMARY KEY (COVID_Period)
);

-- Table 4: Carrier Performance Rankings
CREATE TABLE dbo.tbl_Carrier_Performance (
    Carrier_Name NVARCHAR(255) NOT NULL,
    Total_Passengers INT,
    Total_Buses INT,
    Avg_Passengers_Per_Bus DECIMAL(10,2),
    Performance_Rank INT,
    CONSTRAINT PK_Carrier PRIMARY KEY (Carrier_Name)
);

-- Verify tables created
SELECT 'Table Created' AS Status, name AS Table_Name
FROM sys.tables
WHERE name LIKE 'tbl_%Carrier%' OR name LIKE 'tbl_%Quarterly%' 
   OR name LIKE 'tbl_%COVID%'
ORDER BY name;

USE PortAuthority_DW;
GO

-- Drop and recreate with VARCHAR (matches SSIS output)
DROP TABLE IF EXISTS dbo.tbl_Monthly_Carrier_Summary;

CREATE TABLE dbo.tbl_Monthly_Carrier_Summary (
    Year INT NOT NULL,
    Month INT NOT NULL,
    Carrier_Name VARCHAR(255) NOT NULL,  -- Changed from NVARCHAR to VARCHAR
    Total_Passengers INT,
    Total_Buses INT,
    Avg_Passengers_Per_Bus DECIMAL(10,2),
    CONSTRAINT PK_Monthly_Carrier PRIMARY KEY (Year, Month, Carrier_Name)
);



-- Fix table 2
DROP TABLE IF EXISTS dbo.tbl_Quarterly_Summary;
CREATE TABLE dbo.tbl_Quarterly_Summary (
    Year INT NOT NULL,
    Quarter INT NOT NULL,
    Total_Passengers INT,
    Total_Buses INT,
    Avg_Passengers_Per_Bus DECIMAL(10,2),
    Unique_Carriers INT,
    CONSTRAINT PK_Quarterly PRIMARY KEY (Year, Quarter)
);

-- Fix table 3
DROP TABLE IF EXISTS dbo.tbl_COVID_Impact_Summary;
CREATE TABLE dbo.tbl_COVID_Impact_Summary (
    COVID_Period VARCHAR(50) NOT NULL,  -- Changed from NVARCHAR
    Total_Passengers INT,
    Avg_Weekly_Passengers INT,
    Total_Weeks INT,
    CONSTRAINT PK_COVID PRIMARY KEY (COVID_Period)
);

-- Fix table 4
DROP TABLE IF EXISTS dbo.tbl_Carrier_Performance;
CREATE TABLE dbo.tbl_Carrier_Performance (
    Carrier_Name VARCHAR(255) NOT NULL,  -- Changed from NVARCHAR
    Total_Passengers INT,
    Total_Buses INT,
    Avg_Passengers_Per_Bus DECIMAL(10,2),
    Performance_Rank INT,
    CONSTRAINT PK_Carrier PRIMARY KEY (Carrier_Name)
);


USE PortAuthority_DW;
GO

-- Drop and recreate WITHOUT Performance_Rank
DROP TABLE IF EXISTS dbo.tbl_Carrier_Performance;

CREATE TABLE dbo.tbl_Carrier_Performance (
    Carrier_Name VARCHAR(255) NOT NULL,
    Total_Passengers INT,
    Total_Buses INT,
    Avg_Passengers_Per_Bus DECIMAL(10,2),
    -- Performance_Rank removed (we'll add it later)
    CONSTRAINT PK_Carrier PRIMARY KEY (Carrier_Name)
);