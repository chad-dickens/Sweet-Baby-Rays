"""
Module creates pdf invoices from MySQL database and emails them to customers
This file contains the two main classes for the process, the Params class and the Customer class.
This file imports pdf objects from another module and uses an imported function for sending emails.
The Main() function at the end runs the actual process.
"""

import shelve
import time
from datetime import datetime
import mysql.connector

# The following three imports are all from other modules I have made
from invoice_pdf_objects import SummaryInvoice, DetailInvoice
from email_module import send_email_365
from assorted_functions import number_name


class Params:
    """
    Initializing this class will load in parameters from a shelve database that are
    important for the whole process to run.
    """

    def __init__(self):
        """
        Loads key parameters into the master class for this process from a shelve database.
        If this shelve database does not specify customers, it will call the private load
        customers method.
        :return: None
        """
        with shelve.open('params') as data_base:
            self.save_location = data_base['save_location']
            self.log_location = data_base['log_location']
            self.customers = data_base['customers']

            self.database_name = data_base['database_name']
            self.user = data_base['user']
            self.password = data_base['password']
            self.host = data_base['host']
            self.manager_email = data_base['manager_email']
            self.date_stamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

            self.param_dict = {'year': data_base['year'],
                               'sub_account': data_base['sub_account'],
                               'qtr': data_base['qtr'],
                               'customer': None}

            self.prep_dict = {'officer': data_base['officer'],
                              'company': data_base['company'],
                              'department': data_base['department'],
                              'email_sender': data_base['email_sender'],
                              'email_password': data_base['email_password']}

        if self.customers is None:
            self._load_customers()

    def _load_customers(self):
        """
        Loads a tuple of unique Country_Codes from the MySQL database that
        meet the criteria of the parameters.
        Will be called during init if necessary.
        Loads the tuple directly into the customers class attribute.
        :return: None
        """
        cnx = mysql.connector.connect(user=self.user, password=self.password,
                                      host=self.host, database=self.database_name)

        my_cursor = cnx.cursor()

        sql = 'SELECT DISTINCT(Country_Code) ' \
              'FROM sales_data ' \
              'WHERE ' \
              'Sub_Account_Type = %(sub_account)s AND ' \
              'Despatch_Year = %(year)s AND ' \
              'Qtr = %(qtr)s ' \
              'ORDER BY Country_Code;'

        my_cursor.execute(sql, self.param_dict)

        self.customers = tuple([x[0] for x in my_cursor.fetchall()])

        cnx.close()


