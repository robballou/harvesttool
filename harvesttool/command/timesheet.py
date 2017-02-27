from . import Cmd
from ..exceptions import HarvestToolException
from collections import OrderedDict

import subprocess
import shutil
import requests

class TodayCommand(Cmd):
    cmd = 'today'
    formatter = 'table.grid'

    def run(self, args):
        data = self.tool.get('/daily')
        day_sum = sum([entry['hours'] for entry in data['day_entries']])

        project_ids = [int(entry['project_id']) for entry in data['day_entries']]
        projects = {}
        for project in data['projects']:
            if int(project['id']) in project_ids:
                projects[int(project['id'])] = project
        billable_sum = sum([entry['hours'] for entry in data['day_entries'] if projects[int(entry['project_id'])]['billable']])

        result = OrderedDict()
        result['billable'] = billable_sum
        result['total'] = day_sum
        return result
