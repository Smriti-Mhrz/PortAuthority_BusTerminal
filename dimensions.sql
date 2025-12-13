-- Dim_Carrier: Carrier dimension

CREATE TABLE dim.Dim_Carrier (
    Carrier_Key INT IDENTITY(1,1) PRIMARY KEY,
    Carrier_Name VARCHAR(50) NOT NULL UNIQUE,
    Carrier_Full_Name VARCHAR(100),
    Service_Type VARCHAR(50)
);
GO

CREATE INDEX IX_Carrier_ServiceType ON dim.Dim_Carrier(Service_Type);

-- Dim_Weather: Weather dimension
CREATE TABLE dim.Dim_Weather (
    Weather_Key INT IDENTITY(1,1) PRIMARY KEY,
    Avg_Temp_F DECIMAL(5,2),
    Precipitation_Inches DECIMAL(5,2),
    Snow_Inches DECIMAL(5,2),
    Weather_Condition VARCHAR(50),
    Is_Severe_Weather BIT DEFAULT 0
);

-- Dim_COVID_Status: COVID context dimension
CREATE TABLE dim.Dim_COVID_Status (
    COVID_Key INT IDENTITY(1,1) PRIMARY KEY,
    COVID_Period VARCHAR(50),
    Economic_Period VARCHAR(50),
    Is_COVID_Period BIT,
    Is_High_Inflation BIT,
    Days_Since_Pandemic_Start INT
);

CREATE TABLE dim.Dim_Event (
    Event_Key INT IDENTITY(1,1) PRIMARY KEY,
    Is_Holiday BIT,
    NYC_Event VARCHAR(100),
    Is_Tourism_Peak BIT
);


CREATE TABLE dim.Dim_Service_Type (
    Service_Type_Key INT IDENTITY(1,1) PRIMARY KEY,
    Service_Type VARCHAR(50) NOT NULL UNIQUE,
    Service_Description VARCHAR(200),
    Typical_Distance_Range VARCHAR(50),
    Primary_Customer_Base VARCHAR(100)
);
