#!/usr/bin/env python

import sys
sys.path.append('../')

from sauceboat import Recipe, echo, run_recipe
from csv import DictReader
import re

class Grep(object):
    def __init__(self, *needles):
        self.needles = []

        for needle in needles:
            self.needles.append(re.compile(needle, re.IGNORECASE))

    def __call__(self, source):
        for record in source:
            data = str(record)

            for needle in self.needles:
                if needle.search(data):
                    yield record
                    break

recipe = \
    Recipe( DictReader(open('capitals.csv'), delimiter=';'), Grep(r'.*france.*', r'.*french.*'), echo
          , name='france-related'
          )

if __name__ == '__main__':
    run_recipe(recipe)
