import os
import sys
import json
import yaml
import base64
from collections import OrderedDict
from . import exceptions

def get_authentication(configuration):
    if 'token' in configuration['auth']:
        decoded = base64.b64decode(configuration['auth']['token'])
        return decoded.decode('utf-8').split(':')
    if 'user' in configuration['auth'] and 'pass' in configuration['auth']:
        return (configuration['auth']['user'], configuration['auth']['pass'])

def get_status_names(configuration):
    statuses = configuration['jira'].statuses()
    statuses = [status.name for status in statuses]
    statuses.sort()
    return statuses

def get_status_flags(configuration):
    statuses = configuration['jira'].statuses()
    statuses = sorted(statuses, key=lambda status: status.name)
    status_map = OrderedDict()
    for status in statuses:
        flag = status.name.lower()
        flag = flag.replace(' ', '-')
        flag = flag.replace('.', '')
        count = 1
        while flag in status_map:
            temp_flag = "%s%d" % (flag, count)
            if temp_flag not in status_map:
                flag = temp_flag
            count += 1
        status_map[flag] = status
    return status_map

def get_status_name_from_flag(configuration, flag):
    flags = get_status_flags(configuration)
    if flag in flags:
        return flags[flag]
    return False

def find_configuration_file(args = None):
    """
    Find all applicable configuration files for this configuration.
    """

    sources = [
        '~/.harvest.json',
        '~/.harvest.yml',
        '~/.harvest/config.json',
    ]

    if args and args.config:
        sources.append(args.config)

    use_sources = []
    for source in sources:
        source_path = os.path.expanduser(source)
        if os.path.exists(source_path) and source_path not in use_sources:
            use_sources.append(source_path)

    cwd = os.getcwd()
    while cwd != '/':
        if os.path.exists(os.path.join(cwd, '.harvest.json')) and os.path.join(cwd, '.harvest.json') not in use_sources:
            use_sources.append(os.path.join(cwd, '.harvest.json'))
        elif os.path.exists(os.path.join(cwd, '.harvest.yml')) and os.path.join(cwd, '.harvest.yml') not in use_sources:
            use_sources.append(os.path.join(cwd, '.harvest.yml'))
        cwd = os.path.dirname(cwd)

    return use_sources

def load():
    """
    Load the configuration
    """

    sources = find_configuration_file()
    if len(sources) == 0:
        raise exceptions.HarvestToolException('Could not locate configuration file')
    configuration = {}
    for source in sources:
        (root, ext) = os.path.splitext(source)
        if ext in ['.json', '.js']:
            with open(source, 'r') as fp:
                this_configuration = json.load(fp)
                if 'auth' in this_configuration:
                    file_details = os.stat(source)
                    if oct(file_details.st_mode)[-3:] != '600':
                        sys.stderr.write("WARNING: The configuration file %s contains authentication information and is not set to safe permissions: %s\n" % (source, oct(file_details.st_mode)[-3:]))
                configuration = merge_configurations(configuration, this_configuration)
        elif ext in ['.yml', '.yaml']:
            with open(source, 'r') as fp:
                this_configuration = yaml.load(fp)
                if 'auth' in this_configuration:
                    file_details = os.stat(source)
                    if oct(file_details.st_mode)[-3:] != '600':
                        sys.stderr.write("WARNING: The configuration file %s contains authentication information and is not set to safe permissions: %s\n" % (source, oct(file_details.st_mode)[-3:]))
                configuration = merge_configurations(configuration, this_configuration)

    default_configuration = {
    }

    configuration = merge_configurations(configuration, default_configuration)
    return configuration

def merge_configurations(a, b, path=None):
    """
    Merge two configuration objects.

    From http://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge/7205107#7205107
    """

    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_configurations(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a
