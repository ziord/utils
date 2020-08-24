"""
License
---------
:copyright: Copyright (c) 2020 Jeremiah Ikosin (@ziord)
:license: BSD 3 Clause, see LICENSE for more details


Description
-------------
Simple source lines of code utility script for python source files
sloc is based on physical Source Lines of Code,
as opposed to logical Source Lines of Code (Source: tiny0.cc/BQO566)


Limitations
-------------
blank lines are not counted, be it in comments or regular lines
"""

import sys
from switches.switch import switch

mapping = {
    'python':  {
        'single-line-comment': '#',
        'multi-line-comment':   ['"""', "'''"],
    }
}

MULTILINE_COMMENT_START = False
MULTILINE_COMMENT_END = False

SINGLE_LINE_COMMENT = False
MULTILINE_COMMENT_MARKER = 0


def read_file__lazy(file_name):
    return (line.strip() for line in open(file_name))


def clean_lines(lines):
    return (line for line in lines if not line.isspace() and len(line))


def is_single_line_comment(line):
    global SINGLE_LINE_COMMENT
    flag = mapping['python']['single-line-comment']
    b = line.startswith(flag)
    SINGLE_LINE_COMMENT = True if b else False
    return b


def is_multi_line_comment(line):
    global MULTILINE_COMMENT_START, MULTILINE_COMMENT_END
    flag = mapping['python']['multi-line-comment']
    if any(line.startswith(_) for _ in flag):
        if MULTILINE_COMMENT_START:
            MULTILINE_COMMENT_END = True
        else:
            MULTILINE_COMMENT_START = True
        if MULTILINE_COMMENT_END:
            MULTILINE_COMMENT_START = False
            MULTILINE_COMMENT_END = False
        return True
    return True if MULTILINE_COMMENT_START or MULTILINE_COMMENT_END else False


def is_comment(line):
    return (is_single_line_comment(line)
            or
            is_multi_line_comment(line))


def is_regular_line(line):
    return not line.isspace() and not is_comment(line)


def multiline_comment():
    # the closing """ is not counted because MULTILINE_COMMENT_START and MULTILINE_COMMENT_END
    # would have been turned off at the closing of the multiline comment,
    # and since mlc_count uses these flags for counting, this makes mlc_count off by 1
    global mlc_count, MULTILINE_COMMENT_MARKER, multiline_comments
    if MULTILINE_COMMENT_START or MULTILINE_COMMENT_END:
        mlc_count += 1
    else:
        if mlc_count:
            MULTILINE_COMMENT_MARKER += 1
            multiline_comments[MULTILINE_COMMENT_MARKER] = mlc_count + 1
            mlc_count = 0


def single_line_comment():
    if SINGLE_LINE_COMMENT:
        global slc_count
        slc_count += 1


def linecount():
    global line_count, slc_count, mlc_count, multiline_comments
    line_count, slc_count, mlc_count = 0, 0, 0
    multiline_comments = {}


def inc_line_count():
    global line_count
    line_count += 1


def analysis():
    global multiline_comments, line_count, slc_count
    fmt = "%(w)-25s     %(lc)s"
    fmt2 = "{0:<15}     {1:>6}"
    mlc_summ = "MLC,Lines Per Comment"
    mlc_summ_bd = '\n'.join([fmt2.format(count, line_p_count) for count, line_p_count in multiline_comments.items()])
    print(fmt % (dict(w="Single Line Comments:", lc=slc_count)))
    print(fmt % (dict(w="Multiple Line Comments:", lc=len(multiline_comments))))
    print(fmt2.format(*mlc_summ.split(',')))
    print(mlc_summ_bd)
    print()
    print(fmt % ({'w': 'Total Source Lines of Code:', 'lc': line_count}))


def main(file_name):
    linecount()
    for line in clean_lines(read_file__lazy(file_name)):
        with switch(is_regular_line, args=(line,), as_callable=True, fallthrough=True) as s:
            s.case(True, inc_line_count)
            s.case(False, single_line_comment)
            s.case(False, multiline_comment)
            s.c_break()
            s.default(None)
    global slc_count, mlc_count
    mlc_count = mlc_count + 1 if mlc_count else mlc_count
    analysis()


if __name__ == '__main__':
    usage = "python pysloc.py file-name"
    if len(sys.argv) < 2:
        print(usage)
    else:
        fn = sys.argv[1]
        main(fn)

