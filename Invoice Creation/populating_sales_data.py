import mysql.connector
import csv

file = 'MyFile.csv'

cnx = mysql.connector.connect(user='user', password='password',
                              host='host',
                              database='billings')

mycursor = cnx.cursor()

SQL = "INSERT INTO sales_data (Sub_Account_Type, Despatch_Year, Despatch_Month, Despatch_Date, " \
      "Qtr, Despatch_ID, Serial_Number, Origin, Destination, Mail_Category, Class, Subclass, " \
      "PL, Country_Office, Country_Code, No_of_ItRates, Weight_Kgs) " \
      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

with open(file) as my_file:
    reader = csv.reader(my_file)

    for row in reader:

        for i in [1, 2, 4, 6, 15]:
            row[i] = int(row[i])

        row[-1] = float(row[-1])

        mycursor.execute(SQL, tuple(row))

cnx.commit()

cnx.close()