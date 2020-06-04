"""
An assortment of python functions
"""

from string import ascii_lowercase as alphabet


def number_name(entry):
    """
    Will return the name of a number as a string. Input x as a number.
    The number can be negative and/or floating.
    """

    one_to_19 = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six',
                 '7': 'seven', '8': 'eight', '9': 'nine', '10': 'ten', '11': 'eleven',
                 '12': 'twelve', '13': 'thirteen', '14': 'fourteen', '15': 'fifteen',
                 '16': 'sixteen', '17': 'seventeen', '18': 'eighteen', '19': 'nineteen',
                 '0': 'zero'}

    def hundreds(num):
        """
        Use this function to get the name of an integer in words.
        Input the number as a string, with a length no greater than 3.
        """

        double_digits = {'2': 'twenty', '3': 'thirty', '4': 'forty', '5': 'fifty', '6': 'sixty',
                         '7': 'seventy', '8': 'eighty', '9': 'ninety'}

        # Removing leading zeroes
        num = num.lstrip('0')

        if len(num) > 2:
            return_string = one_to_19[num[0]] + ' hundred'
            if num[1:] != '00':
                return_string += (' and ' + hundreds(num[1:]))
            return return_string

        if num in one_to_19:
            return one_to_19[num]

        return_string = double_digits[num[0]]
        if num[1] != '0':
            return_string += (' ' + one_to_19[num[1]])
        return return_string

    def what_denomination(num_length, name=False):
        """
        Input an integer into this function to determine where it sits on the denominations tuple.
        Do not input an integer with length less than the lowest denominations number.
        For instance, if your string had a length of 5, it would be determined as thousands
        and would return 3. If you specified 'name' as True, it would return 'thousand'.
        """
        denominations = ((18, 'quintillion'), (15, 'quadrillion'), (12, 'trillion'),
                         (9, 'billion'), (6, 'million'), (3, 'thousand'))

        for length, title in denominations:
            if num_length > length:
                if name:
                    return title
                return length
        return None

    def floating_nums(decimals):
        """
        This function will return the numbers you'll need to add the decimals to
        the end the string.
        Input a sequence of numbers with no spaces as a string into this function.
        For instance, '12' will become 'point one two'.
        """
        return_string = ' point '
        for place in decimals:
            return_string += (one_to_19[place] + ' ')
        return_string = return_string.rstrip()
        return return_string

    def create_list(str_num):
        """
        Use this function to return a list of all the
        smaller numbers that make up the whole number.
        For instance, 1001 would return a two element
        list of 'one thousand', and 'one'. Input the
        string of an integer.
        """
        if str_num == '0':
            return ['zero']

        return_list = []

        while str_num:

            if str_num.strip('0') == '':
                str_num = ''
            elif len(str_num) > 3:

                # the desired string length we're interested in
                current_length = len(str_num)
                desired_length = current_length - what_denomination(current_length)

                # Checking for zeroes first
                if str_num[:desired_length].strip('0') != '':
                    appendage = hundreds(str_num[:desired_length]) + ' ' + \
                                what_denomination(current_length, name=True)

                    # Adding to the list
                    return_list.append(appendage)

                # Readjusting the length of x
                str_num = str_num[desired_length:]

            else:
                return_list.append(hundreds(str_num))
                str_num = ''

        return return_list

    def create_string(is_negative, full_list, floats):
        """
        Use this function to create a string out of the list of numbers.
        Use the 'floats' parameter to input a string of decimals.
        Use the 'is_negative' boolean parameter to input whether it is negative.
        """
        if is_negative:
            return_string = 'negative '
        else:
            return_string = ''

        pen = len(full_list) - 2

        for cnt, i in enumerate(full_list):
            return_string += i

            # Last item
            if cnt == (pen + 1):

                # Adding in our floating numbers
                if floats != '':
                    return_string += floating_nums(floats)

            # Second last item
            elif cnt == pen and full_list[-1].count(' ') < 2:
                return_string += ' and '

            # Anything else
            else:
                return_string += ', '

        return return_string

    def run_tests(raw_input):
        """
        Simple function to check that the user input is a valid number and is not too large.
        """
        if not isinstance(raw_input, float) and not isinstance(raw_input, int):
            raise InputError('Number is not valid.')

        if 'e' in str(raw_input):
            raise InputError('The number you have specified is too '
                             'long as it is in scientific notation.')

        raw_input = str(raw_input).split('.')[0]
        raw_input = raw_input.lstrip('-')
        if len(raw_input) > 21:
            raise InputError('Number is too Long. The maximum denomination allowed for '
                             'this function is quintillion.')

    # ========== Main Procedure ==========
    run_tests(entry)
    entry = str(entry)

    # Checking if negative
    negative = (entry[0] == '-')
    entry = entry.lstrip('-')

    # Checking for floats
    if '.' in entry:
        entry, float_nums = entry.split('.')
    else:
        float_nums = ''

    # Creating our list and string
    final_list = create_list(entry)
    return create_string(negative, final_list, float_nums)


