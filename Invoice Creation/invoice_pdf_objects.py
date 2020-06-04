"""
Invoice PDF Objects - contains two classes for creating PDF invoices using PyFPDF Library.
Objects have been designed for specific automated process in invoice_creation.py.
"""

from datetime import datetime
from fpdf import FPDF


class SummaryInvoice(FPDF):
    """
    Class for the creation of summary style invoices.
    Inherits from the imported PyFPDF class.
    Includes 4 methods and an init.
    3 of these methods override parent methods.
    """

    # The widths of the 14 columns in the invoice
    column_widths = [15, 15, 20, 15,
                     15, 20, 20, 20,
                     25, 20, 20,
                     25, 25, 22]

    # The corresponding titles of these 14 columns
    column_titles = ['Operator', 'Origin', 'Destination', 'Category',
                     'Subclass', 'Items', 'Weight', 'Item Rate',
                     'TD Item Rate', 'Item Amount', 'Weight Rate',
                     'TD Weight Rate', 'Weight Amount', 'Total Amount']

    # The default cell height for rows in the invoice
    cell_height = 5

    def __init__(self, address, year, quarter, sub_account):
        """
        Initialise class
        Calls the super class immediately to create a PDF.
        :param address: The customer's address that will be printed on the invoice.
        Can cover as many as 8 lines, broken up by '\n' strings.
        :param year: Year string printed at top right hand corner of invoice.
        :param quarter: Quarter string printed at top right hand corner of invoice.
        :param sub_account: Sub account string printed at top right hand corner of invoice.
        """
        # Default page is landscape A4
        super().__init__(orientation='L', unit='mm', format='A4')
        self.address = address
        self.year = year
        self.quarter = quarter
        self.sub_account = sub_account
        # Allows new pages to be created automatically
        self.accept_page_break()
        self.date_stamp = datetime.now().strftime('%Y-%m-%d')
        # Magic method call here that counts up the total
        # number of pages and puts it in the footer.
        self.alias_nb_pages()
        self.add_page()

    def header(self):
        """
        According to the documentation, the header method is called whenever the 'add_page' method
        is called in the super class. Here we override this method to put in a custom header.
        :return: None
        """
        self.set_font('Arial', size=9)
        address_list = self.address.split('\n')

        # Makes up the lines of our doc header
        header_list = [['', 'Year', self.year],
                       ['', 'Quarter', self.quarter],
                       ['', 'Date', self.date_stamp],
                       [''],
                       ['', 'Sub Account Type'],
                       ['', self.sub_account],
                       [''],
                       ['']]

        # Adding in each line of the customer address into our header list
        for num, item in enumerate(header_list):
            if len(address_list) >= num + 1:
                item[0] = address_list[num]
            else:
                break

        # Defining header column widths
        address_column_width = 235
        param_column_width = 20
        type_column_width = 30

        # First Line
        self.set_font('', 'B')
        self.cell(address_column_width, self.cell_height, txt=header_list[0][0], align='L')

        self.set_font('', '')
        self.cell(param_column_width, self.cell_height, txt=header_list[0][1], align='C', border=1)
        self.cell(param_column_width, self.cell_height,
                  txt=header_list[0][2], align='C', border=1, ln=1)

        # Second Line
        self.set_font('', 'B')
        self.cell(address_column_width, self.cell_height, txt=header_list[1][0], align='L')

        self.set_font('', '')
        self.cell(param_column_width, self.cell_height, txt=header_list[1][1], align='C', border=1)
        self.cell(param_column_width, self.cell_height,
                  txt=header_list[1][2], align='C', border=1, ln=1)

        # Third Line
        self.set_font('', 'B')
        self.cell(address_column_width, self.cell_height, txt=header_list[2][0], align='L')

        self.set_font('', '')
        self.cell(param_column_width, self.cell_height, txt=header_list[2][1], align='C', border=1)
        self.cell(param_column_width, self.cell_height,
                  txt=header_list[2][2], align='C', border=1, ln=1)

        # Fourth Line
        self.set_font('', 'B')
        self.cell(address_column_width, self.cell_height, txt=header_list[3][0], align='L', ln=1)

        # Fifth Line
        self.cell(address_column_width, self.cell_height, txt=header_list[4][0], align='L')

        self.set_font('', 'BU')
        self.cell(type_column_width, self.cell_height, txt=header_list[4][1], ln=1, align='L')

        # Sixth Line
        self.set_font('', 'B')
        self.cell(address_column_width, self.cell_height, txt=header_list[5][0], align='L')

        self.set_font('', '')
        self.cell(type_column_width, self.cell_height, txt=header_list[5][1], ln=1, align='L')

        # Seventh Line
        self.set_font('', 'B')
        self.cell(address_column_width, self.cell_height, txt=header_list[6][0], align='L', ln=1)

        # Eighth Line
        self.cell(address_column_width, self.cell_height, txt=header_list[7][0], align='L', ln=1)

        # Adding the title in the centre
        self.set_font('', 'B')
        self.cell(0, self.cell_height, txt='SUMMARIZED ACCOUNT', ln=1, align='C')
        self.ln(self.cell_height)

        # Column titles
        self.set_font_size(8)
        for num, col in enumerate(self.column_widths):

            # Ensuring we start a new line after the last column
            if num == len(self.column_widths) - 1:
                line = 1
            else:
                line = 0

            self.cell(col, self.cell_height*2, txt=self.column_titles[num],
                      ln=line, align='C', border=1)

    def footer(self):
        """
        According to the documentation, the footer method is also called whenever the 'add_page'
        method is called. Here we override this method to put in a custom footer, using the
        magic 'nb' variable.
        :return: None
        """
        self.set_y(-10)
        self.set_font('Arial', 'I', 8)

        # Add a page number
        page = 'Page ' + str(self.page_no()) + ' of {nb}'
        self.cell(0, 10, page, 0, 0, 'C')

    def insert_line(self, line_items):
        """
        Method that adds all of the lines into the invoice. Lines should be added one at a time.
        :param line_items: Should be a list (or tuple) of strings. The length can either be equal
        to the number of columns in the invoice or 5. If the length is equal to the number of
        columns it will put each item in a column. If the length is equal to 5, it will interpret
        this as being the two totals rows. Ideally, you should add in all the lines first and then
        add the totals at the end and then output the file.
        :return: None
        """
        # Enforcing the list lengths
        assert len(line_items) in [len(self.column_widths), 5]

        # If we have a full list
        if len(line_items) == len(self.column_widths):

            self.set_font('', '', 8)

            for num, item in enumerate(line_items):
                if num == len(line_items) - 1:
                    line = 1
                else:
                    line = 0

                # These columns specifically need to be right aligned
                if num in [5, 6, 9, 12, 13]:
                    align = 'R'
                # Otherwise they should be centre aligned
                else:
                    align = 'C'

                self.cell(self.column_widths[num], self.cell_height, txt=item,
                          align=align, border=1, ln=line)

        # If we have a totals list
        else:
            # Deciding whether or not to insert a new page

            # The logic behind this here is that because the orientation of this page is landscape
            # and the size of the margin on all sides is 10mm, the writing space we have available
            # to us per page is 190mm (A4 pages have a width of 210mm). What we are trying to
            # assure it that the two totals rows and the ending tag are on the same page regardless
            # of the number of rows in the invoice.

            # The assumption this works under is that the height of the two totals rows and the
            # ending tag (in output method below) combined is equal to 12 regular cell heights.
            # Therefore, if the current position of y plus the product of these 12 cells and the
            # default cell height is greater than the writing space of 190mm, we will need to add
            # a new page.

            if (int(self.get_y()) + 12 * self.cell_height) > 190:
                self.add_page()

            # Setting the colour for the blank cells as grey
            self.set_fill_color(169, 169, 169)
            self.set_font('', 'B', 8)

            # Total box spanning five columns
            self.cell(sum(self.column_widths[0:5]), self.cell_height, txt='Total', border=1)

            # Columns 5 and 6 totals
            self.cell(self.column_widths[5], self.cell_height,
                      txt=line_items[0], align='R', border=1)
            self.cell(self.column_widths[6], self.cell_height,
                      txt=line_items[1], align='R', border=1)

            # Columns 7 and 8 blacked out
            self.cell(self.column_widths[7] + self.column_widths[8],
                      self.cell_height, border=1, fill=True)

            # Column 9
            self.cell(self.column_widths[9], self.cell_height,
                      txt=line_items[2], align='R', border=1)

            # Columns 10 and 11 blacked out
            self.cell(self.column_widths[10] + self.column_widths[11],
                      self.cell_height, border=1, fill=True)

            # Column 12
            self.cell(self.column_widths[12], self.cell_height,
                      txt=line_items[3], align='R', border=1)

            # Column 13 blacked out
            self.cell(self.column_widths[13], self.cell_height,
                      border=1, fill=True, ln=1)

            # New Row - Grand Total box spanning five columns
            self.cell(sum(self.column_widths[0:-2]), self.cell_height, txt='Grand Total', border=1)

            # Inserting the grand total figure
            self.cell(self.column_widths[-2] + self.column_widths[-1], self.cell_height,
                      txt=line_items[4], border=1, ln=1, align='R')

    def output(self, file_name, name, department, company):
        """
        Output is a method of the parent class and creates the actual PDF document output.
        This overrides the parent method, adding in an ending tag for the invoice, before
        calling the parent output method.
        :param file_name: String for what the output file should be called. Can include path.
        :param name: The string name of the processing officer that will appear on the invoice.
        :param department: The string name of the department.
        :param company: The string name of the company.
        :return: None
        """
        # Add line break
        self.ln(self.cell_height*2)

        # Set Font
        self.set_font('', 'B', 9)

        # Adding in details
        self.cell(sum(self.column_widths[0:8]), self.cell_height,
                  txt='Administration preparing the account', align='L')
        self.cell(sum(self.column_widths[8:]), self.cell_height,
                  txt='Seen and Accepted by administration of origin', ln=1, align='L')

        pds = 'Place, Date and Signature'
        self.cell(sum(self.column_widths[0:8]), self.cell_height, txt=pds, align='L')
        self.cell(sum(self.column_widths[8:]), self.cell_height, txt=pds, ln=1, align='L')

        self.ln(self.cell_height)

        # Each of the four following components starts with a buffer
        # Name
        self.cell(self.cell_height, self.cell_height)
        self.cell(0, self.cell_height, ln=1, txt=name, align='L')

        # Department
        self.cell(self.cell_height, self.cell_height)
        self.cell(0, self.cell_height, ln=1, txt=department, align='L')

        # Company
        self.cell(self.cell_height, self.cell_height)
        self.cell(0, self.cell_height, ln=1, txt=company, align='L')

        # Date
        self.cell(self.cell_height, self.cell_height)
        self.cell(0, self.cell_height, ln=1, txt=self.date_stamp, align='L')

        self.ln(self.cell_height)

        # Drawing two lines for signing the document
        current_x = self.get_x()
        current_y = self.get_y()
        self.line(current_x, current_y, current_x + sum(self.column_widths[0:6]), current_y)
        self.line(current_x + sum(self.column_widths[0:8]), current_y,
                  current_x + sum(self.column_widths[0:-1]), current_y)

        # Calling parent class
        super().output(file_name)


