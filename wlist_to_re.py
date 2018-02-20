# Pass a filename as the first argument, or use stdin with no arguments.
# Always writes to stdout. Redirect it to a file. The format is valid for the censor module.

import sys, re

if len(sys.argv) >= 2:
    f = open(sys.argv[1])
else:
    f = sys.stdin

print(f'This file was generated automatically by wlist_to_re.py {("on its unknown input" if f is sys.stdin else "on the file " + sys.argv[1])}. Don\'t edit it by hand, or your changes will be lost when it is run again. Instead, edit the source file and invoke this script again.')
print('(?i)' + '|'.join('(^|\s+)' + re.escape(i.strip()) + '(\s+|$)' for i in f.readlines()))
