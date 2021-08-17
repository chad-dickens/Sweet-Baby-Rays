DROP TABLE IF EXISTS address_data;
DROP TABLE IF EXISTS rates_data;
DROP TABLE IF EXISTS sales_data;

CREATE TABLE address_data (
	Country_Code CHAR(2) PRIMARY KEY,
    Physical_Address VARCHAR(200),
    Country_Name VARCHAR(50),
    Email_Address VARCHAR(50)
);

CREATE TABLE rates_data (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Rate_Reference CHAR(11),
    Operator CHAR(3),
    Despatch_Year SMALLINT,
    Sub_Account_Type VARCHAR(50),
    PL CHAR(1),
    Country_Code CHAR(2),
    Mail_Category CHAR(1),
    Subclass CHAR(2),
    Rate_Ltr_Kg DECIMAL(8 , 4 ),
    Rate_Ltr_Itm DECIMAL(8 , 4 ),
    Rate_Bulk_Kg DECIMAL(8 , 4 ),
    Rate_Bulk_Itm DECIMAL(8 , 4 ),
    CONSTRAINT fk_rates_country FOREIGN KEY (Country_Code)
        REFERENCES address_data (Country_Code)
        ON DELETE RESTRICT
);

CREATE TABLE sales_data (
    ID INT AUTO_INCREMENT PRIMARY KEY,
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
    Weight_Kgs DECIMAL(10 , 4 ),
    CONSTRAINT fk_sales_country FOREIGN KEY (Country_Code)
        REFERENCES address_data (Country_Code)
        ON DELETE RESTRICT
);