"""This module is used for creating a share house cleaning roster as a CSV file"""

import csv
import datetime


class House:
    """Class for storing what the roster tasks are
    and keeping track of when they need to be done"""
    # Stores the frequency of when tasks need to be completed
    # A frequency of 0.5 indicates that a task needs to be done every other week, and a frequency
    # of 1 means a task needs to be done every week.
    frequency_dict = {'Kitchen': 0.5, 'Floors': 0.5, 'Bathroom': 0.5,
                      'Laundry': 0.2, 'Oven': 0.2, 'Island Bench': 0.2,
                      'Balcony': 0.2, 'Desk': 0.5, 'Shower': 0.25, 'Fridge': 0.05}
    # Tracks when a task needs to be done. If >= 1, then it needs to be done.
    tracking_dict = {key: 0 for key in frequency_dict.keys()}
    # Tracks if someone else is already doing the task this week
    # Will not usually be necessary except if a task is missed one week and becomes >= 2.
    taken_dict = {key: False for key in frequency_dict.keys()}
    # For specifying different groups of housemates. Tasks specified here will be excluded for
    # these groups. For example, if 'Steve' is placed in group 'B', he will do every task except for
    # Desk and Balcony, but a person in group 'A' would do every task.
    groups_dict = {'A': [], 'B': ['Desk', 'Balcony']}

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
        Won't include members of groups who are excluded from a task in the count.
        :param job: String - The job name which you're enquiring the minimum for
        :return: An integer
        """
        # Creating a list of housemate groups that do this job
        relevant_groups = [gp for gp in House.groups_dict.keys()
                           if job not in House.groups_dict[gp]]
        # Creating list of all relevant members' scores
        relevant_scores = [hm.tracking_dict[job] for hm in cls.house_mates
                           if hm.group in relevant_groups]
        # Returning minimum score or zero if no results
        if len(relevant_scores) == 0:
            return 0
        return min(relevant_scores)

    @classmethod
    def reset_workload(cls):
        """
        Will reset the workload tracker for all house mates. Is required to be run when a new
        week starts.
        :return: Nothing
        """
        for hm in cls.house_mates:
            hm.workload_tracker = hm.workload

    def __init__(self, name, group, workload):
        """
        Constructor for HouseMate. After creating object, will add reference to house_mates list.
        :param name: String - the name of the house member
        :param group: String - the group that this member should be in.
        Must be in House.groups_dict.
        :param workload: int - the maximum number of jobs this person can be allocated to do each
        week.
        """
        self.tracking_dict = {key: 0 for key in House.frequency_dict.keys()}
        self.group = group
        self.name = name
        self.workload = workload
        self.workload_tracker = workload
        HouseMate.house_mates.append(self)

    def available(self, job):
        """
        Will check if housemate is available for a job.
        Being available means that the number of times they have performed a job
        is equal to the minimum number of times it has been done by any house mate.
        If house member is part of a group that doesn't do this job, they will always be
        unavailable.
        :param job: String - Name of job you're enquiring their availability for
        :return: Boolean - True if house mate is available for the job.
        """
        if (job not in House.groups_dict[self.group]) and \
                (self.tracking_dict[job] == HouseMate.min(job)):
            return True
        return False

    def allocate(self):
        """
        Will try and allocate the housemate to a job, if they are available for that job
        and the job needs to be done. Uses recursion to deal with workloads greater than 1.
        :return: A string. Either an empty string if no job allocated, or the string name
        of the job they have been allocated to.
        """
        if self.workload_tracker > 0:
            # Creates a list of the jobs in the tracking dict, sorted in descending order by value.
            # This way, jobs that are the most urgent are done first.
            for job in [td for td in {k: v for k, v in sorted(House.tracking_dict.items(),
                                                              key=lambda item: item[1],
                                                              reverse=True)}.keys()
                        if House.tracking_dict[td] >= 1 and not House.taken_dict[td]]:
                if self.available(job):
                    self.tracking_dict[job] += 1
                    House.tracking_dict[job] -= 1
                    House.taken_dict[job] = True
                    # This stops an endless loop
                    self.workload_tracker -= 1
                    # If this is not the first job being assigned for the week
                    if self.workload_tracker < self.workload - 1:
                        # Add a new line with the job
                        return '\n' + job + self.allocate()
                    # First job assigned for the week doesn't have a new line
                    return job + self.allocate()
        return ''


def create_roster(start_date, end_date, house_members, output_file):
    """
    Will create a roster based on the start date, end date, and house members.
    :param output_file: String - name of the output file. Should end with '.csv'.
    :param start_date: Must be passed as a datetime.date object
    :param end_date: Must be passed as a datetime.date object
    :param house_members: A list of lists, specifying the house members to be be created.
    Each list should contain three items - name as String, group as String, and workload as int.
    :return: None. Will output a csv file where specified.
    """

    # Making sure both dates are mondays
    while start_date.weekday() != 0:
        start_date -= datetime.timedelta(days=1)

    while end_date.weekday() != 0:
        end_date += datetime.timedelta(days=1)

    # Creating our housemate objects
    for member in house_members:
        _ = HouseMate(member[0], member[1], member[2])

    # Writing to CSV
    with open(output_file, 'w', newline='\n') as file:
        writer = csv.writer(file)
        header_row = ['Week Commencing'] + [hm.name for hm in HouseMate.house_mates]
        writer.writerow(header_row)

        while start_date < end_date:
            House.next_week()
            body_row = [start_date.strftime('%d %B %Y')] + \
                       [hm.allocate() for hm in HouseMate.house_mates]
            writer.writerow(body_row)
            start_date += datetime.timedelta(days=7)
            # Rolling over workloads to the next week
            HouseMate.reset_workload()


if __name__ == '__main__':
    create_roster(datetime.date(2022, 2, 7), datetime.date(2023, 2, 7),
                  [['Chad', 'A', 2], ['James', 'B', 2]], 'nicholson_roster.csv')
