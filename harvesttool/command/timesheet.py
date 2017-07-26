from . import Cmd
from ..exceptions import HarvestToolException
from collections import OrderedDict

import subprocess
import shutil
import requests
import datetime

def entry_is_billable(entry, projects):
    project_id = int(entry['project_id'])
    project = projects[project_id]

    if not project['billable']:
        return False

    task_id = int(entry['task_id'])
    task = [task for task in project['tasks'] if task['id'] == task_id]

    if not task[0]['billable']:
        return False

    return True


def get_sums(data):
    day_sum = sum([entry['hours'] for entry in data['day_entries']])

    project_ids = [int(entry['project_id']) for entry in data['day_entries']]
    projects = {}
    for project in data['projects']:
        if int(project['id']) in project_ids:
            projects[int(project['id'])] = project
    for entry in data['day_entries']:
        print(int(entry['project_id']))
        print(entry)
        print(projects[int(entry['project_id'])])
    billable_sum = sum([entry['hours'] for entry in data['day_entries'] if entry_is_billable(entry, projects)])
    return (billable_sum, day_sum)

class AddCommand(Cmd):
    cmd = 'add'

    @classmethod
    def configure(cls, conf, parser):
        parser.add_argument('project', help='The project ID')
        parser.add_argument('task', help='The task ID')
        parser.add_argument('hours', help='User to assign to')
        parser.add_argument('--task', help="Task ID")
        parser.add_argument('--date', default=datetime.date.today(), help="The date for this entry")
        parser.add_argument('--jira', help="Add a comment to the issue(s)")

    def run(self, args):
        entry = {
            'project_id': self.tool.get_project_id_from_input(args.project),
            'task_id': self.tool.get_task_id_from_input(args.task),
            'hours': float(args.hours),
            'start_at': args.date.strftime('%Y-%m-%d')
        }
        if args.task:
            entry['task_id'] = args.task
        self.tool.post('/daily/add', data=entry)

class BillableCommand(Cmd):
    cmd = 'billable'
    formatter = 'output.stdout'

    def run(self, args):
        data = self.tool.get('/daily')

        (billable_sum, day_sum) = get_sums(data)
        return billable_sum

class TotalCommand(Cmd):
    cmd = 'total'
    formatter = 'output.stdout'

    def run(self, args):
        data = self.tool.get('/daily')

        (billable_sum, day_sum) = get_sums(data)
        return day_sum

class TodayCommand(Cmd):
    cmd = 'today'
    formatter = 'table.grid'

    def run(self, args):
        data = self.tool.get('/daily')

        (billable_sum, day_sum) = get_sums(data)

        result = OrderedDict()
        result['billable'] = billable_sum
        result['total'] = day_sum
        return result

class WeekCommand(Cmd):
    cmd = 'week'
    formatter = 'table.multiday_grid'

    def get_day(self, weekday):
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return weekdays[weekday]

    def run(self, args):
        current_day = now = datetime.datetime.now()
        year = now.year
        day_of_the_week = now.weekday()
        current_day_of_the_year = now.timetuple().tm_yday
        days_to_request = [(current_day_of_the_year, year, now)]

        while day_of_the_week > 0:
            current_day = current_day - datetime.timedelta(days=1)
            day_of_the_week = current_day.weekday()
            current_day_of_the_year = current_day.timetuple().tm_yday
            year = current_day.year
            days_to_request.append((current_day_of_the_year, year, current_day))

        days_to_request.reverse()
        week_data = []
        totals = {'billable': 0, 'total': 0}
        for day in days_to_request:
            data = self.tool.get('/daily/%d/%d' % (day[0], day[1]))

            (billable_sum, day_sum) = get_sums(data)

            result = OrderedDict()
            result['date'] = self.get_day(day[2].weekday())
            result['billable'] = billable_sum
            result['total'] = day_sum
            week_data.append(result)
            totals['billable'] += billable_sum
            totals['total'] += day_sum

        totals_dict = OrderedDict()
        totals_dict['date'] = 'Total'
        totals_dict['billable'] = '%0.2f (%0.2f%%)' % (
            totals['billable'],
            (totals['billable'] / totals['total']) * 100,
        )
        totals_dict['total'] = totals['total']
        week_data.append(totals_dict)

        return week_data
