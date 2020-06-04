CREATE TABLE address_data (
ID int NOT NULL AUTO_INCREMENT, 
Country_Code CHAR(2),
Physical_Address VARCHAR(200),
Country_Name VARCHAR(50),
Email_Address VARCHAR(50),
PRIMARY KEY(ID));

CREATE TABLE rates_data (
ID int NOT NULL AUTO_INCREMENT, 
Rate_Reference CHAR(11),
Operator CHAR(3),
Despatch_Year SMALLINT,
Sub_Account_Type VARCHAR(50),
PL CHAR(1),
Country_Code CHAR(2),
Mail_Category CHAR(1),
Subclass CHAR(2),
Rate_Ltr_Kg DECIMAL(8,4),
Rate_Ltr_Itm DECIMAL(8,4),
Rate_Bulk_Kg DECIMAL(8,4),
Rate_Bulk_Itm DECIMAL(8,4),
PRIMARY KEY(ID));

CREATE TABLE sales_data (
ID int NOT NULL AUTO_INCREMENT, 
Sub_Account_Type VARCHAR(50),
Despatch_Year SMALLINT,
Despatch_Month TINYINT,
Despatch_Date DATE,
Qtr TINYINT,
Despatch_ID VARCHAR(30),
Serial_Number INT,
Origin CHAR(6),
Destination CHAR(6),
Mail_Category CHAR(1),
Class CHAR(1),
Subclass CHAR(2),
PL CHAR(2),
Operator CHAR(3),
Country_Code CHAR(2),
No_of_ItRates INT,
Weight_Kgs DECIMAL(10,4),
PRIMARY KEY(ID));