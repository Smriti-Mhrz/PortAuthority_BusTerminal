USE PortAuthority_DW;
GO

-- Indexes on Dimension Tables
CREATE INDEX IX_Dim_Date_Year ON dim.Dim_Date(Year);
CREATE INDEX IX_Dim_Date_Quarter ON dim.Dim_Date(Quarter);
CREATE INDEX IX_Dim_Date_Season ON dim.Dim_Date(Season);
CREATE INDEX IX_Dim_Carrier_Name ON dim.Dim_Carrier(Carrier_Name);
CREATE INDEX IX_Dim_Weather_Condition ON dim.Dim_Weather(Weather_Condition);
CREATE INDEX IX_Dim_COVID_Period ON dim.Dim_COVID_Status(COVID_Period);

-- Indexes on Fact Table (Foreign Keys)
CREATE INDEX IX_Fact_Date_Key ON dbo.Fact_Passenger_Departures(Date_Key);
CREATE INDEX IX_Fact_Carrier_Key ON dbo.Fact_Passenger_Departures(Carrier_Key);
CREATE INDEX IX_Fact_Weather_Key ON dbo.Fact_Passenger_Departures(Weather_Key);
CREATE INDEX IX_Fact_COVID_Key ON dbo.Fact_Passenger_Departures(COVID_Key);

-- Composite Index for common queries (Date + Carrier)
CREATE INDEX IX_Fact_Date_Carrier ON dbo.Fact_Passenger_Departures(Date_Key, Carrier_Key);

PRINT '✓ Indexes created successfully!';
GO
