-- Check if primary keys are defined
USE PortAuthority_DW;
GO

SELECT 
    t.name AS Table_Name,
    i.name AS Index_Name,
    COL_NAME(ic.object_id, ic.column_id) AS Column_Name
FROM sys.indexes i
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN sys.tables t ON i.object_id = t.object_id
WHERE i.is_primary_key = 1
  AND t.name IN ('Dim_Date', 'Dim_Carrier', 'Dim_Weather', 'Dim_COVID_Status', 'Dim_Event', 'Dim_Service_Type')
ORDER BY t.name;


USE PortAuthority_DW;
GO

-- Check foreign key relationships
SELECT 
    fk.name AS Foreign_Key_Name,
    OBJECT_NAME(fk.parent_object_id) AS Fact_Table,
    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS FK_Column,
    OBJECT_SCHEMA_NAME(fk.referenced_object_id) + '.' + OBJECT_NAME(fk.referenced_object_id) AS Referenced_Dimension,
    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS PK_Column
FROM sys.foreign_keys fk
INNER JOIN sys.foreign_key_columns fkc 
    ON fk.object_id = fkc.constraint_object_id
WHERE OBJECT_NAME(fk.parent_object_id) = 'Fact_Passenger_Departures'
ORDER BY fk.name;
GO