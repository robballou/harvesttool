# HarvestTool

Harvest CLI tool.

## Usage

```
# output today's time
harvesttool
```

## Install

Tested in Python 3 but may work in Python 2.

Clone this repository, then:

```
pip install -r requirements.txt
```

Then run one of the following:

1. Add a symlink: `pushd /usr/local/bin && ln -s PATH/harvesttool.py harvesttool && popd`
1. Alternatively, you can add an alias: `alias harvesttool="python PATH/harvesttool.py"`

### Configuration

The configuration can be one of the following:

* `~/.harvest/config.json`
* `~/.harvest.json`
* `~/.harvest.yml`

Configuration should be structured roughly like:

```yaml
auth:
  user: jane
  pass: some_password
host: example
```

This file should be restricted to `0600`.

## Commands

### timesheet

* `timesheet.today`: output today's time
* `timesheet.billable`: output today's billable time
* `timesheet.total`: output today's total time
