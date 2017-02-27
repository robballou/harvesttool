from . import command
import subprocess
import sys
import json
from . import exceptions

def configure_commands(conf, subparser):
    commands = get_commands()
    for cmd in commands:
        try:
            this_command_class = get_command_class(cmd)
            this_parser = subparser.add_parser(cmd)
            this_command_class.configure(conf, this_parser)
            this_parser.set_defaults(cmd=cmd)
        except Exception as err:
            sys.stderr.write("Could not configure command: %s (%s): %s\n" % (cmd, this_command_class, err))
            raise err

def get_commands():
    commands = []
    for cmd in command.command:
        items = dir(command.command[cmd])
        for item in items:
            try:
                this_item = getattr(command.command[cmd], item)
                if issubclass(this_item, command.Cmd) and item != 'Cmd':
                    commands.append("%s.%s" % (cmd, this_item.cmd))
            except TypeError:
                pass
            except AttributeError:
                pass
    return commands

def get_command_class(cmd):
    (parent, sub) = cmd.split('.')

    sub = sub.title()
    if '_' in sub:
        sub_pieces = sub.split('_')
        sub = ''.join([piece.title() for piece in sub_pieces])

    command_name = "%sCommand" % sub
    return getattr(command.command[parent], command_name)

def get_command(tool, cmd):
    return get_command_class(cmd)(tool)

def update_args_with_command_options(tool, args):
    if 'options' in tool.config and args.cmd in tool.config['options']:
        for option in tool.config['options'][args.cmd]:
            setattr(args, option, tool.config['options'][args.cmd][option])

def run_command(tool, args):
    commands = get_commands()

    if args.cmd not in commands:
        raise exceptions.HarvestToolException("Command does not exist: %s" % (args.command))

    this_command = get_command(tool, args.cmd)
    update_args_with_command_options(tool, args)
    # if args.debug:
    #     copy = dict(conf)
    #     sys.stderr.write("%s\n" % json.dumps(copy, indent=4))
    #     sys.stderr.write("%s\n" % args)
    results = this_command.run(args)
    if 'no_defaults' in args and not args.no_defaults:
        this_command.update_args(tool, args)

    return (results, this_command.formatter)
