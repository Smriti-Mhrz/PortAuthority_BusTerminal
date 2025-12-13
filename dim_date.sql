USE PortAuthority_DW;
GO

-- Create schemas
CREATE SCHEMA dim;
GO

CREATE SCHEMA stg;
GO

PRINT '✓ Schemas created successfully!';
GO




CREATE TABLE dim.Dim_Date (
    Date_Key INT PRIMARY KEY,
    Week_Date DATE NOT NULL UNIQUE,
    Year INT NOT NULL,
    Quarter INT NOT NULL,
    Month INT NOT NULL,
    Month_Name VARCHAR(20),
    Week_of_Year INT,
    Season VARCHAR(20),
    Is_Holiday BIT DEFAULT 0,
    Is_Tourism_Peak BIT DEFAULT 0
);

CREATE INDEX IX_Date_Year ON dim.Dim_Date(Year);
CREATE INDEX IX_Date_Quarter ON dim.Dim_Date(Quarter);
CREATE INDEX IX_Date_Season ON dim.Dim_Date(Season);