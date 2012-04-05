#!/usr/bin/env python

import sys
sys.path.append('../')

from sauceboat import Recipe, echo, run_recipe
from csv import DictReader


def cleanup(source):
    for record in source:
        yield {'Population': int(record['Population']),
                'Capital': record['Capital']}


def find_min_and_max(source):
    max_record = None
    min_record = None

    for record in source:
        if not max_record and not min_record:
            max_record = record
            min_record = record
        else:
            if record['Population'] > max_record['Population']:
                max_record = record
            if record['Population'] < max_record['Population']:
                min_record = record

    yield min_record
    yield max_record


recipe = \
    Recipe(DictReader(open('capitals.csv'),
        delimiter=';'),
        cleanup,
        find_min_and_max, echo,
        name='max-population')


if __name__ == '__main__':
    run_recipe(recipe)
