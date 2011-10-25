#!/usr/bin/env python

def a():
    print 'a(): Generating 65'
    yield 65

    print 'a(): Generating 67'
    yield 67

    print 'a(): Generating 66'
    yield 66

def b(source):
    for item in source:
        print 'b(): Converting', item
        yield chr(item)

def c(source):
    max_item = None

    for item in source:
        print 'c(): Got', item

        if max_item is None:
            max_item = item
        else:
            if item > max_item:
                max_item = item

    print 'c(): Found max value', max_item
    yield max_item

def d(source):
    for item in source:
        print 'd(): Got', item

d(c(b(a())))
