coloredlogcat
=============

Android Debug Colored Logcat with limited grep and log level filtering


ARGUMENTS:
 -h                   - Print Help
 -l<logLevel>         - NUMBER - 0 (all) to 4 (errors only)
 -g<grepPattern>      - STRING - (Regex not supported)
 -t<trailingLines>    - NUMBER - Number of lines after grepPattern match to display (use 99 to show all lines and just highlight grepPattern)
 -i                   - Case Insensitive grep

EXAMPLES:
 - Show full adb logcat with color and formatting:
       $ ./coloredlogcat.py
 - Only Warnings and Errors
       $ ./coloredlogcat.py -l3
 - Only show lines containing the word ZEBRA:
       $ ./coloredlogcat.py -gZEBRA
 - Only show lines containing the word ZEBRA, zebra, Zebra etc:
       $ ./coloredlogcat.py -gZEBRA -i
 - Show lines containing the pattern \'MONKEY HAT\' and the next 5 trailing lines
       $ ./coloredlogcat.py -g\'monkey hat\' -t5
 - Show all Info, Warnings and Errors and highlight the word ZEBRA
       $ ./coloredlogcat.py -l2 -g\'ZEBRA\' -t99