import json
from . import Cmd
from .. import configuration
from ..format import get_formatters
from ..configuration import get_status_names, get_status_flags

class ListCommand(Cmd):
    cmd = 'list'
    formatter = 'output.stdout'

    def run(self, args):
        config = self.tool.config
        if 'auth' in config and 'pass' in config['auth']:
            config['auth']['pass'] = 'PASSWORD'
        return json.dumps(config, indent=4)

class SourcesCommand(Cmd):
    cmd = 'sources'
    formatter = 'output.lines'

    def run(self, args):
        return configuration.find_configuration_file()

class FormattersCommand(Cmd):
    cmd = 'formatters'
    formatter = 'output.lines'

    def run(self, args):
        return get_formatters()
