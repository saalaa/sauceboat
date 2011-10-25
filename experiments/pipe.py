#!/usr/bin/env python

def a():
    yield 1
    yield 2
    yield 3

def b():
    yield 10
    yield 20
    yield 30

pipe(a, b)
