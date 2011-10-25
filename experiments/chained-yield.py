#!/usr/bin/env python

def a():
    print 'a(): Generating 65'
    yield 65

    print 'a(): Generating 66'
    yield 66

    print 'a(): Generating 67'
    yield 67

def b(source):
    for item in source:
        print 'b(): Converting', item
        yield chr(item)

def c(source):
    for item in source:
        print 'c(): Got', item

c(b(a()))
