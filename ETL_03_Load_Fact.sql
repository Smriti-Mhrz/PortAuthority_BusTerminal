CREATE TABLE dbo.Fact_Passenger_Departures (
    Fact_Key INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Foreign Keys (6 dimensions)
    Date_Key INT NOT NULL,
    Carrier_Key INT NOT NULL,
    Weather_Key INT NULL,
    COVID_Key INT NULL,
    Event_Key INT NULL,
    Service_Type_Key INT NULL,
    
    -- Core Measures
    Bus_Departures INT,
    Passenger_Departures INT,
    Passengers_Per_Bus DECIMAL(10,2),
    Baseline_2019_Buses INT,
    Baseline_2019_Passengers INT,
    Bus_Recovery_Percent DECIMAL(10,2),
    Passenger_Recovery_Percent DECIMAL(10,2),
    
    -- Trend Indicators
    Bus_WoW_Change DECIMAL(10,2),
    Passenger_WoW_Change DECIMAL(10,2),
    Bus_4wk_MA DECIMAL(10,2),
    Passenger_4wk_MA DECIMAL(10,2),
    Bus_12wk_MA DECIMAL(10,2),
    Passenger_12wk_MA DECIMAL(10,2),
    
    -- ETL Metadata
    ETL_Load_Date DATETIME DEFAULT GETDATE(),
    
    -- Foreign Key Constraints
    CONSTRAINT FK_Fact_Date 
        FOREIGN KEY (Date_Key) REFERENCES dim.Dim_Date(Date_Key),
    CONSTRAINT FK_Fact_Carrier 
        FOREIGN KEY (Carrier_Key) REFERENCES dim.Dim_Carrier(Carrier_Key),
    CONSTRAINT FK_Fact_Weather 
        FOREIGN KEY (Weather_Key) REFERENCES dim.Dim_Weather(Weather_Key),
    CONSTRAINT FK_Fact_COVID 
        FOREIGN KEY (COVID_Key) REFERENCES dim.Dim_COVID_Status(COVID_Key),
    CONSTRAINT FK_Fact_Event 
        FOREIGN KEY (Event_Key) REFERENCES dim.Dim_Event(Event_Key),
    CONSTRAINT FK_Fact_ServiceType 
        FOREIGN KEY (Service_Type_Key) REFERENCES dim.Dim_Service_Type(Service_Type_Key)
);