class Customer:
    """
    The main class that this whole process revolves around.
    Contains a large cohort of methods that retrieve all the necessary information for the
    invoices from the MySQL database, create invoice objects, and then email them off.
    """
    def __init__(self, master):
        """
        Loads important information into the class attributes and determines whether or not
        the Country_Code supplied through the master parameter is valid.
        :param master: Should be an instance of the Params class.
        """
        self.master = master
        self.rates_issues = self._get_rates_issues()
        self.details = self._get_details()
        self.valid = self._is_valid()
        # Where the status of the customer is stored, ie whether the process failed or not
        self.status = None
        # Where the total amount the customer is to be billed will be stored
        self.total_due = None

    def _get_rates_issues(self):
        """
        Queries the MySQL database to find if this customer has any missing rates.
        :return: A tuple of the missing rate references, if any.
        """
        cnx = mysql.connector.connect(user=self.master.user, password=self.master.password,
                                      host=self.master.host, database=self.master.database_name)

        my_cursor = cnx.cursor()

        sql = 'SELECT DISTINCT ' \
              'CONVERT(sd.Despatch_Year, CHAR), ' \
              'sd.Operator, ' \
              'sd.PL, ' \
              'sd.Mail_Category, ' \
              'sd.Subclass ' \
              '' \
              'FROM sales_data sd ' \
              '' \
              'LEFT JOIN rates_data rd ' \
              'USING (Despatch_Year, Operator, PL, Mail_Category, Subclass) ' \
              '' \
              'WHERE ' \
              'sd.Sub_Account_Type = %(sub_account)s AND ' \
              'sd.Despatch_Year = %(year)s AND ' \
              'sd.Qtr = %(qtr)s AND ' \
              'sd.Country_Code = %(customer)s AND ' \
              'rd.Rate_Ltr_Kg IS NULL;'

        my_cursor.execute(sql, self.master.param_dict)
        go_fetch = my_cursor.fetchall()
        go_fetch = tuple([''.join(x) for x in go_fetch])
        cnx.close()
        return go_fetch

    def _get_details(self):
        """
        Queries the MySQL database to retrieve customer information.
        :return: A dictionary object containing Country_Name, Physical_Address, Email_Address
        """
        cnx = mysql.connector.connect(user=self.master.user, password=self.master.password,
                                      host=self.master.host, database=self.master.database_name)

        my_cursor = cnx.cursor()

        sql = 'SELECT DISTINCT ' \
              'ad.Country_Name, ' \
              'ad.Physical_Address, ' \
              'ad.Email_Address ' \
              '' \
              'FROM sales_data sd ' \
              'LEFT JOIN address_data ad ' \
              'USING (Country_Code) ' \
              '' \
              'WHERE ' \
              'sd.Sub_Account_Type = %(sub_account)s AND ' \
              'sd.Despatch_Year = %(year)s AND ' \
              'sd.Qtr = %(qtr)s AND ' \
              'sd.Country_Code = %(customer)s;'

        my_cursor.execute(sql, self.master.param_dict)
        go_fetch = my_cursor.fetchall()[0]
        go_fetch = {'Country_Name': go_fetch[0],
                    'Physical_Address': go_fetch[1],
                    'Email_Address': go_fetch[2]}
        cnx.close()
        return go_fetch

    def _is_valid(self):
        """
        Boolean function that will look at whether or not the customer is valid.
        If any of the details values are none or there are any rates issues,
        the customer is invalid. In this case, invoices should not be created.
        :return: Boolean
        """
        if None in self.details.values() or len(self.rates_issues) > 0:
            return False
        return True

    def _retrieve_summary_data(self):
        """
        Will query the MySQL database and retrieve all necessary
        data to construct the summary invoice.
        :return: List containing tuples
        """

        cnx = mysql.connector.connect(user=self.master.user, password=self.master.password,
                                      host=self.master.host, database=self.master.database_name)
        my_cursor = cnx.cursor()

        # The bulk part of the invoice
        sql = 'SELECT ' \
              'sd.Operator, ' \
              'sd.Origin, ' \
              'sd.Destination, ' \
              'sd.Mail_Category, ' \
              'sd.Subclass, ' \
              'FORMAT(SUM(sd.No_of_ItRates), 0), ' \
              'FORMAT(SUM(sd.Weight_Kgs), 2), ' \
              '' \
              'FORMAT(rd.Rate_Ltr_Itm, 4), ' \
              'FORMAT(rd.Rate_Bulk_Itm, 4), ' \
              '' \
              'FORMAT(SUM((rd.Rate_Ltr_Itm + rd.Rate_Bulk_Itm) * sd.No_of_ItRates), 2), ' \
              '' \
              'FORMAT(rd.Rate_Ltr_Kg, 4), ' \
              'FORMAT(rd.Rate_Bulk_Kg, 4), ' \
              '' \
              'FORMAT(SUM((rd.Rate_Ltr_Kg + rd.Rate_Bulk_Kg) * sd.Weight_Kgs), 2), ' \
              '' \
              'FORMAT(SUM((rd.Rate_Ltr_Itm + rd.Rate_Bulk_Itm) * sd.No_of_ItRates + ' \
              '(rd.Rate_Ltr_Kg + rd.Rate_Bulk_Kg) * sd.Weight_Kgs), 2) ' \
              '' \
              'FROM sales_data sd ' \
              '' \
              'LEFT JOIN rates_data rd ' \
              'USING (Despatch_Year, Operator, PL, Mail_Category, Subclass) ' \
              '' \
              'WHERE ' \
              'sd.Sub_Account_Type = %(sub_account)s AND ' \
              'sd.Despatch_Year = %(year)s AND ' \
              'sd.Qtr = %(qtr)s AND ' \
              'sd.Country_Code = %(customer)s ' \
              '' \
              'GROUP BY ' \
              'sd.Operator, ' \
              'sd.Origin, ' \
              'sd.Destination, ' \
              'sd.Mail_Category, ' \
              'sd.Subclass, ' \
              'rd.Rate_Ltr_Itm, ' \
              'rd.Rate_Bulk_Itm, ' \
              'rd.Rate_Ltr_Kg, ' \
              'rd.Rate_Bulk_Kg ' \
              '' \
              'ORDER BY ' \
              'sd.Operator, ' \
              'sd.Origin, ' \
              'sd.Destination, ' \
              'sd.Mail_Category, ' \
              'sd.Subclass;'

        my_cursor.execute(sql, self.master.param_dict)
        summary_body = my_cursor.fetchall()

        # The totals section underneath
        sql = 'SELECT ' \
              'FORMAT(SUM(sd.No_of_ItRates), 0), ' \
              'FORMAT(SUM(sd.Weight_Kgs), 2), ' \
              'FORMAT(SUM((rd.Rate_Ltr_Itm + rd.Rate_Bulk_Itm) * sd.No_of_ItRates), 2), ' \
              'FORMAT(SUM((rd.Rate_Ltr_Kg + rd.Rate_Bulk_Kg) * sd.Weight_Kgs), 2), ' \
              'CONCAT(\'$\', FORMAT(SUM((rd.Rate_Ltr_Itm + rd.Rate_Bulk_Itm) ' \
              '* sd.No_of_ItRates + ' \
              '(rd.Rate_Ltr_Kg + rd.Rate_Bulk_Kg) * sd.Weight_Kgs), 2)) ' \
              '' \
              'FROM sales_data sd ' \
              '' \
              'LEFT JOIN rates_data rd ' \
              'USING (Despatch_Year, Operator, PL, Mail_Category, Subclass) ' \
              '' \
              'WHERE ' \
              'sd.Sub_Account_Type = %(sub_account)s AND ' \
              'sd.Despatch_Year = %(year)s AND ' \
              'sd.Qtr = %(qtr)s AND ' \
              'sd.Country_Code = %(customer)s ' \
              '' \
              'GROUP BY sd.Country_Code;'

        my_cursor.execute(sql, self.master.param_dict)
        summary_totals = my_cursor.fetchall()

        cnx.close()

        summary_body.append(summary_totals[0])

        self.total_due = summary_body[-1][-1]

        return summary_body

    def _retrieve_detail_data(self):
        """
        Will query the MySQL database and retrieve all necessary
        data to construct the detail invoice.
        Is a bit more complicated than the summary data method because the detail invoice
        has so many subtotal rows.
        :return: List containing tuples
        """
        cnx = mysql.connector.connect(user=self.master.user, password=self.master.password,
                                      host=self.master.host, database=self.master.database_name)
        my_cursor = cnx.cursor()

        # Starting off by getting a list of unique rates combinations for this customer
        sql = 'SELECT DISTINCT ' \
              'Origin,' \
              'Destination,' \
              'Mail_Category, ' \
              'Subclass ' \
              '' \
              'FROM sales_data ' \
              '' \
              'WHERE ' \
              'Sub_Account_Type = %(sub_account)s AND ' \
              'Despatch_Year = %(year)s AND ' \
              'Qtr = %(qtr)s AND ' \
              'Country_Code = %(customer)s ' \
              '' \
              'ORDER BY ' \
              'Origin, ' \
              'Destination, ' \
              'Mail_Category, ' \
              'Subclass;'

        my_cursor.execute(sql, self.master.param_dict)
        unique_cb_list = my_cursor.fetchall()

        # Looping through this new unique list and adding our results to the detail_list
        detail_list = []

        for row in unique_cb_list:
            new_param_dict = {'origin': row[0],
                              'destination': row[1],
                              'mail_category': row[2],
                              'subclass': row[3]}
            new_param_dict.update(self.master.param_dict)

            # Getting the bulk part of the detail invoice
            sql = 'SELECT ' \
                  'DATE_FORMAT(Despatch_Date, \'%Y-%m-%d\'), ' \
                  'Origin, ' \
                  'Destination, ' \
                  'Mail_Category, ' \
                  'Subclass, ' \
                  'CONVERT(Serial_Number, CHAR), ' \
                  'FORMAT(No_of_ItRates, 0), ' \
                  'FORMAT(Weight_Kgs, 2) ' \
                  '' \
                  'FROM sales_data ' \
                  '' \
                  'WHERE ' \
                  'Sub_Account_Type = %(sub_account)s AND ' \
                  'Despatch_Year = %(year)s AND ' \
                  'Qtr = %(qtr)s AND ' \
                  'Country_Code = %(customer)s AND ' \
                  'Origin = %(origin)s AND ' \
                  'Destination = %(destination)s AND ' \
                  'Mail_Category = %(mail_category)s AND ' \
                  'Subclass = %(subclass)s ' \
                  '' \
                  'ORDER BY ' \
                  'Origin, ' \
                  'Destination, ' \
                  'Mail_Category, ' \
                  'Subclass, ' \
                  'Serial_Number, ' \
                  'Despatch_Date;'

            my_cursor.execute(sql, new_param_dict)

            for item in my_cursor.fetchall():
                detail_list.append(item)

            # Getting the totals for this bulk section
            sql = 'SELECT ' \
                  'FORMAT(SUM(No_of_ItRates), 0), ' \
                  'FORMAT(SUM(Weight_Kgs), 2) ' \
                  '' \
                  'FROM sales_data ' \
                  '' \
                  'WHERE ' \
                  'Sub_Account_Type = %(sub_account)s AND ' \
                  'Despatch_Year = %(year)s AND ' \
                  'Qtr = %(qtr)s AND ' \
                  'Country_Code = %(customer)s AND ' \
                  'Origin = %(origin)s AND ' \
                  'Destination = %(destination)s AND ' \
                  'Mail_Category = %(mail_category)s AND ' \
                  'Subclass = %(subclass)s;'

            my_cursor.execute(sql, new_param_dict)
            detail_list.append(my_cursor.fetchall()[0])

        cnx.close()
        return detail_list

    def run_invoices(self):
        """
        Does most of the work for this class.
        Creates the invoices from our imported pdf classes and then sends the email to customers.
        :return: None
        """
        assert self.valid

        # Summary Invoice
        summary_invoice = SummaryInvoice(address=self.details['Physical_Address'],
                                         quarter='Q' + str(self.master.param_dict['qtr']),
                                         year=str(self.master.param_dict['year']),
                                         sub_account=self.master.param_dict['sub_account'])

        for row in self._retrieve_summary_data():
            summary_invoice.insert_line(row)

        # The file name for saving the summary invoice
        summary_file = '{}{} {} Summary Invoice Q{} {}.pdf'.format(
            self.master.save_location, self.details['Country_Name'],
            self.master.param_dict['sub_account'], str(self.master.param_dict['qtr']),
            str(self.master.param_dict['year']))

        summary_invoice.output(file_name=summary_file,
                               company=self.master.prep_dict['company'],
                               department=self.master.prep_dict['department'],
                               name=self.master.prep_dict['officer'])

        del summary_invoice

        # Detail Invoice
        detail_invoice = DetailInvoice(customer=self.details['Country_Name'],
                                       year=str(self.master.param_dict['year']),
                                       quarter='Q' + str(self.master.param_dict['qtr']))

        for row in self._retrieve_detail_data():
            detail_invoice.insert_line(row)

        # The file name for saving the detail invoice
        detail_file = '{}{} {} Detail Invoice Q{} {}.pdf'.format(
            self.master.save_location, self.details['Country_Name'],
            self.master.param_dict['sub_account'], str(self.master.param_dict['qtr']),
            str(self.master.param_dict['year']))

        detail_invoice.output(detail_file)

        del detail_invoice

        # Sending the email

        # Total_less_coms removes the commas and dollar sign
        # This is so we can run the number name function on the total amount due and include
        # this text in the email to customers.
        total_less_coms = self.total_due.replace(',', '')[1::]
        first_num = number_name(int(total_less_coms.split('.')[0]))
        second_num = total_less_coms.split('.')[1].lstrip('0')

        if second_num == '':
            total_as_string = 'The total amount due is {} - {} dollars' \
                .format(self.total_due, first_num)
        else:
            second_num = number_name(int(second_num))
            total_as_string = 'The total amount due is {} - {} dollars and {} cents' \
                .format(self.total_due, first_num, second_num)

        email_message = 'Hello,\n\nPlease find your invoice attached.\n\n' \
                        '{}.\n\n' \
                        'Kind regards,\n\n{}' \
                        .format(total_as_string, self.master.prep_dict['officer'])

        email_subject = '{} Invoices Q{} {} From {}'.format(self.details['Country_Name'],
                                                            str(self.master.param_dict['qtr']),
                                                            str(self.master.param_dict['year']),
                                                            self.master.prep_dict['company'])

        self.status = send_email_365(email_recipient=self.details['Email_Address'],
                                     email_subject=email_subject,
                                     email_message=email_message,
                                     email_sender=self.master.prep_dict['email_sender'],
                                     email_password=self.master.prep_dict['email_password'],
                                     attachments=(summary_file, detail_file))[1]

        self.valid = self.status[0]

    def log_status(self, cnt=1, file_name=None):
        """
        This method is used for logging the status of the customer to a txt file.
        This text may include whether or not the email failed for instance, or if there were rates
        issues found. The log will be appended to a file if it already exists, and will create a
        new file otherwise.
        :param cnt: The number that will appear at the start of the log. Useful when logging
        many items into the same file.
        :param file_name: What txt file to log to. Will use the master date as the file name
        if none provided.
        :return: None
        """
        if file_name is None:
            file_name = '{}{}.txt'.format(self.master.log_location,
                                          self.master.date_stamp)

        if self.status is None:
            log_message = 'No files created and no emails sent.\n'

            if len(self.rates_issues) > 0:
                log_message += '\n{} rate(s) issues were found:\n'.format(len(self.rates_issues))

                for num, rate in enumerate(self.rates_issues):
                    log_message += '\t{}. {}\n'.format(num + 1, rate)

            if None in self.details.values():
                log_message += '\nCustomer address issue(s) found.\n'
                log_message += '\tName: {}\n'.format(self.details['Country_Name'])
                log_message += '\tAddress: {}\n'.format(self.details['Physical_Address'])
                log_message += '\tEmail: {}\n'.format(self.details['Email_Address'])

        else:
            log_message = self.status

        with open(file_name, 'a+') as log_file:
            print('{}. {}\n{}'.format(cnt, self.master.param_dict['customer'],
                                      log_message), file=log_file)


