from . import Cmd
from ..exceptions import HarvestToolException
from collections import OrderedDict

import subprocess
import shutil
import requests
import datetime
import re

def get_sums(data):
    day_sum = sum([entry['hours'] for entry in data['day_entries']])

    project_ids = [int(entry['project_id']) for entry in data['day_entries']]
    projects = {}
    for project in data['projects']:
        if int(project['id']) in project_ids:
            projects[int(project['id'])] = project
    billable_sum = sum([entry['hours'] for entry in data['day_entries'] if projects[int(entry['project_id'])]['billable']])
    return (billable_sum, day_sum)

class TasksCommand(Cmd):
    cmd = 'tasks'
    formatter = 'table.custom'

    @classmethod
    def configure(cls, conf, parser):
        parser.add_argument('--filter', help="Filter tasks")
        parser.add_argument('--project', help="Filter tasks for a specific project")

    def run(self, args):
        data = self.tool.get('/tasks')

        task_filter = None
        if args.filter:
            task_filter = re.compile(args.filter)

        # filter by valid tasks
        valid_tasks = None
        if args.project:
            project_id = self.tool.get_project_id_from_input(args.project)
            if not project_id:
                raise HarvestToolException('Could not find project: %s' % args.project)

            tasks = self.tool.get('/projects/%d/task_assignments' % project_id)
            valid_tasks = [task['task_assignment']['task_id'] for task in tasks]

        tasks = []
        for task in data:
            result = OrderedDict()
            result['id'] = task['task']['id']
            result['name'] = task['task']['name']
            if task_filter and not task_filter.search(result['name']):
                continue
            if valid_tasks != None and result['id'] not in valid_tasks:
                continue
            tasks.append(result)

        tasks = sorted(tasks, key=lambda task: task['name'])
        if not tasks:
            return

        args.headers = ['ID', 'Name']
        args.row_keys = ['id', 'name']
        args.align = {'ID': 'l', 'Name': 'l'}
        return tasks


class AllCommand(Cmd):
    cmd = 'all'
    formatter = 'table.custom'

    @classmethod
    def configure(cls, conf, parser):
        parser.add_argument('--filter', help="Add a comment to the issue(s)")

    def run(self, args):
        data = self.tool.get('/projects')

        project_filter = None
        if args.filter:
            project_filter = re.compile(args.filter)

        projects = []
        for project in data:
            result = OrderedDict()
            result['code'] = project['project']['code']
            result['id'] = project['project']['id']
            result['name'] = project['project']['name']
            if project_filter and not project_filter.search(result['name']):
                continue
            projects.append(result)

        projects = sorted(projects, key=lambda project: project['name'])
        if not projects:
            return

        args.headers = ['Code', 'ID', 'Name']
        args.row_keys = ['code', 'id', 'name']
        args.align = {'Code': 'l', 'ID': 'l', 'Name': 'l'}
        return projects
