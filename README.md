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
       
       
ATTRIBUTION:
This library was derived from Jeff Sharkey's coloredlogcat module:
http://jsharkey.org/blog/2009/04/22/modifying-the-android-logcat-stream-for-full-color-debugging/

License Text for that module follows:

    Copyright 2009, The Android Open Source Project

    Licensed under the Apache License, Version 2.0 (the "License"); 
    you may not use this file except in compliance with the License. 
    You may obtain a copy of the License at 

        http://www.apache.org/licenses/LICENSE-2.0 

    Unless required by applicable law or agreed to in writing, software 
    distributed under the License is distributed on an "AS IS" BASIS, 
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
    See the License for the specific language governing permissions and 
    limitations under the License.