def main():
    """
    Will run the full process.
    Appends a count of the time the process took onto the end of the log file.
    Will email the process manager if errors are present.
    """
    start_time = time.perf_counter()

    params = Params()

    err_num = 0
    # Full log will contain everything, error log will just contain errors
    full_log = '{}{} Full Log.txt'.format(params.log_location, params.date_stamp)
    err_log = '{}{} Error Log.txt'.format(params.log_location, params.date_stamp)

    # Attempting to create invoices for each customer
    for num, item in enumerate(params.customers):
        params.param_dict['customer'] = item
        customer = Customer(params)

        if customer.valid:

            try:
                customer.run_invoices()
            except Exception as err:
                customer.status = 'The following error occurred:\n{}.\n'.format(err)
                err_num += 1
                customer.log_status(cnt=err_num, file_name=err_log)

            customer.log_status(cnt=num+1, file_name=full_log)

        else:
            customer.log_status(cnt=num+1, file_name=full_log)
            err_num += 1
            customer.log_status(cnt=err_num, file_name=err_log)

    # Append the elapsed time
    elapsed_time = time.perf_counter() - start_time
    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    with open(full_log, 'a+') as log_file:
        print('=' * 100, end='\n\n', file=log_file)
        print('ELAPSED TIME (Hours, Mins, Secs): {}.'.format(elapsed_time), file=log_file)

    # Send email to process manager if errors
    if err_num > 0:

        err_subject = '{} errors encountered - Python Invoice Creation'\
                      .format(number_name(err_num).capitalize())
        err_message = '{}({}) errors have been encountered during the creation of invoices.\n\n' \
                      'Please review attached file.'\
                      .format(number_name(err_num).capitalize(), err_num)

        send_email_365(email_recipient=params.manager_email, email_subject=err_subject,
                       email_message=err_message, email_sender=params.prep_dict['email_sender'],
                       email_password=params.prep_dict['email_password'], attachments=(err_log,))


if __name__ == '__main__':
    main()
