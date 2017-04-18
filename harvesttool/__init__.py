import sys
import requests
import json
import re
from . import configuration
from . import exceptions
from . import format

class HarvestTool(object):
    def __init__(self):
        self.config = None

    def build_headers(self, headers=None):
        request_headers = {
            'content-type': 'application/json',
            'accept': 'application/json'
        }
        if headers:
            request_headers.update(headers)
        return request_headers

    def build_url(self, uri):
        return "https://%s.harvestapp.com%s" % (self.config['host'], uri)

    def get(self, uri):
        try:
            r = requests.get(self.build_url(uri), auth=self.get_authentication(), headers=self.build_headers())
            assert r.status_code == 200
            assert r.headers['Content-Type'].startswith('application/json')
            return r.json()
        except AssertionError as e:
            if r.status_code == 404:
                print(self.build_url(uri))
            sys.stderr.write("Error retrieving information from the API\n")
            sys.exit(1)

    def get_authentication(self):
        return configuration.get_authentication(self.config)

    def get_project_id_from_code(self, code):
        projects = self.get('/projects')
        for project in projects:
            if project['project']['code'] == code:
                return project['project']['id']
        return False

    def get_project_id_from_input(self, code):
        if re.search('^\d+$', code):
            return int(code)
        return self.get_project_id_from_code(code)

    def get_task_id_from_code(self, code, project=None):
        if not project:
            tasks = self.get('/tasks')
            for task in tasks:
                if task['task']['code'] == code:
                    return task['task']['id']
            return False

        tasks = self.get()

    def get_task_id_from_input(self, input):
        if re.search('^\d+$', input):
            return int(input)
        return self.get_task_id_from_code(input)

    def post(self, uri, data=None):
        try:
            print(json.dumps(data))
            r = requests.post(self.build_url(uri), auth=self.get_authentication(), headers=self.build_headers(), data=json.dumps(data))
            assert r.status_code >= 200 and r.status_code <= 300
            assert r.headers['Content-Type'].startswith('application/json')
            return r.json()
        except AssertionError as e:
            print(r.status_code)
            print(r.content)
            sys.stderr.write("Error sending information to the API\n")
            sys.exit(1)

    def run(self, args=None):
        self.config = configuration.load()

        if (args):
            try:
                (results, formatter) = commands.run_command(self, args)
            except exceptions.HarvestToolException as e:
                sys.stderr.write("Error: %s\n" % e)
                sys.exit(1)

            if results == None or results == False:
                sys.exit(1)

            if results == True:
                sys.exit()

            formatter = format.get_formatter(self, args, formatter)
            formatter(self, args, results)
