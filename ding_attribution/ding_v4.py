#!/usr/bin/env python
# -*- coding: utf-8 -*-


# This code allows to extract Ding et al. features  (described in Burrows et al. study https://onlinelibrary.wiley.com/doi/abs/10.1002/spe.2146) from source code files using earlier parsed files from step 2.1.
# This source code should be located in the same folder as *.java, *.txt, *.com files.
# The main output is results.arff file, which contains Ding et al. feature vectors.

# The input are java files. The names of java files should have the following pattern, such as
# “a_____N10001.java”, where “a” is a file name, N10001 is an author. For example an author N10001 can have 4 files:
# “a_____N10001.java”, “b_____N10001.java”, “c_____N10001.java”, “d_____N10001.java”.


import re
import os
import os.path
import io
import sys


# ==============================================================================
# from original file
def numericalSort(value):
    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def gcd(a, b):
    if (b == 0):
        return a
    else:
        return gcd(b, a % b)


def get_lcm_for(your_list):
    return reduce(lambda x, y: gcd(x, y), your_list)


# ==============================================================================

def lcount(keyword, list_of_lines):
    count = 0
    for line in list_of_lines:
        if (keyword in line):
            count = count + 1
    return (count)


def ccount(keychar, list_of_lines):
    count = 0
    for line in list_of_lines:
        for xchar in line:
            if (xchar == keychar):
                count = count + 1
    return (count)


def absoluteFilePaths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def file_lines(fname):
    # UnicodeDecodeError: 'utf8' codec can't decode byte 0xce in position 601: invalid continuation byte
    with io.open(fname, "r", encoding='utf-8', errors='ignore') as f:
        for i, l in enumerate(f):
            pass
    return i + 1


# ==============================================================================
# ==============================================================================
# ==============================================================================


# parse ALL
main_directory = str(sys.argv[-1])
print(main_directory)

error_file = main_directory + "_ding_errors.txt"
result_file = main_directory + '_ding_results.arff'
separator = "/"

if os.path.exists(result_file):
    os.remove(result_file)
if os.path.exists(error_file):
    os.remove(error_file)
all_files = absoluteFilePaths(main_directory)

java_files = list()
for item in all_files:
    if not ("/._" in item):
        if item.endswith(".java"):
            if not (item in java_files):
                java_files.append(item)
java_files.sort()

