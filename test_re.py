import re, sys

if len(sys.argv) < 2:
    sys.argv.append('vulgar.re')

exp = open(sys.argv[1]).readlines()[1].strip()
print(exp)
pat = re.compile(exp)
print(pat)

while True:
    txt = input('> ')
    print(f'Query: {txt!r}')
    mt = pat.search(txt)
    print(f'Result: {mt!r}')
    if mt:
        print(f'Profanity found: "{mt.group()}" matching index {mt.lastindex}.')
    else:
        print('Clean.')
