#!/usr/bin/python

'''
coloredlogcat
Colored and Indented adb (Android Debugging) Output


ARGUMENTS:
 -l <logLevel>         - number - 0 (all) to 4 (errors only)
 -g <grepPattern>      - string - (Regex not supported)
 -t <trailingLines>    - number - Number of lines after grepPattern match to display (use 99 to show all lines and just highlight grepPattern)

EXAMPLES:
 - Show full adb logcat with color and formatting:
       $ ./coloredlogcat.py
 - Only Warnings and Errors
       $ ./coloredlogcat.py -l3
 - Only show lines containing the word ZEBRA:
       $ ./coloredlogcat.py -gZEBRA
 - Show lines containing the pattern \'MONKEY HAT\' and the next 5 trailing lines
       $ ./coloredlogcat.py -g\'monkey hat\' -t5
 - Show all Info, Warnings and Errors and highlight the word ZEBRA
       $ ./coloredlogcat.py -l2 -g\'ZEBRA\' -t99

'''


import getopt
import fcntl
import os
import re
import StringIO
import struct
import sys
import termios

# unpack the current terminal width/height
data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234')
HEIGHT, WIDTH = struct.unpack('hh', data)

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def format(fg=None, bg=None, bright=False, bold=False, dim=False, reset=False):
    # manually derived from http: //en.wikipedia.org/wiki/ANSI_escape_code#Codes
    codes = []
    if reset:
        codes.append("0")
    else:
        if not fg is None:
            codes.append("3%d" % (fg))
        if not bg is None:
            if not bright:
                codes.append("4%d" % (bg))
            else:
                codes.append("10%d" % (bg))
        if bold:
            codes.append("1")
        elif dim:
            codes.append("2")
        else:
            codes.append("22")
    return "\033[%sm" % (";".join(codes))


def indent_wrap(message, indent=0, width=80):
    wrap_area = width - indent
    messagebuf = StringIO.StringIO()
    current = 0
    while current < len(message):
        next = min(current + wrap_area, len(message))
        messagebuf.write(message[current: next])
        if next < len(message):
            messagebuf.write("\n%s" % (" " * indent))
        current = next
    return messagebuf.getvalue()


LAST_USED = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]
KNOWN_TAGS = {
    "dalvikvm": BLUE,
    "Process": BLUE,
    "ActivityManager": CYAN,
    "ActivityThread": CYAN,
}


def allocate_color(tag):
    # this will allocate a unique format for the given tag
    # since we dont have very many colors, we always keep track of the LRU
    if not tag in KNOWN_TAGS:
        KNOWN_TAGS[tag] = LAST_USED[0]
    color = KNOWN_TAGS[tag]
    LAST_USED.remove(color)
    LAST_USED.append(color)
    return color


RULES = {
    #re.compile(r"([\w\.@]+)=([\w\.@]+)"): r"%s\1%s=%s\2%s" % (format(fg=BLUE), format(fg=GREEN), format(fg=BLUE), format(reset=True)),
}

TAGTYPE_WIDTH = 3
TAG_WIDTH = 20
PROCESS_WIDTH = 8  # 8 or -1
HEADER_SIZE = TAGTYPE_WIDTH + 1 + TAG_WIDTH + 1 + PROCESS_WIDTH + 1

TAGTYPE_LOG_LEVELS = {
    "V": 0, "D": 1, "I": 2, "W": 3, "E": 4
}

TAGTYPES = {
    "V": "%s%s%s " % (format(fg=WHITE, bg=BLACK), "V".center(TAGTYPE_WIDTH), format(reset=True)),
    "D": "%s%s%s " % (format(fg=BLACK, bg=BLUE), "D".center(TAGTYPE_WIDTH), format(reset=True)),
    "I": "%s%s%s " % (format(fg=BLACK, bg=GREEN), "I".center(TAGTYPE_WIDTH), format(reset=True)),
    "W": "%s%s%s " % (format(fg=BLACK, bg=YELLOW), "W".center(TAGTYPE_WIDTH), format(reset=True)),
    "E": "%s%s%s " % (format(fg=BLACK, bg=RED), "E".center(TAGTYPE_WIDTH), format(reset=True)),
}

retag = re.compile("^([A-Z])/([^\(]+)\(([^\)]+)\): (.*)$")

