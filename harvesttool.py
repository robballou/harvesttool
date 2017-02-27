#!/usr/bin/env python
import argparse
from harvesttool import HarvestTool
from harvesttool import commands

if __name__ == '__main__':
    tool = HarvestTool()

    parser = argparse.ArgumentParser(description='Time tracking with Harvest')
    parser.add_argument('--config', '-c', default=None, help='Specify the configuration file that contains authentication')
    parser.add_argument('--formatter', '-f', help='Output formatter', default=None)
    parser.add_argument('--json', help='Output in JSON. Same as --formatter=json.basic', action='store_true')
    parser.add_argument('--yaml', help='Output in YAML. Same as --formatter=yaml.basic', action='store_true')
    subparser = parser.add_subparsers()

    commands.configure_commands(tool, subparser)

    args = parser.parse_args()
    if 'cmd' not in args:
        args.cmd = 'timesheet.today'

    tool.run(args)
