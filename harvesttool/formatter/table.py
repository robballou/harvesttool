from prettytable import PrettyTable

def truncate(thing, length, suffix='...'):
    if len(thing) <= length:
        return thing
    return ' '.join(thing[:length+1].split(' ')[0:-1]) + suffix

def table_basic(conf, args, rows):
    if not rows:
        return
    headers = ['ID', 'Summary', 'Status', 'Link']
    real_rows = []
    table = PrettyTable(headers)
    table.align['ID'] = 'l'
    table.align['Summary'] = 'l'

    if 'truncate' not in args:
        args.truncate = 42

    for row in rows:
        this_row = [row.key, truncate(row.fields.summary, args.truncate), "%s" % row.fields.status, '%sbrowse/%s' % (conf['auth']['url'], row.key)]
        table.add_row(this_row)
    print(table)

def custom(conf, args, rows):
    table_headers = args.headers

    table = PrettyTable(table_headers)
    if 'align' in args:
        for key in args.align:
            table.align[key] = args.align[key]
    for row in rows:
        this_row = []
        for key in args.row_keys:
            this_row.append(row[key])
        table.add_row(this_row)
    print(table)

def grid(conf, args, rows):
    table = PrettyTable([])
    table.header = False
    for thing in rows:
        table.add_row([thing, rows[thing]])
    print(table)

def multiday_grid(conf, args, rows):
    headers = ['']
    for row in rows:
        headers.append(row['date'])
    row_headers = [key for key in rows[0].keys() if key != 'date']

    table = PrettyTable(headers)
    index = 0

    all_rows = []
    for row_header in row_headers:
        all_rows.append([row_header])

    for record in rows:
        row_index = 0
        for key in record.keys():
            if key == 'date':
                continue
            all_rows[row_index].append(record[key])
            row_index = row_index + 1
        index = index + 1

    for row in all_rows:
        table.add_row(row)

    # for row in rows:
    #     this_row = []
    #
    #     this_row.append(row_headers[index])
    #     row_index = 0
    #     for thing in row:
    #         if thing == 'date':
    #             continue
    #         if row_index == index:
    #             this_row.append(row[thing])
    #         row_index = row_index + 1
    #     index = index + 1
    #     table.add_row(this_row)
    print(table)