class DetailInvoice(FPDF):
    """
    Class for the creation of detail style invoices.
    Inherits from the imported PyFPDF class.
    Contains 3 methods and an init. 2 of those methods override the parent class.
    Is very similar in structure to the SummaryInvoice class, although it does not have an ending
    tag and is portrait instead of landscape. It can also have multiple totals rows instead of
    just have totals rows at the end.
    """

    # The widths of the 8 columns in the invoice
    column_widths = [23.75 for x in range(8)]

    # The corresponding titles of these 8 columns
    column_titles = ['Despatch Date', 'Origin', 'Destination', 'Category',
                     'Subclass', 'Serial Number', 'Items', 'Weight']

    # The default cell height for rows in the invoice
    cell_height = 5

    def __init__(self, customer, year, quarter):
        """
        Initialise class
        Calls the super class immediately to create a PDF.
        :param customer: Name string of customer that appears at top of invoice.
        :param year: Year string printed at top of invoice.
        :param quarter: Quarter string printed at top of invoice.
        """
        # Default page is portrait A4
        super().__init__(orientation='P', unit='mm', format='A4')
        self.customer = customer
        self.year = year
        self.quarter = quarter
        # Allows new pages to be created automatically
        self.accept_page_break()
        self.date_stamp = datetime.now().strftime('%Y-%m-%d')
        # Magic method call here that counts up the total
        # number of pages and puts it in the footer.
        self.alias_nb_pages()
        self.add_page()

    def header(self):
        """
        According to the documentation, the header method is called whenever the 'add_page' method
        is called in the super class. Here we override this method to put in a custom header.
        :return: None
        """
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(169, 169, 169)

        # Title
        self.cell(0, self.cell_height*2, txt='DETAILED ACCOUNT', border=1,
                  ln=1, fill=True, align='C')
        self.ln(self.cell_height)

        # Second line
        self.set_font('', 'B')
        self.cell(sum(self.column_widths[0:3]), self.cell_height,
                  txt='Administration preparing the form:', border=1, align='L')
        self.set_font('', '')
        self.cell(sum(self.column_widths[3:5]), self.cell_height,
                  txt='Australia', border=1, align='C', ln=1)
        self.ln(self.cell_height)

        # Third line
        self.set_font('', 'B')
        self.cell(sum(self.column_widths[0:3]), self.cell_height,
                  txt='Administration of destination:', border=1, align='L')
        self.set_font('', '')
        self.cell(sum(self.column_widths[3:5]), self.cell_height,
                  txt=self.customer, border=1, align='C', ln=1)
        self.ln(self.cell_height)

        # Fourth line
        self.set_font('', 'B')
        self.cell(self.column_widths[0], self.cell_height, txt='Period', border=1, align='C')
        self.set_font('', '')
        self.cell(self.column_widths[1], self.cell_height, txt=self.year + ' ' + self.quarter,
                  border=1, align='C')

        self.cell(sum(self.column_widths[2:-2]), self.cell_height)

        self.set_font('', 'B')
        self.cell(self.column_widths[-2], self.cell_height, txt='Date', border=1, align='C')
        self.set_font('', '')
        self.cell(self.column_widths[-1], self.cell_height,
                  txt=self.date_stamp, align='C', border=1, ln=1)

        self.ln(self.cell_height)

        # Insert columns
        self.set_font('', 'B', 8)
        for num, col in enumerate(self.column_widths):

            # Ensuring we start a new line after the last column
            if num == len(self.column_widths) - 1:
                line = 1
            else:
                line = 0

            self.cell(col, self.cell_height*2, txt=self.column_titles[num],
                      ln=line, align='C', border=1)

    def footer(self):
        """
        According to the documentation, the footer method is also called whenever the 'add_page'
        method is called. Here we override this method to put in a custom footer, using the
        magic 'nb' variable.
        :return: None
        """
        self.set_y(-10)
        self.set_font('Arial', 'I', 8)

        # Add a page number
        page = 'Page ' + str(self.page_no()) + ' of {nb}'
        self.cell(0, 10, page, 0, 0, 'C')

    def insert_line(self, line_items):
        """
        Method that adds all of the lines into the invoice. Lines should be added one at a time.
        :param line_items: Should be a list (or tuple) of strings. The length can either be equal
        to the number of columns in the invoice or 2. If the length is equal to the number of
        columns it will put each item in a column. If the length is equal to 2, it will interpret
        this as being a totals row.
        :return: None
        """
        # Enforcing the list lengths
        assert len(line_items) in [len(self.column_widths), 2]

        # If we have a full list
        if len(line_items) == len(self.column_widths):

            self.set_font('', '', 8)

            for num, item in enumerate(line_items):
                if num == len(line_items) - 1:
                    line = 1
                else:
                    line = 0

                # These columns specifically need to be right aligned
                if num in [6, 7]:
                    align = 'R'
                # Otherwise they should be centre aligned
                else:
                    align = 'C'

                self.cell(self.column_widths[num], self.cell_height, txt=item,
                          align=align, border=1, ln=line)

        # If we only have 2 elements in the list, we have a totals row
        else:
            self.set_font('', 'B', 8)

            self.cell(sum(self.column_widths[0:-2]), self.cell_height, txt='Total', border=1,
                      align='L')
            self.cell(self.column_widths[-2], self.cell_height, txt=line_items[0], border=1,
                      align='R')
            self.cell(self.column_widths[-1], self.cell_height, txt=line_items[1], border=1,
                      align='R', ln=1)
