USE PortAuthority_DW;
GO

-- ============================================================
-- DROP EXISTING FOREIGN KEY CONSTRAINTS (if they exist)
-- ============================================================
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Fact_Date')
    ALTER TABLE dbo.Fact_Passenger_Departures DROP CONSTRAINT FK_Fact_Date;

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Fact_Carrier')
    ALTER TABLE dbo.Fact_Passenger_Departures DROP CONSTRAINT FK_Fact_Carrier;

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Fact_Weather')
    ALTER TABLE dbo.Fact_Passenger_Departures DROP CONSTRAINT FK_Fact_Weather;

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Fact_COVID')
    ALTER TABLE dbo.Fact_Passenger_Departures DROP CONSTRAINT FK_Fact_COVID;

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Fact_Event')
    ALTER TABLE dbo.Fact_Passenger_Departures DROP CONSTRAINT FK_Fact_Event;

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Fact_ServiceType')
    ALTER TABLE dbo.Fact_Passenger_Departures DROP CONSTRAINT FK_Fact_ServiceType;

PRINT '✓ Old constraints dropped (if they existed)';
GO

-- ============================================================
-- CREATE NEW FOREIGN KEY CONSTRAINTS
-- ============================================================
ALTER TABLE dbo.Fact_Passenger_Departures
ADD CONSTRAINT FK_Fact_Date 
    FOREIGN KEY (Date_Key) REFERENCES dim.Dim_Date(Date_Key);

ALTER TABLE dbo.Fact_Passenger_Departures
ADD CONSTRAINT FK_Fact_Carrier 
    FOREIGN KEY (Carrier_Key) REFERENCES dim.Dim_Carrier(Carrier_Key);

ALTER TABLE dbo.Fact_Passenger_Departures
ADD CONSTRAINT FK_Fact_Weather 
    FOREIGN KEY (Weather_Key) REFERENCES dim.Dim_Weather(Weather_Key);

ALTER TABLE dbo.Fact_Passenger_Departures
ADD CONSTRAINT FK_Fact_COVID 
    FOREIGN KEY (COVID_Key) REFERENCES dim.Dim_COVID_Status(COVID_Key);

ALTER TABLE dbo.Fact_Passenger_Departures
ADD CONSTRAINT FK_Fact_Event 
    FOREIGN KEY (Event_Key) REFERENCES dim.Dim_Event(Event_Key);

ALTER TABLE dbo.Fact_Passenger_Departures
ADD CONSTRAINT FK_Fact_ServiceType 
    FOREIGN KEY (Service_Type_Key) REFERENCES dim.Dim_Service_Type(Service_Type_Key);

PRINT '✓ Foreign Key constraints added successfully!';
GO