for java_file in java_files:

    bad_file = False
    NCLOC = 0
    # print(java_file)

    # get number of lines
    line_num = file_lines(java_file)

    # print(line_num)

    # FROM JAVA FILE, get all lines with LATIN-1 encoding
    all_lines_latin1 = list()
    with io.open(java_file, 'r', encoding="latin-1") as rfl:
        for line in rfl:
            all_lines_latin1.append(line)

    com_file = str(java_file)[:-5] + ".com"
    if not os.path.isfile(com_file):
        bad_file = True
        with io.open(error_file, 'a') as waf:
            waf.write("**** ERROR " + str(java_file) + " \n")
            waf.write("Missing " + com_file + " \n")
    if bad_file:
        continue

    txt_file = str(java_file)[:-5] + ".txt"
    if not os.path.isfile(txt_file):
        bad_file = True
        with io.open(error_file, 'a') as waf:
            waf.write("**** ERROR " + str(java_file) + " \n")
            waf.write("Missing " + txt_file + " \n")
    if bad_file:
        continue

    # FROM COM FILE, get all lines
    all_lines_nocomments = list()
    with io.open(com_file, 'r', encoding='utf-8', errors='ignore') as rfl:
        try:
            for line in rfl:
                all_lines_nocomments.append(line)
                # Save number of java line that are not comment and not empty
                if line.strip():
                    NCLOC += 1

        except Exception as e:
            bad_file = True
            print(java_file)
            print(e)
            with io.open(error_file, 'a') as waf:
                waf.write("**** ERROR " + str(java_file) + " UnicodeDecodeError: 'charmap' codec can't decode byte  \n")
                waf.write(str(e) + " \n")
            continue

    # UnicodeDecodeError: 'charmap' codec can't decode byte 0x90 in position 2834: character maps to <undefined>
    # FROM TXT FILE, get all lines
    all_lines_txtparsed = list()
    with io.open(txt_file, 'r', encoding='utf-8', errors='ignore') as rfl:
        try:
            for line in rfl:
                all_lines_txtparsed.append(line)
        except Exception as e:
            bad_file = True
            print(java_file)
            print(e)
            with io.open(error_file, 'a') as waf:
                waf.write("**** ERROR " + str(java_file) + " UnicodeDecodeError: 'charmap' codec can't decode byte \n")
                waf.write(str(e) + " \n")
            continue

    result_list = list()

    s = ''.join(all_lines_latin1)
    count2 = 0
    k1 = re.findall('/\*[\d\D]*?\*/', s, re.MULTILINE)

    new_items = []
    for item in k1:
        new_items.extend(item.split('\n'))

    allc = len(new_items)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k2 = [re.findall('[a-z][a-z0-9\s\S]+/\*[a-z0-9\s\S]+[\*/]*', line)
          for line in all_lines_latin1]
    nn = sum(k2, [])
    commentArr = []
    for i in range(len(nn)):
        if ('*/') not in nn[i]:
            commentArr += [nn[i]]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k3 = [re.findall('^\s*/\*[^\/*]+$', line)
          for line in all_lines_latin1]
    nnn = sum(k3, [])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k4 = [re.findall('^\s*/\*[^\/*]+\*/\s*$', line)
          for line in all_lines_latin1]
    m = sum(k4, [])
    kk = len(m)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k5 = [re.findall('/\*[^\/*]+\*/', line)
          for line in all_lines_latin1]
    m2 = sum(k5, [])
    inl = len(m2)
    inline = inl - kk
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # // comments
    k6 = [re.findall('[\s\S]*//', line)
          for line in all_lines_latin1]
    nn2 = sum(k6, [])
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k7 = [re.findall('^\s*//', line)
          for line in all_lines_latin1]
    nnn2 = sum(k7, [])
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    nnnn = len(nn2) - len(nnn2)

    pure = (allc - len(commentArr) - inline) + len(nnn2)
    inlinecomment = nnnn + len(commentArr) + inline

    # D90

    if pure + inlinecomment == 0:
        string_d90 = '0'
    else:
        l = (pure / (pure + inlinecomment)) * 100
        l = round(l, 3)
        string_d90 = str(l)

    result_list.append("D09:" + string_d90)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    array = []
    for element in all_lines_latin1:
        if '//' in element:
            array.append(element)
    li = len(array)
    a = 0
    for element in all_lines_latin1:
        a = a + element.count('/*')

    if a == 0:
        string_d10 = '0'
    else:
        lii = (li / (li + a)) * 100
        lii = round(lii, 3)
        string_d10 = str(lii)

    result_list.append("D10:" + string_d10)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    non_blank_count = 0

    for line in all_lines_latin1:
        if line.strip():
            non_blank_count += 1

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    blank_lines = line_num - non_blank_count

    percentage_of_blank = (blank_lines / line_num) * 100
    percentage_of_blank = round(percentage_of_blank, 3)

    string_d14 = str(percentage_of_blank)

    result_list.append("D14:" + string_d14)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    if pure + non_blank_count == 0:
        string_d15 = '0'
    else:
        l = (pure / (non_blank_count)) * 100
        l = round(l, 3)
        string_d15 = str(l)

    result_list.append("D15:" + string_d15)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    if non_blank_count == 0 or NCLOC == 0:
        string_d16 = '0'
    else:
        try:
            l = (inlinecomment / NCLOC) * 100
        except Exception as e:
            bad_file = True
            with io.open(error_file, 'a') as waf:
                waf.write("**** ERROR " + str(java_file) + " NCLOC:" + str(NCLOC) + " \n")
                waf.write(str(e) + " \n")
            continue

        l = round(l, 3)
        string_d16 = str(l)

    result_list.append("D16:" + string_d16)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    # D31
    number = 0
    for line in all_lines_latin1:
        if 'class ' in line:
            number = number + 1

    lookup = 'class '
    a = []
    with io.open(java_file, 'r', encoding="latin-1") as myFile:
        for num, line in enumerate(myFile, 1):
            if lookup in line:
                a.append(num)
            else:
                a.append(0)
    b = int(a[0])
    tocheck = 0
    for line in all_lines_latin1:
        if 'class' in line:
            k = [re.findall('^\s*/\*[^\/*]+\*/\s*$', line) for line in all_lines_latin1]
            m = sum(k, [])
            tocheck = len(m)

    for line in all_lines_latin1:
        if 'class' in line:
            k2 = [re.findall('^\s*/\*[^\/*]+$', line) for line in all_lines_latin1]
            nnn = sum(k2, [])

    for line in all_lines_latin1:
        if 'class' in line:
            k = [re.findall('/\*[^\/*]+\*/', line) for line in all_lines_latin1]
            m = sum(k, [])
    inl = len(m)
    inline = inl - tocheck

    for line in all_lines_latin1:
        if 'class' in line:
            k = [re.findall('[a-z][a-z0-9\s\S]+/\*[a-z0-9\s\S]+[\*/]*', line) for line in all_lines_latin1]
            nn = sum(k, [])
    commentArr = []
    for i in range(len(nn)):
        if ('*/') not in nn[i]:
            commentArr += [nn[i]]

    papa = []
    for line in all_lines_latin1:
        if 'class' in line:
            s = ''.join(all_lines_latin1)
            k = re.findall('/\*[\d\D]*?\*/', s, re.MULTILINE)
            papa = []
            for item in k:
                papa.extend(item.split('\n'))
            break
    allc = len(papa)
    pure = (allc - len(commentArr) - inline) + len(nnn)

    if number == 0:
        string_d31 = '0'
    else:
        l = (line_num - b - pure - 1) / number
        l = round(l, 3)
        string_d31 = str(l)

    result_list.append("D31:" + string_d31)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    content = ''.join(all_lines_latin1)
    k = len(content)
    string_d17 = str(k)

    result_list.append("D17:" + string_d17)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    count1 = 0
    for line in all_lines_nocomments:
        for c in line:
            if c == '{':
                count1 = count1 + 1;
    count = 0
    k = [re.findall('^\s*\t*\{\t*\s*$', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    b1 = len(m)

    if count1 == 0:
        string_d01 = '0'
        result_list.append("D01:" + string_d01)
    else:
        aaa1 = (b1 / count1) * 100
        aaa1 = round(aaa1, 3)
        string_d01 = str(aaa1)
        result_list.append("D01:" + string_d01)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    count = 0
    k = [re.findall('^\s*\t*\{\t*\s*[a-zA-Z0-9\S]', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    b1 = len(m)

    if count1 == 0:
        string_d02 = '0'
        result_list.append("D02:" + string_d02)
    else:
        aaa2 = (b1 / count1) * 100
        aaa2 = round(aaa2, 3)
        string_d02 = str(aaa2)
        result_list.append("D02:" + string_d02)

    d = lcount('{', all_lines_nocomments)

    count2 = 0
    k = [re.findall('\t*\s*[a-zA-Z0-9\S]\s*\t*\{', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    b1 = len(m)

    if count1 == 0:
        string_d03 = '0'
        result_list.append("D03:" + string_d03)
    else:
        aaa3 = (b1 / count1) * 100
        aaa3 = round(aaa3, 3)
        string_d03 = str(aaa3)
        result_list.append("D03:" + string_d03)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    count1 = 0
    for line in all_lines_nocomments:
        for c in line:
            if c == '}':
                count1 = count1 + 1;

    count = 0
    k = [re.findall('^\s*\t*\}\t*\s*$', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    b1 = len(m)

    if count1 == 0:
        string_d04 = '0'
        result_list.append("D04:" + string_d04)
    else:
        aaa1 = (b1 / count1) * 100
        aaa1 = round(aaa1, 3)
        string_d04 = str(aaa1)
        result_list.append("D04:" + string_d04)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    count = 0
    k = [re.findall('^\s*\t*\}\t*\s*[a-zA-Z0-9\S]', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    b1 = len(m)

    if count1 == 0:
        string_d05 = '0'
        result_list.append("D05:" + string_d05)
    else:
        aaa2 = (b1 / count1) * 100
        aaa2 = round(aaa2, 3)
        string_d05 = str(aaa2)
        result_list.append("D05:" + string_d05)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    d = lcount('}', all_lines_nocomments)

    count2 = 0
    k = [re.findall('\t*\s*[a-zA-Z0-9\S]\s*\t*\}', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    b1 = len(m)
    str1 = ''.join(m)
    b1 = str1.count('}')

    if count1 == 0:
        string_d06 = '0'
        result_list.append("D06:" + string_d06)
    else:
        aaa3 = (b1 / count1) * 100
        aaa3 = round(aaa3, 3)
        string_d06 = str(aaa3)
        result_list.append("D06:" + string_d06)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    count1 = 0
    for line in all_lines_nocomments:
        for c in line:
            if c == '{':
                count1 = count1 + 1;

    count2 = 0
    k = [re.findall('\{\s+', line)
         for line in all_lines_nocomments]
    m = sum(k, [])

    a = 0
    for element in m:
        a = a + element.count(' ')

    b = 0
    for element in m:
        b = b + element.count('{')

    if a == 0:
        string_d07 = '0'
    else:
        s = a / b
        s = round(s, 3)
        string_d07 = str(s)

    result_list.append("D07:" + string_d07)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    count1 = 0
    for line in all_lines_nocomments:
        for c in line:
            if c == '{':
                count1 = count1 + 1;

    count2 = 0
    k = [re.findall('\{\t+', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    a = 0
    for element in m:
        a = a + element.count('\t')

    b = 0
    for element in m:
        b = b + element.count('{')

    if a == 0:
        string_d08 = '0'
    else:
        s = a / b
        s = round(s, 3)
        string_d08 = str(s)

    result_list.append("D08:" + string_d08)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    count_spaces = ccount(" ", all_lines_nocomments)
    count_tabs = ccount("\t", all_lines_nocomments)

    a = [];
    for line in all_lines_nocomments:
        a.append(len(line) - len(line.lstrip(' ')))

    if sum(a) == 0:
        pass
    else:
        lookup = '{'
        b = []
        for num, line in enumerate(all_lines_nocomments, 1):
            if lookup in line:
                b.append(num - 1)
        k = []
        try:
            for element in b:
                k.append(a[element])
        except Exception as e:
            bad_file = True
            with io.open(error_file, 'a') as waf:
                waf.write("**** ERROR " + str(java_file) + " IndexError: list index out of range \n")
                waf.write("a:" + a)
                waf.write("b:" + b)
                waf.write("k:" + k)
                waf.write(str(e) + " \n")
            continue

        # print('Number of white spaces next line after open braces',k)
        if sum(k) == 0:
            # print('No white spaces after open braces')
            pass
        else:
            at = [x for x in k if x != 0]
            from functools import reduce  # need this line if you're using Python3.x
            def gcd(a, b):
                if (b == 0):
                    return a
                else:
                    return gcd(b, a % b)

                def get_lcm_for(your_list):
                    return reduce(lambda x, y: gcd(x, y), your_list)
                ans = get_lcm_for(at)

    a = [];

    for line in all_lines_nocomments:
        a.append(len(line) - len(line.lstrip('\t')))

    if count_tabs == 0:
        pass
    else:
        lookup = '{'
        b = []
        for num, line in enumerate(all_lines_nocomments, 1):
            if lookup in line:
                b.append(num + 2)

        b = b[:-2]

        k = []
        for element in b:
            k.append(a[element])
        if sum(k) == 0:
            pass
        else:
            at = [x for x in k if x != 0]
            from functools import reduce  # need this line if you're using Python3.x
            def gcd(a, b):
                if (b == 0):
                    return a
                else:
                    return gcd(b, a % b)
            def get_lcm_for(your_list):
                return reduce(lambda x, y: gcd(x, y), your_list)
            ans = get_lcm_for(at)

    count2 = 0
    k = [re.findall('if[\s*\t*](.*).*\;', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    a1 = len(m)

    p = 0
    for line in all_lines_nocomments:
        if 'if' in line:
            p += 1

    if p == 0:
        string_d11 = '0'
    else:
        d = (a1 / p) * 100
        d = round(d, 3)
        string_d11 = str(d)

    result_list.append("D11:" + string_d11)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    count2 = 0
    k = [re.findall('\s+[\+\-\*\/\%\=]', line)
         for line in all_lines_nocomments]
    m = sum(k, [])

    a = [x for x in m if '{\n' not in x]
    str1 = ''.join(a)
    m = len(str1)

    k = m - str1.count(' ')

    if k == 0:
        string_d12 = '0'
    else:
        l = str1.count(' ') / k
        l = round(l, 3)
        string_d12 = str(l)

    result_list.append("D12:" + string_d12)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    count2 = 0
    k = [re.findall('[\+\-\*\/\%\=]\s+', line)
         for line in all_lines_nocomments]
    m = sum(k, [])

    a = [x for x in m if '{\n' not in x]
    str1 = ''.join(a)
    m = len(str1)
    k = m - str1.count(' ')

    if k == 0:
        string_d13 = '0'
    else:
        l = str1.count(' ') / k
        l = round(l, 3)
        string_d13 = str(l)

    result_list.append("D13:" + string_d13)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Variable Declaration Expression Collected:(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    typevar = []
    for element in m:
        if ' = ' in element:
            typevar.append(element.rpartition(' = ')[0])
        else:
            typevar.append(element)

    typevar = list(filter(None, typevar))

    typevar = [element.split() for element in typevar]

    k = [re.findall('Parameter Collected:\s(.*)', line)
         for line in all_lines_txtparsed]

    parameters = sum(k, [])

    newparameters = [element.split() for element in parameters]

    allvar = typevar + newparameters
    lenallvar = len(allvar)

    a = ['short', 'short[]', 'int', 'int[]', 'long', 'float', 'double', 'char', 'char[]', 'String', 'String[]',
         'boolean', 'byte', 'byte[]']

    primandstr_var = []

    for element in allvar:
        for i in range(len(a) - 1):
            if element[0] == a[i]:
                primandstr_var.append(element)
            i = i + 1

    primandstr_var2 = [element[1] for element in primandstr_var]

    g = [bb.replace(" ", "") for bb in primandstr_var2]

    bb1 = ''.join(g)

    k1 = []
    for el in allvar:
        if len(el) == 1:
            k1.append(el[0])
        else:
            k1.append(el[1])

    a = ['short', 'int', 'long', 'float', 'double', 'char', 'boolean', 'byte']

    prim_var = []

    for element in allvar:
        for i in range(len(a) - 1):
            if element[0] == a[i]:
                prim_var.append(element)
            i = i + 1

    if len(primandstr_var) == 0:
        string_d18 = '0'
    else:
        number = round(len(bb1) / len(primandstr_var), 3)
        string_d18 = str(number)

    result_list.append("D18:" + string_d18)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    k = [re.findall('Method Collected:(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])
    g = [bb.replace(" ", "") for bb in m]

    a = [x for x in g if x != 'main']
    bb2 = ''.join(a)

    if len(a) == 0:
        string_d19 = '0'
    else:
        number = round(len(bb2) / len(a), 3)
        string_d19 = str(number)

    result_list.append("D19:" + string_d19)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Class or Interface Collected:(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    a1 = [x for x in g if x != 'main']
    bb3 = ''.join(a)

    whole = k1 + a + a1

    s = []
    i = 0
    while i < len(whole):
        if re.match('^[A-Z].*', whole[i]):
            s.append(whole[i])
        i = i + 1

    if len(whole) == 0:
        string_d20 = '0'
        result_list.append("D20:" + string_d20)
    else:
        number = (len(s) / len(whole)) * 100
        number = round(number, 3)
        string_d20 = str(number)
        result_list.append("D20:" + string_d20)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    s = []
    i = 0
    while i < len(whole):
        if re.match('^[a-z].*', whole[i]):
            s.append(whole[i])
        i = i + 1

    if len(whole) == 0:
        string_d21 = '0'
        result_list.append("D21:" + string_d21)
    else:
        number = (len(s) / len(whole)) * 100
        number = round(number, 3)
        string_d21 = str(number)
        result_list.append("D21:" + string_d21)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    s = []
    i = 0
    while i < len(whole):
        if re.match('(^\_.*)', whole[i]):
            s.append(whole[i])
        i = i + 1

    if len(whole) == 0:
        string_d22 = "0"
        result_list.append("D22:" + string_d22)
    else:
        number = (len(s) / len(whole)) * 100
        number = round(number, 3)
        string_d22 = str(number)
        result_list.append("D22:" + string_d22)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    s = []
    i = 0
    while i < len(whole):
        if re.match('(^\$.*)', whole[i]):
            s.append(whole[i])
        i = i + 1
    if len(whole) == 0:
        string_d23 = "0"
        result_list.append("D23:" + string_d23)
    else:
        number = (len(s) / len(whole)) * 100
        number = round(number, 3)
        string_d23 = str(number)
        result_list.append("D23:" + string_d23)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('While Statement Count:(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]
    try:
        while_num = int(g[0])
    except IndexError:
        while_num = 0

    k = [re.findall('For Statement Count:(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        for_num = int(g[0])
    except IndexError:
        for_num = 0

    k = [re.findall('Do Statement Count:(.*)', line)
         for line in all_lines_txtparsed]

    g = [bb.replace(" ", "") for bb in m]

    try:
        do_num = int(g[0])
    except IndexError:
        do_num = 0

    total = while_num + do_num + for_num

    if total == 0:
        string_d24 = "0"
        result_list.append("D24:" + string_d24)

        string_d25 = "0"
        result_list.append("D25:" + string_d25)

        string_d26 = "0"
        result_list.append("D26:" + string_d26)

    else:
        percwh = (while_num / total) * 100
        percwh = round(percwh, 3)
        string_d24 = str(percwh)
        result_list.append("D24:" + string_d24)

        percfor = (for_num / total) * 100
        percfor = round(percfor, 3)
        string_d25 = str(percfor)
        result_list.append("D25:" + string_d25)

        percdo = (do_num / total) * 100
        percdo = round(percdo, 3)
        string_d26 = str(percdo)
        result_list.append("D26:" + string_d26)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('If Statement Collected:(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    s = ''.join(all_lines_txtparsed)

    k = re.findall("(?s)If Statement Collected:\\s(.*)If Statement Count:", s, re.MULTILINE)

    if k == []:
        else_num = 0;
    else:
        else_num = k[0].count('else')

    k = [re.findall('If Statement Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        if_num = int(g[0])
    except IndexError:
        if_num = 0

    k = [re.findall('Switch Entry Statement Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        case_num = int(g[0])
    except IndexError:
        case_num = 0

    k = [re.findall('Switch Statement Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]
    try:
        switch_num = int(g[0])
    except IndexError:
        switch_num = 0

    totala = if_num + else_num + switch_num + case_num

    if totala == 0:
        string_d27 = "0.000"
        result_list.append("D27:" + string_d27)

        string_d28 = "0.000"
        result_list.append("D28:" + string_d28)

    else:
        n1 = ((if_num + else_num) / totala) * 100
        n1 = round(n1, 3)
        string_d27 = str(n1)
        result_list.append("D27:" + string_d27)

        n2 = ((switch_num + case_num) / totala) * 100
        n2 = round(n2, 3)
        string_d28 = str(n2)
        result_list.append("D28:" + string_d28)

    if if_num + else_num == 0:
        string_d29 = "0.000"
    else:
        n3 = (if_num / (if_num + else_num)) * 100
        n3 = round(n3, 3)
        string_d29 = str(n3)
    result_list.append("D29:" + string_d29)

    if switch_num + case_num == 0:
        string_d30 = "0.000"
    else:
        n4 = (switch_num / (switch_num + case_num)) * 100
        n4 = round(n4, 3)
        string_d30 = str(n4)
    result_list.append("D30:" + string_d30)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Class or Interface Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        class_num = int(g[0])
    except IndexError:
        class_num = 0

    # print('class_num=',class_num)
    # print('Primitive variables=',prim_var)
    # Changed by fari
    if class_num == 0:
        string_d32 = "0.000"
        result_list.append("D32:" + string_d30)
    else:
        # Traceback (most recent call last):
        #  File "ding_v2.py", line 1315, in <module>
        #    n1=len(prim_var)/class_num
        # ZeroDivisionError: integer division or modulo by zero
        try:
            n1 = len(prim_var) / class_num
        except Exception as e:
            bad_file = True
            with io.open(error_file, 'a') as waf:
                waf.write("**** ERROR " + str(java_file) + " \n")
                waf.write(
                    str(e) + "Class or Interface Count:" + " class_num:" + class_num + " prim_var:" + prim_var + "m,g" + m + g + " \n")
            continue

        n1 = len(prim_var) / class_num
        n1 = round(n1, 3)
        string_d32 = str(n1)
        result_list.append("D32:" + string_d32)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Method Collected:(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    a = [x for x in g if x != 'main']
    n1 = len(a)
    n1 = round(n1, 3)
    string_d33 = str(n1)
    result_list.append("D33:" + string_d33)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    # -------------------------------------!do no comments file---

    k = [re.findall('[\t\s\n]+interface ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^interface ', line)
         for line in all_lines_nocomments]

    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]interface ', line)
         for line in all_lines_nocomments]

    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if class_num == 0:
        string_d34 = "0.000"
        result_list.append("D34:" + string_d34)
    else:
        n1 = number3 / class_num
        n1 = round(n1, 3)
        string_d34 = str(n1)
        result_list.append("D34:" + string_d34)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = len(prim_var) / NCLOC
    n1 = round(n1, 3)
    string_d35 = str(n1)
    result_list.append("D35:" + string_d35)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = len(a) / NCLOC
    n1 = round(n1, 3)
    string_d36 = str(n1)
    result_list.append("D36:" + string_d36)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('[\t\s\n]+static ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^static ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]static ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d37 = str(n1)
    result_list.append("D37:" + string_d37)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall(' extends ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number / NCLOC
    n1 = round(n1, 3)
    string_d38 = str(n1)
    result_list.append("D38:" + string_d38)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    k = [re.findall('[\t\s\n]+class ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^class ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])

    number3 = number2 + number

    k = [re.findall('[=({]class ', line)
         for line in all_lines_nocomments]

    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d39 = str(n1)
    result_list.append("D39:" + string_d39)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('[\t\s\n]+abstract ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^abstract ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]abstract ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d40 = str(n1)
    result_list.append("D40:" + string_d40)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    k = [re.findall('[\t\s\n]+implements ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^implements ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]implements ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d41 = str(n1)
    result_list.append("D41:" + string_d41)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    k = [re.findall('Import Declaration Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        import_num = int(g[0])
    except IndexError:
        import_num = 0

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = import_num / NCLOC
    n1 = round(n1, 3)
    string_d42 = str(n1)
    result_list.append("D42:" + string_d42)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Instance Of Expression Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        instanceof_num = int(g[0])
    except IndexError:
        instanceof_num = 0

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = instanceof_num / NCLOC
    n1 = round(n1, 3)
    string_d43 = str(n1)
    result_list.append("D43:" + string_d43)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('[\t\s\n]+interface ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^interface ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]interface ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d44 = str(n1)
    result_list.append("D44:" + string_d44)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('[\t\s\n]+native ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^native ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]native ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d45 = str(n1)
    result_list.append("D45:" + string_d45)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('[\t\s\n]+new ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^new ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]new ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d46 = str(n1)
    result_list.append("D46:" + string_d46)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Package Declaration Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        package_num = int(g[0])
    except IndexError:
        package_num = 0

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = package_num / NCLOC
    n1 = round(n1, 3)
    string_d47 = str(n1)
    result_list.append("D47:" + string_d47)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('[\t\s\n]+private ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^private ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]private ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d48 = str(n1)
    result_list.append("D48:" + string_d48)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('[\t\s\n]+public ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^public ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]public ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d49 = str(n1)
    result_list.append("D49:" + string_d49)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('[\t\s\n]+protected ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^protected ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]protected ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)
    string_d50 = str(n1)
    result_list.append("D50:" + string_d50)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('This Expression Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        this_num = int(g[0])
    except IndexError:
        this_num = 0

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = this_num / NCLOC
    n1 = round(n1, 3)
    string_d51 = str(n1)
    result_list.append("D51:" + string_d51)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Super Expression Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        super_num = int(g[0])
    except IndexError:
        super_num = 0

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = super_num / NCLOC
    n1 = round(n1, 3)
    string_d52 = str(n1)
    result_list.append("D52:" + string_d52)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Try Statement Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        try_num = int(g[0])
    except IndexError:
        try_num = 0
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = try_num / NCLOC
    n1 = round(n1, 3)
    string_d53 = str(n1)
    result_list.append("D53:" + string_d53)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Throw Statement Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        throw_num = int(g[0])
    except IndexError:
        throw_num = 0

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = throw_num / NCLOC
    n1 = round(n1, 3)
    string_d54 = str(n1)
    result_list.append("D54:" + string_d54)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('Catch Clause Count:\s(.*)', line)
         for line in all_lines_txtparsed]

    m = sum(k, [])

    g = [bb.replace(" ", "") for bb in m]

    try:
        catch_num = int(g[0])
    except IndexError:
        catch_num = 0

    if NCLOC == 0:
        n1 = 0
    else:
        n1 = catch_num / NCLOC
    n1 = round(n1, 3)
    string_d55 = str(n1)
    result_list.append("D55:" + string_d55)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

    k = [re.findall('[\t\s\n]+final ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number = len(m)

    k = [re.findall('^final ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number2 = len(m)

    k = [re.findall('[=({]final ', line)
         for line in all_lines_nocomments]
    m = sum(k, [])
    number4 = len(m)

    number3 = number2 + number + number4
    if NCLOC == 0:
        n1 = 0
    else:
        n1 = number3 / NCLOC
    n1 = round(n1, 3)

    string_d56 = str(n1)
    result_list.append("D56:" + string_d56)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 
    # changed by fari
    relative_path = java_file.replace(main_directory, "")
    folder_name_author = relative_path.split(separator)[1]
    result_list.append(java_file)

    results = ','.join(result_list) + "\n"

    if not bad_file:
        with io.open(result_file, 'a') as waf:
            waf.write(results)

    all_lines_latin1 = None
    all_lines_nocomments = None
    all_lines_txtparsed = None
    results = None

    del (all_lines_latin1)
    del (all_lines_nocomments)
    del (all_lines_txtparsed)
    del (results)

# CONSISTENCY CHECK

total_java_files = len(java_files)

total_processed_files = 0
if os.path.isfile(result_file):
    with io.open(result_file, 'r') as raf:
        for line in raf:
            line = line.strip()
            if line:
                total_processed_files = total_processed_files + 1

total_error_files = 0
if os.path.isfile(error_file):
    with io.open(error_file, 'r') as raf:
        for line in raf:
            line = line.strip()
            if ("**** ERROR " in line):
                total_error_files = total_error_files + 1

processed_plus_errors = total_processed_files + total_error_files
if not (total_java_files == processed_plus_errors):
    print("Total files = " + str(total_java_files))
    print("Total processed = " + str(total_processed_files))
    print("Total errors = " + str(total_error_files))
    print("Total processed + Total errors = " + str(processed_plus_errors))
    raise AssertionError("ERROR: number of processed files does not match total files")

sys.exit()
