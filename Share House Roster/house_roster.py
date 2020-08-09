"""This module is used for creating a share house cleaning roster as a CSV file"""

import csv
import datetime


class House:
    """Class for storing what the roster tasks are
    and keeping track of when they need to be done"""
    # Stores the frequency of when tasks need to be completed
    frequency_dict = {'Kitchen': 1, 'Floors': 1, 'Bathroom': 0.5,
                      'Laundry': 0.25, 'Lawns': 0.25, 'Oven': 0.2}
    # Tracks when a task needs to be done. If >= 1, then it needs to be done.
    tracking_dict = {key: 0 for key in frequency_dict.keys()}
    # Tracks if someone else is already doing the task this week
    # Will not usually be necessary except if a task is missed one week and becomes >= 2.
    taken_dict = {key: False for key in frequency_dict.keys()}

    @classmethod
    def next_week(cls):
        """Moves onto the next week by updating the tracking dict and resetting the taken_dict"""
        for key in cls.tracking_dict.keys():
            cls.tracking_dict[key] += cls.frequency_dict[key]
            cls.taken_dict[key] = False


class HouseMate:
    """Class for each house mate as well as storing class methods"""
    # This list will store the object reference for each house mate created
    house_mates = []

    @classmethod
    def min(cls, job):
        """
        Will return the minimum number of times any member of the house has done a task.
        Except if the housemate is not inside, then it will exclude them from bathroom.
        :param job: The job name which you're enquiring the minimum for
        :return: An integer
        """
        if job == 'Bathroom':
            return min([hm.tracking_dict[job] for hm in cls.house_mates if hm.inside])
        return min([hm.tracking_dict[job] for hm in cls.house_mates])

    def __init__(self, name, inside):
        """
        :param name: Name of housemate
        :param inside: A boolean value of whether or not the housemate is inside the main house
        """
        self.tracking_dict = {key: 0 for key in House.frequency_dict.keys()}
        self.inside = inside
        self.name = name
        HouseMate.house_mates.append(self)

    def available(self, job):
        """
        Will check if housemate is available for a job.
        Being available means that the number of times they have performed a job
        is equal to the minimum number of times it has been done by any house mate.
        Housemates not inside are always unavailable for doing the bathroom.
        :param job: Name of job you're enquiring their availability for
        :return: Boolean
        """
        if not (self.inside is False and job == 'Bathroom'):
            if self.tracking_dict[job] == HouseMate.min(job):
                return True
        return False

    def allocate(self):
        """
        Will try and allocate the housemate to a job, if they are available for that job
        and the job needs to be done.
        :return: A string. Either an empty string if no job allocated, or the string name
        of the job they have been allocated to.
        """
        for job in [td for td in House.tracking_dict.keys()
                    if House.tracking_dict[td] >= 1 and not House.taken_dict[td]]:
            if self.available(job):
                self.tracking_dict[job] += 1
                House.tracking_dict[job] -= 1
                House.taken_dict[job] = True
                return job
        return ''


def create_roster(start_date, end_date, house_dict):
    """
    Will create a roster based on the start date, end date, and house mates.
    :param start_date: Must be passed as a datetime.date object
    :param end_date: Must be passed as a datetime.date object
    :param house_dict: A dictionary containing house mate names as keys, with the key values
    being boolean values of whether or not a house mate is inside the main house.
    :return: None. Will output a csv file.
    """

    # Making sure both dates are mondays
    while start_date.weekday() != 0:
        start_date -= datetime.timedelta(days=1)

    while end_date.weekday() != 0:
        end_date += datetime.timedelta(days=1)

    # Creating our housemate objects
    for name in house_dict.keys():
        _ = HouseMate(name, inside=house_dict[name])

    # Writing to CSV
    with open('HouseRoster.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        header_row = ['Week Commencing'] + [hm.name for hm in HouseMate.house_mates]
        writer.writerow(header_row)

        while start_date < end_date:
            House.next_week()
            body_row = [start_date.strftime('%d %B %Y')] + \
                       [hm.allocate() for hm in HouseMate.house_mates]
            writer.writerow(body_row)
            start_date += datetime.timedelta(days=7)


create_roster(datetime.date(2020, 8, 10), datetime.date(2021, 12, 31),
              {'Chad': True, 'James': True, 'Max': True, 'Tom': False, 'Roberto': False})
