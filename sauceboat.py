#!/usr/bin/env python

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
                raise Exception('Error: unexpected operand found: %s' % arg)

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
    def usage(self, fh, name, long_version=True):
        print >>fh, 'Usage: %s [OPTIONS]' % name
        print >>fh, ''
        print >>fh, 'Arguments:'

        for key in self.options.keys():
            default, function, message = self.options[key]

            print >>fh, ''

            if type(default) is bool:
                print >>fh, '    --%s' % key
            else:
                print >>fh, '    --%s=%s (Default: %s)' % (key, function.__name__.upper(), default)

            if long_version:
                print >>fh, '        %s' % message

    def boolean(value):
        return bool(value)
    def string(value):
        return unicode(value)
    def integer(value):
        return int(value)

options = Options( \
    { 'help': (False, Options.boolean, 'Display this help message')
    , 'version': (False, Options.boolean, 'Display the version of sauceboat')
    #, 'info': (False, boolean, 'Display information about the receipe')
    })

class StopProcessing(Exception):
    pass

class ProcessingError(object):
    pass

class Recipe(object):
    def __init__(self, *steps, **kwargs):
        self.name = 'default'
        self.salt = None
        self.options = {}

        self.steps = steps

        for key, value in kwargs.items():
            setattr(self, key, value)

    def prepare_steps(self):
        steps = []

        for step in self.steps[:-1]:
            steps.append(step)

            if self.salt:
                steps.append(self.salt)

        steps.append(self.steps[-1])

        return steps

    def __call__(self):
        logfile = open('%s-%s.log' % (self.name, now()), 'w')

        def middleware(source, name):
            print name

            for record in source:
                if issubclass(ProcessingError, type(record)):
                    print >>logfile, now(), self.name, name, 'error'
                    continue

                print >>logfile, now(), self.name, name, 'ok'

                yield record

        source = None

        try:
            print >>logfile, now(), self.name, 'start'

            for step in self.prepare_steps():
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
    if len(args) > 1:
        for recipe in args:
            if not hasattr(recipe, 'name'):
                sys.stderr.write('Error: recipe no. %s has no name\n' % recipes.index(recipe))

            option_name = 'run-%s' % recipe.name.lower()

            options.add({option_name: (False, boolean, 'Run recipe %s' % recipe.name)})
            recipes[option_name] = recipe

        recipe = None
    else:
        recipe = args[0]

    try:
        options.parse(sys.argv[1:])
    except:
        options.usage(sys.stderr, sys.argv[0])
        sys.exit(1)

    if options.help:
        options.usage(sys.stdout, sys.argv[0])
    elif options.version:
        sys.stdout.write('%s\n' % __version__)
    else:
        if not recipe:
            for name, recipe_ in recipes.items():
                if options[name]:
                    recipe = recipe_
                    break

        if not recipe:
            sys.stderr.write('Error: no recipe to start\n')
            sys.exit(1)
    
        for record in recipe():
            pass

    sys.exit(0)