class InputError(Exception):
    """Very simple class to trap input errors"""
    def __init__(self, message=None):
        """Calling parent class"""
        if message:
            super().__init__(message)
        else:
            super().__init__('Inputted value does not conform to requirements.')


def pig_latin(str_input):
    """
    Converts a string into pig latin, keeping punctuation
    and capitalization in the same spot
    """
    my_list = []
    vowels = 'aeiou'
    my_string = ''

    str_input = str_input.strip()
    tracker = 0

    # Making a list of words used
    for num, char in enumerate(str_input):
        if char.lower() not in alphabet:
            if str_input[tracker:num] != '':
                my_list.append(str_input[tracker:num])
            my_list.append(char)

            tracker = num + 1

    # Grabbing the last sequence
    if str_input[tracker:] != '':
        my_list.append(str_input[tracker:])

    # Making a final string
    for element in my_list:

        if len(element) == 1:
            my_string += element

        else:
            vowel_start = 0

            for num, char in enumerate(element):

                if char in vowels:
                    vowel_start = num
                    break

            appendage = (element[vowel_start:] + element[:vowel_start] + 'ay')

            # Checking if whole word is upper
            if element.isupper():
                appendage = appendage.upper()

            # Checking if start is capital
            elif element[0:1].isupper():
                appendage = appendage.capitalize()

            my_string += appendage

    return my_string


def caesar_cipher(my_string, shifter):
    """Simple Caesar Cipher encoding function"""
    final_string = ''

    for char in my_string:

        if char.isalpha():

            appendage = ord(char.lower()) + shifter

            if appendage > 122:
                appendage -= 26
            if appendage < 97:
                appendage += 26

            appendage = chr(appendage)

            if char.isupper():
                appendage = appendage.upper()

            final_string += appendage
        else:
            final_string += char

    return final_string


def caesar_cipher_decoder(my_string):
    """
    Simple Caesar Cipher decoding function. Uses letter frequencies from Wikipedia.
    """
    # Master frequency tuples
    freq = (('a', 8.167), ('b', 1.492), ('c', 2.202), ('d', 4.253), ('e', 12.702), ('f', 2.228),
            ('g', 2.015), ('h', 6.094), ('i', 6.966), ('j', 0.153), ('k', 1.292), ('l', 4.025),
            ('m', 2.406), ('n', 6.749), ('o', 7.507), ('p', 1.929), ('q', 0.095), ('r', 5.987),
            ('s', 6.327), ('t', 9.356), ('u', 2.758), ('v', 0.978), ('w', 2.560), ('x', 0.150),
            ('y', 1.994), ('z', 0.077))

    # Creating our letter counting dictionary
    my_dict = {}
    for letter in alphabet:
        my_dict[letter] = 0

    # Counting the letter frequency in my_string
    total = 0
    for char in my_string:

        if char.lower() in my_dict:
            my_dict[char.lower()] += 1
            total += 1

    # Converting our dictionary into lists
    my_dict = [[k, v / total * 100] for k, v in my_dict.items()]

    # Comparing our lists
    common = []

    # Seeing which key has the most similarity to the master tuple
    for _ in range(26):

        my_dict = [my_dict[-1]] + my_dict[:-1]

        total = 0

        for num in range(26):
            total += abs(my_dict[num][1]-freq[num][1])
        common.append(total)

    common.reverse()

    key = common.index(min(common))

    return 'Key: {}. {}.'.format(key, caesar_cipher(my_string, -key))
