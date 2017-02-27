from . import Cmd
from ..exceptions import HarvestToolException
from collections import OrderedDict

import subprocess
import shutil
import requests

def get_sums(data):
    day_sum = sum([entry['hours'] for entry in data['day_entries']])

    project_ids = [int(entry['project_id']) for entry in data['day_entries']]
    projects = {}
    for project in data['projects']:
        if int(project['id']) in project_ids:
            projects[int(project['id'])] = project
    billable_sum = sum([entry['hours'] for entry in data['day_entries'] if projects[int(entry['project_id'])]['billable']])
    return (billable_sum, day_sum)

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
