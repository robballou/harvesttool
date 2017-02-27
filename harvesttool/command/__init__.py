from os.path import dirname, basename, isfile
import glob
import importlib
import sys

from .. import format

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]

class Cmd(object):
    formatter = None

    @classmethod
    def configure(cls, conf, subparser):
        pass

    def __init__(self, tool):
        self.tool = tool

    def error_message(self, message):
        sys.stderr.write("%s\n" % message)

    def get_project(self, args):
        if 'project' in args and args.project:
            if isinstance(args.project, str):
                args.project = (args.project,)
            return args.project
        if 'project' in self.tool.config:
            if isinstance(self.tool.config['project'], str):
                self.tool.config['project'] = (self.tool.config['project'],)
            return self.tool.config['project']
        return False

    def has_option(self, args, option):
        if 'options' not in self.tool.config or args.cmd not in self.tool.config['options']:
            return None
        if option not in self.tool.config['options'][args.cmd]:
            return None
        return self.tool.config['options'][args.cmd][option]

    def has_options(self, args):
        if 'options' in self.tool.config and args.cmd in self.tool.config['options']:
            return True

    def is_structured_format(self, args):
        if args.json or args.yaml:
            return True
        formatter = format.get_requested_formatter(args)
        if formatter and (formatter.startswith('json.') or formatter.startswith('yaml.')):
            return True
        return False

    def query_projects(self, args, query, project):
        projects_query = Query(joiner='OR')
        for proj in project:
            projects_query.add('project=%s' % proj)
        query.add(projects_query)

    def update_args(self, args):
        if self.has_options(self.tools.config, args):
            for arg in vars(args):
                opt = self.has_option(self.tools.config, args, arg)
                if opt != None:
                    setattr(args, arg, opt)

command = {}
for item in __all__:
    if item[0] != '_':
        command[item] = importlib.import_module(".%s" % item, 'harvesttool.command')