HELP_MESSAGE = "\n".join([
    '\ncoloredlogcat.py',
    'Colored and Indented adb (Android Debugging) Output',
    '\n',
    'ARGUMENTS:',
    ' -l <logLevel>         - number - 0 (all) to 4 (errors only)',
    ' -g <grepPattern>      - string - (Regex not supported)',
    ' -t <trailingLines>    - number - Number of lines after grepPattern match to display (use 99 to show all lines and just highlight grepPattern'
    '\n',
    'EXAMPLES:',
    ' - Show full adb logcat with color and formatting:',
    '       $ ./coloredlogcat.py',
    ' - Only Warnings and Errors',
    '       $ ./coloredlogcat.py -l3',
    ' - Only show lines containing the word ZEBRA:',
    '       $ ./coloredlogcat.py -gZEBRA',
    ' - Show lines containing the pattern \'MONKEY HAT\' and the next 5 trailing lines',
    '       $ ./coloredlogcat.py -g\'monkey hat\' -t5',
    ' - Show all Info, Warnings and Errors and highlight the word ZEBRA',
    '       $ ./coloredlogcat.py -l2 -g\'ZEBRA\' -t99',
    '\n'
])

__doc__

# get args

log_level = -1
grep_pattern = None
grep_trailing_lines = 0
try:
    opts, args = getopt.getopt(sys.argv[1:],"hl:g:t:")
except getopt.GetoptError:
    print __doc__
    sys.exit(2)
opts, args = getopt.getopt(sys.argv[1:],"hl:g:t:",)
for opt, arg in opts:
    if opt in ("-h", "--help","-?"):
        print __doc__
        sys.exit()
    if opt in ("-l"):
        log_level = int(arg)
    if opt in ("-g"):
        grep_pattern = arg
    if opt in ("-t"):
        if not grep_pattern:
            print "Error: -g (grepPattern) is required if -t (trailingLines) argument is used."
            sys.exit()
        grep_trailing_lines = int(arg)

print 'log_level is "', log_level
print 'grep_pattern is "', grep_pattern
print 'grep_trailing_lines is "', grep_trailing_lines

#sys.exit()

# invoke adb logcat
input = os.popen("adb logcat")

def iFind(string, searchPattern):
    return string.lower().find(searchPattern.lower())

grep_trailing_counter = grep_trailing_lines+1
while True:
    try:
        line = input.readline()
    except KeyboardInterrupt:
        break

    match = retag.match(line)
    if not match is None:
        tagtype, tag, owner, message = match.groups()

        linebuf = StringIO.StringIO()

        # center process info
        if PROCESS_WIDTH > 0:
            owner = owner.strip().center(PROCESS_WIDTH)
            linebuf.write("%s%s%s " % (format(fg=BLACK, bg=BLACK, bright=True), owner, format(reset=True)))

        # right-align tag title and allocate color if needed
        tag = tag.strip()
        color = allocate_color(tag)
        tag = tag[-TAG_WIDTH:].rjust(TAG_WIDTH)
        linebuf.write("%s%s %s" % (format(fg=color, dim=False), tag, format(reset=True)))

        # write out tagtype colored edge
        if not tagtype in TAGTYPES:
            break
        linebuf.write(TAGTYPES[tagtype])

        # insert line wrapping as needed
        message = indent_wrap(message, HEADER_SIZE, WIDTH)

        # format tag message using rules
        for matcher in RULES:
            replace = RULES[matcher]
            message = matcher.sub(replace, message)

        # Apply grep and log level filter
        filter_match = False
        if grep_pattern:
            if line.lower().find(grep_pattern.lower()) > -1:
                if log_level==-1 or log_level <= TAGTYPE_LOG_LEVELS[tagtype]:
                    grep_trailing_counter = 0
                    filter_match = True
                    if iFind(message,grep_pattern) > -1:
                        matchStart = iFind(message,grep_pattern)
                        matchEnd = matchStart + len(grep_pattern)
                        linebuf.write(message[:matchStart])
                        linebuf.write("%s%s%s" % (format(fg=YELLOW, dim=False),
                            message[matchStart:matchEnd],
                            format(reset=True))
                        )
                        linebuf.write(message[matchEnd:])
                    else:
                        linebuf.write(message)
            if not filter_match:
                linebuf.write(message)
        else:
            linebuf.write(message)
            if log_level > -1:
                if log_level <= TAGTYPE_LOG_LEVELS[tagtype]:
                    filter_match = True
            else:
                filter_match = True
        grep_trailing_counter += 1
        if not filter_match:
            if grep_trailing_lines<99 and grep_trailing_counter > grep_trailing_lines+1:
                continue

        line = linebuf.getvalue()


    print line
    #if len(line) == 0: break