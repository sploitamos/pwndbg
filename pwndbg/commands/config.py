#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dumps all pwndbg-specific configuration points.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse

import pwndbg.commands
import pwndbg.config
from pwndbg.color import light_yellow
from pwndbg.color import ljust_colored
from pwndbg.color import strip


def print_row(name, value, default, docstring, ljust_optname, ljust_value, empty_space=6):
    name = ljust_colored(name, ljust_optname + empty_space)
    defval = extend_value_with_default(value, default)
    defval = ljust_colored(defval, ljust_value + empty_space)
    result = ' '.join((name, defval, docstring))
    print(result)
    return result


def extend_value_with_default(value, default):
    if strip(value) != strip(default):
        return '%s (%s)' % (value, default)
    return value


config_parser = argparse.ArgumentParser(description='Shows pwndbg-specific configuration points')


@pwndbg.commands.ArgparsedCommand(config_parser)
def config():
    values = [v for k, v in pwndbg.config.__dict__.items()
              if isinstance(v, pwndbg.config.Parameter) and v.scope == 'config']
    longest_optname = max(map(len, [v.optname for v in values]))
    longest_value = max(map(len, [extend_value_with_default(repr(v.value), repr(v.default)) for v in values]))

    header = print_row('Name', 'Value', 'Def', 'Documentation', longest_optname, longest_value)
    print('-' * (len(header)))

    for v in sorted(values):
        print_row(v.optname, repr(v.value), repr(v.default), v.docstring, longest_optname, longest_value)

    print(light_yellow('You can set config variable with `set <config-var> <value>`'))
    print(light_yellow('You can generate configuration file using `configfile` '
                       '- then put it in your .gdbinit after initializing pwndbg'))


configfile_parser = argparse.ArgumentParser(description='Generates a configuration file for the current Pwndbg options')
configfile_parser.add_argument('--show-all', action='store_true', help='Force displaying of all configs.')


@pwndbg.commands.ArgparsedCommand(configfile_parser)
def configfile(show_all=False):
    configfile_print_scope('config', show_all)


themefile_parser = argparse.ArgumentParser(
    description='Generates a configuration file for the current Pwndbg theme options'
)
themefile_parser.add_argument('--show-all', action='store_true', help='Force displaying of all theme options.')


@pwndbg.commands.ArgparsedCommand(themefile_parser)
def themefile(show_all=False):
    configfile_print_scope('theme', show_all)


def configfile_print_scope(scope, show_all=False):
    params = pwndbg.config.get_params(scope)

    if not show_all:
        params = list(filter(lambda p: p.is_changed, params))

    if params:
        if not show_all:
            print(light_yellow('Showing only changed values:'))
        for p in params:
            print('# %s: %s' % (p.optname, p.docstring))
            print('# default: %s' % p.native_default)
            print('set %s %s' % (p.optname, p.native_value))
            print()
    else:
        print(light_yellow('No changed values. To see current values use `%s`.' % scope))
