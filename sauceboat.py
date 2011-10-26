#!/usr/bin/env python

# Copyright 2011 Almacom (Thailand) Ltd. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
# 
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY ALMACOM (THAIALND) LTD. ''AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL ALMACOM (THAIALND) LTD. OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Almacom (Thailand) Ltd.

# XXX Add documentation and more examples

import sys, time, re

__version__ = '0.1'
__all__ = ['Options', 'options', 'StopProcessing', 'ProcessingError', 'echo', 'run_recipe']

def now():
    return time.time()
def humanize(string):
    string = string.replace('_', ' ')

    string = re.sub(r'^([A-Z]{2,})(?=[A-Z][a-z])', r' \1', string)
    string = re.sub(r'(?!^)([A-Z]{2,})(?=[A-Z][a-z])', r' \1', string)
    string = re.sub(r'([A-Z][a-z])', r' \1', string)

    string = re.sub(r'\s+', ' ', string)

    return string.strip()

class Options(object):
    def __init__(self, options):
        self.options = options.copy()
        self.operands = []
        self.values = {}
    def __getitem__(self, name):
        name = name.replace('_', '-')

        if name in self.values:
            return self.values[name]
        else:
            return self.options[name][0]
    def __getattr__(self, name):
        name = name.replace('_', '-')

        if name in self.values:
            return self.values[name]
        else:
            return self.options[name][0]

    def add(self, options):
        self.options.update(options.copy())
    def parse(self, arguments):
        for arg in arguments:
            if not arg.startswith('--'):
                self.operands.append(arg)
                continue

            if '=' in arg:
                key, value = arg.split('=')
            else:
                key = arg
                value = True

            key = key.lstrip('-')

            try:
                self.values[key] = self.options[key][1](value)
            except:
                raise Exception('Error: unknown argument: %s' % arg)
    def usage(self, fh, name, recipes=None, long_version=True):
        print >>fh, 'Usage: %s [OPTIONS] [RECIPE...]' % name
        print >>fh, ''

        if recipes:
            print >>fh, 'Recipes:'
            print >>fh, ''
            print >>fh, '   ', ', '.join([r.name for r in recipes])
            print >>fh, ''

        print >>fh, 'Arguments:'

        keys = self.options.keys()
        keys.sort()

        for key in keys:
            default, function, message = self.options[key]

            print >>fh, ''

            if type(default) is bool:
                print >>fh, '    --%s' % key
            else:
                print >>fh, '    --%s=%s (Default: %s)' % (key, function.__name__.upper(), default)

            if message:
                print >>fh, '        %s' % message

    @classmethod
    def boolean(cls, value):
        return bool(value)
    @classmethod
    def string(cls, value):
        return unicode(value)
    @classmethod
    def integer(cls, value):
        return int(value)

options = Options( \
    { 'help': (False, Options.boolean, 'Display this help message')
    , 'version': (False, Options.boolean, 'Display the version of sauceboat')
    #, 'info': (False, Options.boolean, 'Display information about the receipe')
    })

class StopProcessing(Exception):
    pass

class ProcessingError(object):
    pass

class Recipe(object):
    def __init__(self, *steps, **kwargs):
        self.name = None
        self.steps = steps

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self):
        logfile = open('%s-%s.log' % (self.name, now()), 'w')

        def middleware(source, name):
            for record in source:
                if issubclass(ProcessingError, type(record)):
                    print >>logfile, now(), self.name, name, 'error'
                    continue

                print >>logfile, now(), self.name, name, 'ok'

                yield record

        source = None

        try:
            print >>logfile, now(), self.name, 'start'

            for step in self.steps:
                if hasattr(step, 'setup'):
                    step.setup(self)

                name = 'Unknown <%s>' % id(step)

                if hasattr(step, '__name__'):
                    name = step.__name__
                elif hasattr(step, '__class__'):
                    name = step.__class__.__name__

                if callable(step):
                    source = middleware(step(source), name)
                else:
                    source = middleware(step, name)

            for record in source:
                yield record
        except StopProcessing, e:
            print >>sys.stderr, e
            print e
        finally:
            print >>logfile, self.name, now(), 'stop'
            logfile.close()

def echo(source):
    for record in source:
        print record
        yield record

def run_recipe(*args):
    global options

    recipes = {}
    for recipe in args:
        if not recipe.name:
            sys.stderr.write('Error: recipe no. %s has no name\n' % recipes.index(recipe) + 1)
            sys.exit(1)

        if recipe.name in recipes:
            sys.stderr.write('Error: name %s is being used by another recipe\n' % recipes.name)
            sys.exit(1)

        recipes[recipe.name] = recipe

    try:
        options.parse(sys.argv[1:])
    except Exception, e:
        sys.stderr.write(u'%s\n' % str(e))
        options.usage(sys.stderr, sys.argv[0], recipes.values(), False)
        sys.exit(1)

    if options.version:
        sys.stdout.write('%s\n' % __version__)
    elif options.help or not options.operands:
        options.usage(sys.stdout, sys.argv[0], recipes.values())
    else:
        for operand in options.operands:
            if operand not in recipes:
                sys.stderr.write('Error: recipe %s does not exist\n' % operand)
                sys.exit(1)

            for record in recipes[operand]():
                pass

    sys.exit(0)
