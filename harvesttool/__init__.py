import sys
import requests
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
            sys.stderr.write("Error retrieving information from the API\n")
            sys.exit(1)

    def get_authentication(self):
        return configuration.get_authentication(self.config)

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
