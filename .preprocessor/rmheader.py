#!/usr/bin/env python

import json
import sys

def rmheader(content: str):
    '''
    Remove the header from the markdown file.
    '''
    if content.startswith('---'):
        content = content.split('---', 2)
        if len(content) >= 3:
            return content[2]

    return content

def recurse(content: dict):
    '''
    Recurse through the content dictionary and remove the header.
    '''
    for key, value in content.items():
        if isinstance(value, dict):
            recurse(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    recurse(item)
        elif isinstance(value, str):
            if key == 'content':
                content[key] = rmheader(value)

if __name__ == '__main__':
    if len(sys.argv) > 1: # we check if we received any argument
        if sys.argv[1] == "supports": 
            # then we are good to return an exit status code of 0, since the other argument will just be the renderer's name
            sys.exit(0)

    # load both the context and the book representations from stdin
    context, book = json.load(sys.stdin)
    # and now, we can just modify the content of the first chapter
    recurse(book)
    # we are done with the book's modification, we can just print it to stdout, 
    print(json.dumps(book))
