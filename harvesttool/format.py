from . import formatter

def get_requested_formatter(args, requested_format = None):
    if 'formatter' in args and args.formatter:
        requested_format = args.formatter
    if 'json' in args and args.json:
        requested_format = 'json.basic'
    if 'yaml' in args and args.yaml:
        requested_format = 'yaml.basic'
    return requested_format

def get_formatter(conf, args, requested_format = None):
    requested_format = get_requested_formatter(args, requested_format)
    if requested_format:
        (mod, mod_formatter) = requested_format.split('.')
        return getattr(formatter.formatters[mod], mod_formatter)
    return formatter.formatters['table'].table_basic

def get_formatters():
    formatters = []
    for output in formatter.formatters:
        formatter_items = dir(formatter.formatters[output])
        for item in formatter_items:
            if item[0] == '_':
                continue
            this_item = getattr(formatter.formatters[output], item)
            if callable(this_item):
                formatters.append("%s.%s" % (output, item))
    return formatters
