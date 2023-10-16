import sys
import re
import math
import os
import io

# ================================================================== #
"""
Given a directory location, obtains all the files in the directory
directory: the starting directory
Yield: the absolute paths of the files in the provided directory
"""
def absoluteFilePaths(directory):
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))


"""
Count the lines in a file
fname: the name of the file
Return: the number of lines in the file
"""
def file_lines(fname):
    count = 0
    # UnicodeDecodeError: 'utf8' codec can't decode byte 0xce in position 601: invalid continuation byte
    if os.path.isfile(fname):
        with io.open(fname, "r", encoding='utf-8', errors='ignore') as f:
             for line in f:
                count = count + 1
    else:
        print("filepath --> ", fname)
        raise AssertionError("ERROR: file NOT found")
    return count


"""
Counts a searched-for character in a list of lines
keychar: the character being searched for
list_of_lines: list containing lines (that are strings?)
"""
def ccount(keychar, list_of_lines):
    count = 0
    for line in list_of_lines:
        for xchar in line:
            if (xchar == keychar):
                count = count + 1
    return (count)

"""
Calculates standard deviation
data: a list containing values
"""
def sd_calc(data):
    n = len(data)

    if n <= 1:
        return 0.0

    mean, sd = avg_calc(data), 0.0

    # calculate std. dev.
    for el in data:
        sd += (float(el) - mean)**2
    sd = math.sqrt(sd / float(n-1))

    return sd

"""
Calculates the average of a list of values
ls: list of values
"""
def avg_calc(ls):
    n, mean = len(ls), 0.0

    # NR adjustment b/c of this error:
    # IndexError: list index out of range
    if n == 0:
        return 0.0

    elif n == 1:
        return ls[0]

    # calculate average
    for el in ls:
        mean = mean + float(el)
    mean = mean / float(n)

    return mean


#-----------------------------------------------------------------------------

main_directory = str(sys.argv[1])
print(main_directory)
separator = "/"


error_file = main_directory + separator + "caliskan_errors.txt"

all_files = absoluteFilePaths(main_directory)

# Get list of java files in the dataset folder
java_files = list()
for item in all_files:
    if not ("/._" in item):
        if item.endswith(".java"):
            if not (item in java_files):
                java_files.append(item)
java_files.sort()

# Obtain list of author paths
author_pathnames = list()
for files in java_files:
    author_path = separator.join(files.split(separator)[:-2])
    if author_path not in author_pathnames:
        author_pathnames.append(author_path)
author_pathnames.sort()

# Each author file path key has a list of all its java files
authors_dict = dict()
for author in author_pathnames:
    authors_dict[author] = list()

# Get a list of java files per author
for files in java_files:
    author_folder = separator.join(files.split(separator)[:-2])
    authors_dict[author_folder].append(files)


#------------------------------ LAYOUT FEATURES --------------------------------------- #

for author in authors_dict:

    all_authors_laylex = list()

    all_results = str()
    
    for java_file in authors_dict[author]:

        results = dict()

        bad_file = False

        # Ignore the corresponding Java file if com file doesn't exist
        com_file = str(java_file)[:-5] + ".com"
        if not os.path.isfile(com_file):
            bad_file = True
            with io.open(error_file,'a') as waf:
                waf.write("**** ERROR " + str(java_file) + " \n")
                waf.write("Missing " + com_file + " \n")
        if bad_file:
            continue

        # Ignore the corresponding Java file if txt file doesn't exist
        txt_file = str(java_file)[:-5] + ".txt"
        if not os.path.isfile(txt_file):
            bad_file = True
            with io.open(error_file,'a') as waf:
                waf.write("**** ERROR " + str(java_file) + " \n")
                waf.write("Missing " + txt_file + " \n")
        if bad_file:
            continue

        # FROM COM FILE, get all lines
        all_lines_nocomments = list()
        with io.open(com_file,'r', encoding='utf-8', errors='ignore') as rfl:
            for line in rfl:
                all_lines_nocomments.append(line)

        # FROM TXT FILE, get all lines
        all_lines_txtparsed = list()
        with io.open(txt_file, 'r', encoding='utf-8', errors='ignore') as rfl:
            for line in rfl:
                all_lines_txtparsed.append(line)


        # FROM JAVA FILE, get all lines with LATIN-1 encoding
        all_lines_latin1 = list()
        with io.open(java_file,'r', encoding='utf-8', errors='ignore') as rfl:
            for line in rfl:
                all_lines_latin1.append(line)

        line_num = file_lines(java_file)

        content = ''.join(all_lines_latin1)
        char_num = len(content)

        # ------------------------- F1: ln(# of tabs/length) -------------------------------- #
        
        count_tabs = ccount("\t", all_lines_nocomments)
        result = math.log((count_tabs+1)/char_num)
        result = round(result, 5)

        str_f1 = str(result)
        results["F1: ln(# of tabs/length)"] = str_f1

        # ------------------------- F2: ln(# of spaces/length) -------------------------------- #
        
        
        count_spaces = ccount(" ", all_lines_nocomments)
        result = math.log((count_spaces+1)/char_num)
        result = round(result, 5)

        str_f2 = str(result)
        results["F2: ln(# of spaces/length)"] = str_f2

        # ------------------------- F3: ln(# empty lines/length) -------------------------------- #
        non_blank_count = 0

        for line in all_lines_latin1:
           if line.strip():
              non_blank_count += 1

        blank_lines = line_num - non_blank_count

        result = math.log((blank_lines+1)/char_num)
        result = round(result, 5)

        str_f3 = str(result)
        results["F3: ln(# of empty lines/length)"] = str_f3

        # ------------------------- F4: whitespace ratio -------------------------------- #

        count_newlines = ccount("\n", all_lines_nocomments)
        total_whitespace = count_tabs + count_spaces + count_newlines

        non_whitespace = char_num - total_whitespace

        whitespace_ratio = total_whitespace/non_whitespace
        whitespace_ratio = round(whitespace_ratio, 5)

        str_f4 = str(whitespace_ratio)
        results["F4: whitespace ratio)"] = str_f4

        # ------------------------- F5: newline before open braces -------------------------------- #

        # Open curly brackets at the beginning of a line
        begin_brackets = [re.findall('^\s*\t*\{\t*\s*[a-zA-Z0-9\S]', line) for line in all_lines_nocomments]
        total_begin_brackets = sum(begin_brackets, [])
        num_begin_brackets = len(total_begin_brackets)
        
        # Open curly brackets alone on a line
        alone_brackets = [re.findall('^\s*\t*\{\t*\s*$', line) for line in all_lines_nocomments]
        total_alone_brackets = sum(alone_brackets, [])
        num_alone_brackets = len(total_alone_brackets)

        # Open curly brackets at the end of a line
        end_brackets = [re.findall('\t*\s*[a-zA-Z0-9\S]\s*\t*\{', line) for line in all_lines_nocomments]
        total_end_brackets = sum(end_brackets, [])
        num_end_brackets = len(total_end_brackets)

        # Brackets that are begin on/alone on a line are preceded by a newline char
        if (num_begin_brackets + num_alone_brackets) > num_end_brackets:
            majority = 1         # True
        else:
            majority = 0        # False

        str_f5 = str(majority)
        results["F5: majority of open curly braces preceded by a newline"] = str_f5

        # ------------------------- F6: tab lead lines -------------------------------- #

        # Count lines that begin with spaces
        spaces = []
        for line in all_lines_nocomments:
            spaces.append(len(line) - len(line.lstrip(" ")))
        space_count = 0
        for el in spaces:
            if el > 0:
                space_count = space_count + 1

        # Count lines that begin with tabs
        tabs = [];
        for line in all_lines_nocomments:
            tabs.append(len(line) - len(line.lstrip("\t")))
        tab_count = 0
        for el in tabs:
            if el > 0:
                tab_count = tab_count + 1

        if tab_count > space_count:
            majority = 1             # True
        else:
            majority = 0            # False

        str_f6 = str(majority)
        results["F6: majority of indented lines begin with a tab"] = str_f6


    # ------------------------------ LEXICAL FEATURES --------------------------------------- #

    # ------------------------------F7: ln(do statement #/length) --------------------------------------- #

        do_statements = [re.findall("Do Statement Count:(.*)", line) for line in all_lines_txtparsed]
        do_total = sum(do_statements, [])
        g = [elem.replace(" ", "") for elem in do_total]
        do_num = int(g[0])

        result = math.log((do_num+1)/char_num)
        result = round(result,3)

        str_f7 = str(result)
        results["F7: ln(# of do/length)"] = str_f7

    # ------------------------------F8: ln(while statement #/length) --------------------------------------- #

        while_statements = [re.findall("While Statement Count:(.*)", line) for line in all_lines_txtparsed]
        while_total = sum(while_statements, [])
        g = [elem.replace(" ", "") for elem in while_total]
        while_num = int(g[0])

        result = math.log((while_num+1)/char_num)
        result = round(result,3)

        str_f8 = str(result)
        results["F8: ln(# of while/length)"] = str_f8

    # ------------------------------F9: ln(for statement #/length) --------------------------------------- #

        for_statements = [re.findall("For Statement Count:(.*)", line) for line in all_lines_txtparsed]
        for_total = sum(for_statements, [])
        g = [elem.replace(" ", "") for elem in for_total]
        for_num = int(g[0])

        result = math.log((for_num+1)/char_num)
        result = round(result,3)

        str_f9 = str(result)
        results["F9: ln(# of for/length)"] = str_f9

    # ------------------------------F10: ln(if statement #/length) --------------------------------------- #

        if_statements = [re.findall("If Statement Count:(.*)", line) for line in all_lines_txtparsed]
        if_total = sum(if_statements, [])

        s = ''.join(all_lines_txtparsed)
        
        k1 = re.findall("(?s)If Statement Collected:\\s(.*)If Statement Count:", s, re.MULTILINE)

        if k1==[]:
           else_num=0
        else:
           else_num=k1[0].count('else')

        if_statements = [re.findall("If Statement Count:(.*)", line) for line in all_lines_txtparsed]
        if_total = sum(if_statements, [])
        g = [elem.replace(" ", "") for elem in if_total]
        if_num = int(g[0])

        result = math.log((if_num+1)/char_num)
        result = round(result,3)

        str_f10 = str(result)
        results["F10: ln(# of if/length"] = str_f10

    # ------------------------------F11: ln(else statement #/length) --------------------------------------- #

        else_statements = re.findall("(?s)If Statement Collected:\\s(.*)If Statement Count:", s, re.MULTILINE)

        if else_statements == []:
           else_num=0
        else:
           else_num=else_statements[0].count('else')

        result = math.log((else_num+1)/char_num)
        result = round(result,3)

        str_f11 = str(result)
        results["F11: ln(# of else/length)"] = str_f11


    # ------------------------------F12: ln(switch statement #/length) --------------------------------------- #

        switch_statements = [re.findall("Switch Statement Count:(.*)", line) for line in all_lines_txtparsed]
        switch_total = sum(switch_statements, [])
        g = [elem.replace(" ", "") for elem in switch_total]
        switch_num = int(g[0])

        result = math.log((switch_num+1)/char_num)
        result = round(result,3)

        str_f12 = str(result)
        results["F12: ln(# of switch/length)"] = str_f12

    # ------------------------------F13: ln(else if statement #/length) --------------------------------------- #

        else_if_statements1 = [re.findall("[\t\s\n]+else if ", line) for line in all_lines_nocomments]
        total1 = sum(else_if_statements1, [])
        num1 = len(total1)

        else_if_statements2 = [re.findall("^else if ", line) for line in all_lines_nocomments]
        total2 = sum(else_if_statements2, [])
        num2 = len(total2)

        else_if_statements3 = [re.findall("[=({]else if ", line) for line in all_lines_nocomments]
        total3 = sum(else_if_statements3, [])
        num3 = len(total3)

        total_else_if = num1 +  num2 + num3

        result = math.log((total_else_if+1)/char_num)
        result = round(result,3)

        str_f13 = str(result)
        results["F13: ln(# of else if/length)"] = str_f13

    # ------------------------------F14: ln(ternary operators #/length) --------------------------------------- #

        ternary_ops = [re.findall("[a-z0-9\s\S]+\?[a-z0-9\s\S]+\:[a-z0-9\s\S]+", line) for line in all_lines_nocomments]
        ternary_ops_total = sum(ternary_ops, [])
        ternary_num = len(ternary_ops_total)
        
        result = math.log((ternary_num+1)/char_num)
        result = round(result,3)

        str_f14 = str(result)
        results["F14: ln(# ternary operators/length)"] = str_f14

    # ------------------------------F15: ln(word token #/length) --------------------------------------- #
        word_tokens = [re.findall(r'\w+', line) for line in all_lines_nocomments]
        word_token_total = sum(word_tokens, [])
        token_num = len(word_token_total)

        result = math.log((token_num+1)/char_num)
        result = round(result,3)

        str_f15 = str(result)
        results["F15: ln(# word tokens/length)"] = str_f15

    # ------------------------------F16: ln(comment #/length) --------------------------------------- #

        # Count block comments -------------------------------- #
        
        block_com = [re.findall("Block Comment Count:\s(.*)", line) for line in all_lines_txtparsed]

        block_com_total = sum(block_com, [])

        g = [elem.replace(" ", "") for elem in block_com_total]

        block_com_num = int(g[0])

        # Count line comments -------------------------------- #

        line_com = [re.findall("Line Comment Count:\s(.*)", line) for line in all_lines_txtparsed]

        line_com_total = sum(line_com, [])

        g = [elem.replace(" ", "") for elem in line_com_total]

        line_com_num = int(g[0])

        # Count Javadoc comments -------------------------------- #

        java_com = [re.findall("Javadoc Comment Count:\s(.*)", line) for line in all_lines_txtparsed]
        java_com_total = sum(java_com, [])

        g = [elem.replace(" ", "") for elem in java_com_total]

        java_com_num = int(g[0])

        # Sum comments -------------------------------- #

        total_com = block_com_num + line_com_num + java_com_num
        result = math.log((total_com+1)/char_num)
        result = round(result,3)

        str_f16 = str(result)
        results["F16: ln(# comments/length)"] = str_f16

    # ------------------------------F17: ln(literal #/length) --------------------------------------- #

        # Count boolean literal expressions -------------------------------- #
        
        bool_lit = [re.findall("Boolean Literal Expression Count:\s(.*)", line) for line in all_lines_txtparsed]
        bool_lit_total = sum(bool_lit, [])

        g= [elem.replace(" ", "") for elem in bool_lit_total]
        bool_num = int(g[0])

        # Count char literal expressions -------------------------------- #

        char_lit = [re.findall("Char Literal Expression Count:\s(.*)", line) for line in all_lines_txtparsed]
        char_lit_total = sum(char_lit, [])

        g = [elem.replace(" ", "") for elem in char_lit_total]
        char_lit_num = int(g[0])
        #print("char_lit_num = ",char_lit_num)

        # Count double literal expressions -------------------------------- #

        double_lit = [re.findall("Double Literal Expression Count:\s(.*)", line) for line in all_lines_txtparsed]
        double_lit_total = sum(double_lit, [])

        g = [elem.replace(" ", "") for elem in double_lit_total]

        double_num = int(g[0])

        # Count integer literal expressions -------------------------------- #

        int_lit = [re.findall("Integer Literal Expression Count:\s(.*)", line) for line in all_lines_txtparsed]
        int_lit_total = sum(int_lit, [])

        g = [elem.replace(" ", "") for elem in int_lit_total]

        int_num = int(g[0])

        # Count long literal expressions -------------------------------- #

        long_lit = [re.findall("Long Literal Expression Count:\s(.*)", line) for line in all_lines_txtparsed]
        long_lit_total = sum(long_lit, [])

        g = [elem.replace(" ", "") for elem in long_lit_total]

        long_num = int(g[0])

        # Count null literal expressions -------------------------------- #

        null_lit = [re.findall("Null Literal Expression Count:\s(.*)", line) for line in all_lines_txtparsed]
        null_lit_total = sum(null_lit, [])

        g = [elem.replace(" ", "") for elem in null_lit_total]

        null_num = int(g[0])

        # Count single literal expressions -------------------------------- #

        single_lit = [re.findall("Single Literal Expression Count:\s(.*)", line) for line in all_lines_txtparsed]
        single_lit_total = sum(single_lit, [])

        g = [elem.replace(" ", "") for elem in single_lit_total]
        single_num = int(g[0])

        # Sum literals -------------------------------- #

        total_lit = bool_num + char_lit_num + double_num + int_num + long_num + null_num + single_num
        result = math.log((total_lit+1)/char_num)
        result = round(result,3)

        str_f17 = str(result)
        results["F17: ln(# literals/length)"] = str_f17


        # ------------------------------F18: ln(method #/length) --------------------------------------- #

        methods = [re.findall("Method Count:\s(.*)", line) for line in all_lines_txtparsed]

        method_total = sum(methods, [])

        g = [elem.replace(" ", "") for elem in method_total]

        method_num = int(g[0])

        result = math.log((method_num+1)/char_num)
        result = round(result,3)

        str_f18 = str(result)
        results["F18: ln(# methods/length)"] = str_f18

        # ---------------------F19: average parameters + F20: std. dev. of parameters ------------------------------ #

        k1 = [re.findall("Method Collected:\s(.*)", line) for line in all_lines_txtparsed]
        m = sum(k1, [])
        n1=[]
        for element in range(len(m)):
            a=str(' '+m[element]+'(')
            n1.append(a)

        n2=[]
        for element in range(len(m)):
            a=str(' '+m[element]+' (')
            n2.append(a)

        a=[]
        for i in range(len(n1)):
            k1 = [re.findall(re.escape(n1[i])+'(.*)'+'\)', line) for line in all_lines_txtparsed]
            m = sum(k1, [])
            a.append(m)

        for i in range(len(n2)):
            k1 = [re.findall(re.escape(n2[i])+'(.*)'+'\)', line) for line in all_lines_txtparsed]
            m = sum(k1, [])
            a.append(m)

        m = sum(a, [])

        new_list = [m[i:i+1] for i in range(0, len(m), 1)]

        a=[]
        for i in range(len(new_list)):
            a.append(new_list[i][0].split(','))

        lenf=[]
        for element in range(len(a)):
            if a[element][0]=='':
                lenf.append(0)
            else:
                lenf.append(len(a[element]))

        avg_params = avg_calc(lenf)
        str_f19 = str(avg_params)
        results["F19: avg"] = str_f19

        std_dev_params = sd_calc(lenf)
        str_f20 = str(std_dev_params)
        results["F20: std. dev"] = str_f20


        # Generate an .arff file of rsults for each author
        results_str = str()
        for key in results:
            results_str = results_str + key + " === " + str(results[key]) + "\n"
        results_str = results_str + java_file.split(separator)[-1] + "\n"


        results_filename = separator.join(java_file.split(separator)[:-1]) + separator + java_file.split(separator)[-1][:-5] + ".results"
        with io.open(results_filename, 'w') as waf:
            waf.write(results_str)

        all_results = all_results + results_str

    # For each author, write the author results to an arff file
    author_name = author.split(separator)[-1]

    results_filename = author + separator + author_name + "_results.arff"

    with io.open(results_filename, 'w') as waf:
        waf.write(all_results)


# --------------------- KEYWORDS ------------------------------------ # 

all_keywords = list()      
for author in authors_dict:

    all_keywords_dicts = list()

    for java_file in authors_dict[author]:

        # FROM COM FILE, get all lines
        com_file = java_file[:-4] + "com"
        all_lines_nocomments = list()
        with io.open(com_file,'r', encoding='utf-8', errors='ignore') as rfl:
            for line in rfl:
                all_lines_nocomments.append(line)

        # FROM TXT FILE, get all lines
        txt_file = java_file[:-4] + "txt"
        all_lines_txtparsed = list()
        with io.open(txt_file, 'r', encoding='utf-8', errors='ignore') as rfl:
            for line in rfl:
                all_lines_txtparsed.append(line)


        keywords = dict()
        NCLOC = 50

        #----------------------- D1: ratio of abstact to NCLOC ------------------------------ #

        abs1 = [re.findall('[\t\s\n]+abstract ', line) for line in all_lines_nocomments]
        abs1_total = sum(abs1, [])
        num1 = len(abs1_total)

        abs2 = [re.findall('^abstract ', line) for line in all_lines_nocomments]
        abs2_total = sum(abs2, [])
        num2 = len(abs2_total)

        abs3 = [re.findall('[=({]abstract ', line) for line in all_lines_nocomments]
        abs3_total = sum(abs3, [])
        num3 = len(abs3_total)

        abs_total = num1 + num2 + num3

        result = abs_total/NCLOC
        result = round(result,3)

        str_d1 = str(result)
        keywords["D1: ratio of abstract to NCLOC"] = str_d1

        #----------------------- D2: ratio of continue to NCLOC ------------------------------ #

        cont = [re.findall("Continue Statement Count:\s(.*)", line) for line in all_lines_txtparsed]

        cont_total = sum(cont, [])

        g= [elem.replace(" ", "") for elem in cont_total]

        if not g:
            cont_num = 0
        else:
            cont_num = int(g[0])

        result = cont_num/NCLOC
        result = round(result,3)

        str_d2 = str(result)
        keywords["D2: ratio of continue to NCLOC"] = str_d2

        #----------------------- D3: ratio of for to NCLOC ------------------------------ #

        for_stat = [re.findall("For Statement Count:\s(.*)", line) for line in all_lines_txtparsed]

        for_total = sum(for_stat, [])

        g= [elem.replace(" ", "") for elem in for_total]

        if not g:
            for_num = 0
        else:
            for_num = int(g[0])

        result = for_num/NCLOC
        result = round(result,3)

        str_d3 = str(result)
        keywords["D3: ratio of for to NCLOC"] = str_d3

        #----------------------- D4: ratio of new to NCLOC ------------------------------ #

        new1 = [re.findall('[\t\s\n]+new ', line) for line in all_lines_nocomments]
        new1_total = sum(new1, [])
        num1 = len(new1_total)

        new2 = [re.findall('^new ', line) for line in all_lines_nocomments]
        new2_total = sum(new2, [])
        num2 = len(new2_total)

        new3 = [re.findall('[=({]new ', line) for line in all_lines_nocomments]
        new3_total = sum(new3, [])
        num3 = len(new3_total)

        new_total = num1+ num2 + num3

        result = new_total/NCLOC
        result = round(result,3)

        str_d4 = str(result)
        keywords["D4: ratio of new to NCLOC"] = str_d4

        #----------------------- D5: ratio of switch to NCLOC ------------------------------ #

        switch_stat = [re.findall("Switch Statement Count:\s(.*)", line) for line in all_lines_txtparsed]

        switch_total = sum(switch_stat, [])

        g= [elem.replace(" ", "") for elem in switch_total]

        if not g:
            switch_num = 0
        else:
            switch_num = int(g[0])

        result = switch_num/NCLOC
        result = round(result,3)

        str_d5 = str(result)
        keywords["D5: ratio of switch to NCLOC"] = str_d5

        #----------------------- D6: ratio of assert to NCLOC ------------------------------ #

        assert_stat = [re.findall("Assert Statment Count:\s(.*)", line) for line in all_lines_txtparsed]

        assert_total = sum(assert_stat, [])

        g= [elem.replace(" ", "") for elem in assert_total]

        if not g:
            assert_num = 0
        else:
            assert_num = int(g[0])

        result = assert_num/NCLOC
        result = round(result,3)

        str_d6 = str(result)
        keywords["D6: ratio of assert to NCLOC"] = str_d6

        #----------------------- D7: ratio of default to NCLOC ------------------------------ #

        default1 = [re.findall('[\t\s\n]+default ', line) for line in all_lines_nocomments]
        default1_total = sum(default1, [])
        num1 = len(default1_total)


        default2 = [re.findall('^default ', line) for line in all_lines_nocomments]
        default2_total = sum(default2, [])
        num2 = len(default2_total)

        default3 = [re.findall('[=({]default ', line) for line in all_lines_nocomments]
        default3_total = sum(default3, [])
        num3 = len(default3_total)

        default_total = num1 + num2 + num3

        result = default_total/NCLOC
        result = round(result,3)

        str_d7 = str(result)
        keywords["D7: ratio of default to NCLOC"] = str_d7

        #----------------------- D8: ratio of goto to NCLOC ------------------------------ #

        goto1 = [re.findall('[\t\s\n]+goto ', line) for line in all_lines_nocomments]
        goto1_total = sum(goto1, [])
        num1 = len(goto1_total)


        goto2 = [re.findall('^goto ', line) for line in all_lines_nocomments]
        goto2_total = sum(goto2, [])
        num2 = len(goto2_total)

        goto3 = [re.findall('[=({]goto ', line) for line in all_lines_nocomments]
        goto3_total = sum(goto3, [])
        num3 = len(goto3_total)

        goto_total = num1 + num2 + num3

        result = goto_total/NCLOC
        result = round(result,3)

        str_d8 = str(result)
        keywords["D8: ratio of goto to NCLOC"] = str_d8

        #----------------------- D9: ratio of package to NCLOC ------------------------------ #

        pkg = [re.findall("Package Declaration Count:\s(.*)", line) for line in all_lines_txtparsed]

        pkg_total = sum(pkg, [])
        g= [elem.replace(" ", "") for elem in pkg_total]

        if not g:
            pkg_num=0
        else:
            pkg_num=int(g[0])

        result = pkg_num/NCLOC
        result = round(result,3)

        str_d9 = str(result)
        keywords["D9: ratio of package to NCLOC"] = str_d9

        #----------------------- D10: ratio of synchronized to NCLOC ------------------------------ #

        synch = [re.findall("Synchronized Statement Count:\s(.*)", line) for line in all_lines_txtparsed]
        synch_total = sum(synch, [])

        g= [elem.replace(" ", "") for elem in synch_total]

        if not g:
            synch_num=0
        else:
            synch_num=int(g[0])

        result = synch_num/NCLOC
        result = round(result,3)

        str_d10 = str(result)
        keywords["D10: ratio of synchronized to NCLOC"] = str_d10

        #----------------------- D11: ratio of boolean to NCLOC ------------------------------ #

        bool1 = [re.findall('[\t\s\n]+boolean ', line) for line in all_lines_nocomments]
        bool1_total = sum(bool1, [])
        num1 = len(bool1_total)


        bool2 = [re.findall('^boolean ', line) for line in all_lines_nocomments]
        bool2_total = sum(bool2, [])
        num2 = len(bool2_total)

        bool3 = [re.findall('[=({]boolean ', line) for line in all_lines_nocomments]
        bool3_total = sum(bool3, [])
        num3 = len(bool3_total)

        bool_total = num1 + num2 + num3

        result = bool_total/NCLOC
        result = round(result,3)

        str_d11 = str(result)
        keywords["D11: ratio of boolean to NCLOC"] = str_d11

        #----------------------- D12: ratio of do to NCLOC ------------------------------ #

        do_stat = [re.findall('Do Statement Count:(.*)', line) for line in all_lines_txtparsed]

        do_total = sum(do_stat, [])

        g = [elem.replace(" ", "") for elem in do_total]
        if not g:
            do_num=0
        else:
            do_num=int(g[0])

        result = do_num/NCLOC
        result = round(result,3)

        str_d12 = str(result)
        keywords["D12: ratio of do to NCLOC"] = str_d12

        #----------------------- D13: ratio of if to NCLOC ------------------------------ #

        if_stat = [re.findall('If Statement Count:\s(.*)', line) for line in all_lines_txtparsed]
        if_total = sum(if_stat, [])

        g= [elem.replace(" ", "") for elem in if_total]

        if not g:
            if_num = 0
        else:
            if_num = int(g[0])

        result = if_num/NCLOC
        result = round(result,3)

        str_d13 = str(result)
        keywords["D13: ratio of if to NCLOC"] = str_d13

        #----------------------- D14: ratio of private to NCLOC ------------------------------ #
        priv1 = [re.findall('[\t\s\n]+private ', line) for line in all_lines_nocomments]
        priv1_total = sum(priv1, [])
        num1 = len(priv1_total)


        priv2 = [re.findall('^private ', line) for line in all_lines_nocomments]
        priv2_total = sum(priv2, [])
        num2 = len(priv2_total)

        priv3 = [re.findall('[=({]private ', line) for line in all_lines_nocomments]
        priv3_total = sum(priv3, [])
        num3 = len(priv3_total)

        priv_total = num1 + num2 + num3

        result = priv_total/NCLOC
        result = round(result,3)

        str_d14 = str(result)
        keywords["D14: ratio of private to NCLOC"] = str_d14

        #----------------------- D15: ratio of this to NCLOC ------------------------------ #

        this_stat = [re.findall('This Expression Count:\s(.*)', line) for line in all_lines_txtparsed]
        this_total = sum(this_stat, [])

        g= [elem.replace(" ", "") for elem in this_total]

        if not g:
            this_num = 0
        else:
            this_num = int(g[0])

        result = this_num/NCLOC
        result = round(result,3)

        str_d15 = str(result)
        keywords["D15: ratio of this to NCLOC"] = str_d15

        #----------------------- D16: ratio of break to NCLOC ------------------------------ #

        break_stat = [re.findall('Break Statement Count:\s(.*)', line) for line in all_lines_txtparsed]
        break_total = sum(break_stat, [])

        g= [elem.replace(" ", "") for elem in break_total]

        if not g:
            break_num = 0
        else:
            break_num = int(g[0])

        result = break_num/NCLOC
        result = round(result,3)


        str_d16 = str(result)
        keywords["D16: ratio of break to NCLOC"] = str_d16

        #----------------------- D17: ratio of double to NCLOC ------------------------------ #

        doub1 = [re.findall('[\t\s\n]+double ', line) for line in all_lines_nocomments]
        doub1_total = sum(doub1, [])
        num1 = len(doub1_total)


        doub2 = [re.findall('^double ', line) for line in all_lines_nocomments]
        doub2_total = sum(doub2, [])
        num2 = len(doub2_total)

        doub3 = [re.findall('[=({]double ', line) for line in all_lines_nocomments]
        doub3_total = sum(doub3, [])
        num3 = len(doub3_total)

        doub_total = num1 + num2 + num3

        result = doub_total/NCLOC
        result = round(result,3)

        str_d17 = str(result)
        keywords["D17: ratio of double to NCLOC"] = str_d17

        #----------------------- D18: ratio of implements to NCLOC ------------------------------ #

        imp1 = [re.findall('[\t\s\n]+implements ', line) for line in all_lines_nocomments]
        imp1_total = sum(imp1, [])
        num1 = len(imp1_total)


        imp2 = [re.findall('^implements ', line) for line in all_lines_nocomments]
        imp2_total = sum(imp2, [])
        num2 = len(imp2_total)

        imp3 = [re.findall('[=({]implements ', line) for line in all_lines_nocomments]
        imp3_total = sum(imp3, [])
        num3 = len(imp3_total)

        imp_total = num1 + num2 + num3

        result = imp_total/NCLOC
        result = round(result,3)

        str_d18 = str(result)
        keywords["D18: ratio of implements to NCLOC"] = str_d18

        #----------------------- D19: ratio of protected to NCLOC ------------------------------ #

        pro1 = [re.findall('[\t\s\n]+protected ', line) for line in all_lines_nocomments]
        pro1_total = sum(pro1, [])
        num1 = len(pro1_total)

        pro2 = [re.findall('^protected ', line) for line in all_lines_nocomments]
        pro2_total = sum(pro2, [])
        num2 = len(pro2_total)

        pro3 = [re.findall('[=({]protected ', line) for line in all_lines_nocomments]
        pro3_total = sum(pro3, [])
        num3 = len(pro3_total)

        pro_total = num1 + num2 + num3

        result = pro_total/NCLOC
        result = round(result,3)

        str_d19 = str(result)
        keywords["D19: ratio of protected to NCLOC"] = str_d19

        #----------------------- D20: ratio of throw to NCLOC ------------------------------ #

        throw_stat = [re.findall('Throw Statement Count:\s(.*)', line) for line in all_lines_txtparsed]
        throw_total = sum(throw_stat, [])

        g = [elem.replace(" ", "") for elem in throw_total]

        if not g:
            throw_num = 0
        else:
            throw_num = int(g[0])

        result = throw_num/NCLOC
        result = round(result,3)

        str_d20 = str(result)
        keywords["D20: ratio of throw to NCLOC"] = str_d20

        #----------------------- D21: ratio of byte to NCLOC ------------------------------ #

        byte1 = [re.findall('[\t\s\n]+byte ', line) for line in all_lines_nocomments]
        byte1_total = sum(byte1, [])
        num1 = len(byte1_total)

        byte2 = [re.findall('^byte ', line) for line in all_lines_nocomments]
        byte2_total = sum(byte2, [])
        num2 = len(byte2_total)

        byte3 = [re.findall('[=({]byte ', line) for line in all_lines_nocomments]
        byte3_total = sum(byte3, [])
        num3 = len(byte3_total)

        byte4 = [re.findall('byte\[', line) for line in all_lines_nocomments]
        byte4_total = sum(byte4, [])
        num4 = len(byte4_total)

        byte_total = num1 + num2 + num3 + num4

        result = byte_total/NCLOC
        result = round(result,3)

        str_d21 = str(result)
        keywords["D21: ratio of byte to NCLOC"] = str_d21

        #----------------------- D22: ratio of else to NCLOC ------------------------------ #

        s = ''.join(all_lines_txtparsed)
        else_stat = re.findall("(?s)If Statement Collected:\\s(.*)If Statement Count:", s, re.MULTILINE)

        if else_stat == []:
            else_num = 0;
        else:
            else_num = else_stat[0].count('else')

        result = else_num/NCLOC
        result = round(result,3)

        str_d22 = str(result)
        keywords["D22: ratio of else to NCLOC"] = str_d22

        #----------------------- D23: ratio of import to NCLOC ------------------------------ #

        import_stat = [re.findall('Import Declaration Count:\s(.*)', line) for line in all_lines_txtparsed]
        import_total = sum(import_stat, [])

        g = [elem.replace(" ", "") for elem in import_total]

        if not g:
            import_num = 0
        else:
            import_num = int(g[0])

        result = import_num/NCLOC
        result = round(result,3)

        str_d23 = str(result)
        keywords["D23: ratio of import to NCLOC"] = str_d23

        #----------------------- D24: ratio of public to NCLOC ------------------------------ #

        public1 = [re.findall('[\t\s\n]+public ', line) for line in all_lines_nocomments]
        public1_total = sum(public1, [])
        num1 = len(public1_total)

        public2 = [re.findall('^public ', line) for line in all_lines_nocomments]
        public2_total = sum(public2, [])
        num2 = len(public2_total)

        public3 = [re.findall('[=({]public ', line) for line in all_lines_nocomments]
        public3_total = sum(public3, [])
        num3 = len(public3_total)

        public_total = num1 + num2 + num3
        result = public_total/NCLOC
        result = round(result,3)

        str_d24 = str(result)
        keywords["D24: ratio of public to NCLOC"] = str_d24

        #----------------------- D25: ratio of throws to NCLOC ------------------------------ #

        throws1 = [re.findall('[\t\s\n]+throws ', line) for line in all_lines_nocomments]
        throws1_total = sum(throws1, [])
        num1 = len(throws1_total)

        throws2 = [re.findall('^throws ', line) for line in all_lines_nocomments]
        throws2_total = sum(throws2, [])
        num2 = len(throws2_total)

        throws3 = [re.findall('[=({]throws ', line) for line in all_lines_nocomments]
        throws3_total = sum(throws3, [])
        num3 = len(throws3_total)

        throws_total = num1 + num2 + num3

        result = throws_total/NCLOC
        result = round(result,3)

        str_d25 = str(result)
        keywords["D25: ratio of throws to NCLOC"] = str_d25

        #----------------------- D26: ratio of case to NCLOC ------------------------------ #

        case_stat = [re.findall('Switch Entry Statement Count:\s(.*)', line) for line in all_lines_txtparsed]
        case_total = sum(case_stat, [])

        g = [elem.replace(" ", "") for elem in case_total]

        case_num = int(g[0])

        result = case_num/NCLOC
        result = round(result,3)

        str_d26 = str(result)
        keywords["D26: ratio of case to NCLOC"] = str_d26

        #----------------------- D27: ratio of enum to NCLOC ------------------------------ #

        enum_stat = [re.findall('Enum Declaration Count:\s(.*)', line) for line in all_lines_txtparsed]
        enum_total = sum(enum_stat, [])

        g = [elem.replace(" ", "") for elem in enum_total]
        enum_num = int(g[0])

        result = enum_num/NCLOC
        result = round(result,3)

        str_d27 = str(result)
        keywords["D27: ratio of enum to NCLOC"] = str_d27

        #----------------------- D28: ratio of instance of to NCLOC ------------------------------ #

        instanceof_stat = [re.findall('Instance Of Expression Count:\s(.*)', line) for line in all_lines_txtparsed]
        instanceof_total = sum(instanceof_stat, [])

        g = [elem.replace(" ", "") for elem in instanceof_total]

        instanceof_num = int(g[0])
        result = instanceof_num/NCLOC
        result = round(result,3)

        str_d28 = str(result)
        keywords["D28: ratio of instance of to NCLOC"] = str_d28

        #----------------------- D29: ratio of return to NCLOC ------------------------------ #

        ret1 = [re.findall('[\t\s\n]+return ', line)for line in all_lines_nocomments]
        ret1_total = sum(ret1, [])
        num1 = len(ret1_total)

        ret2 = [re.findall('^return ', line) for line in all_lines_nocomments]
        ret2_total = sum(ret2, [])
        num2 = len(ret2_total)

        ret3 = [re.findall('[=({]return ', line) for line in all_lines_nocomments]
        ret3_total = sum(ret3, [])
        num3 = len(ret3_total)

        ret_total = num1 + num2 + num3

        result = ret_total/NCLOC
        result = round(result,3)

        str_d29 = str(result)
        keywords["D29: ratio of return to NCLOC"] = str_d29

        #----------------------- D30: ratio of transient to NCLOC ------------------------------ #

        transient1 = [re.findall('[\t\s\n]+transient ', line) for line in all_lines_nocomments]
        transient1_total = sum(transient1, [])
        num1 = len(transient1_total)

        transient2 = [re.findall('^transient ', line) for line in all_lines_nocomments]
        transient2_total = sum(transient2, [])
        num2 = len(transient2_total)

        transient3 = [re.findall('[=({]transient ', line) for line in all_lines_nocomments]
        transient3_total = sum(transient3, [])
        num3 = len(transient3_total)

        transient_total = num1 + num2 + num3

        result = transient_total/NCLOC
        result = round(result,3)

        str_d30 = str(result)
        keywords["D30: ratio of transient to NCLOC"] = str_d30

        #----------------------- D31: ratio of catch to NCLOC ------------------------------ #

        catch_stat = [re.findall('Catch Clause Count:\s(.*)', line) for line in all_lines_txtparsed]
        catch_total = sum(catch_stat, [])

        g = [elem.replace(" ", "") for elem in catch_total]

        catch_num = int(g[0])

        result = catch_num/NCLOC
        result = round(result,3)

        str_d31 = str(result)
        keywords["D31: ratio of catch to NCLOC"] = str_d31

        #----------------------- D32: ratio of extends to NCLOC ------------------------------ #

        extends_stat = [re.findall(' extends ', line) for line in all_lines_nocomments]
        extends_total = sum(extends_stat, [])
        extends_num = len(extends_total)

        result = extends_num/NCLOC
        result = round(result,3)

        str_d32 = str(result)
        keywords["D32: ratio of extends to NCLOC"] = str_d32

        #----------------------- D33: ratio of int to NCLOC ------------------------------ #

        int1 = [re.findall('[\t\s\n]+int ', line) for line in all_lines_nocomments]
        int1_total = sum(int1, [])
        num1 = len(int1_total)

        int2 = [re.findall('^int ', line) for line in all_lines_nocomments]
        int2_total = sum(int2, [])
        num2 = len(int2_total)

        int3 = [re.findall('[=({]int ', line) for line in all_lines_nocomments]
        int3_total = sum(int3, [])
        num3 = len(int3_total)

        int_total = num1 + num2 + num3

        result = int_total/NCLOC
        result = round(result,3)

        str_d33 = str(result)
        keywords["D33: ratio of int to NCLOC"] = str_d33

        #----------------------- D34: ratio of short to NCLOC ------------------------------ #

        short1 = [re.findall('[\t\s\n]+short ', line) for line in all_lines_nocomments]
        short1_total = sum(short1, [])
        num1 = len(short1_total)

        short2 = [re.findall('^short ', line) for line in all_lines_nocomments]
        short2_total = sum(short2, [])
        num2 = len(short2_total)

        short3 = [re.findall('[=({]short ', line) for line in all_lines_nocomments]
        short3_total = sum(short3, [])
        num3 = len(short3_total)

        short_total = num1 + num2 + num3

        result = short_total/NCLOC
        result = round(result,3)

        str_d34 = str(result)
        keywords["D34: ratio of short to NCLOC"] = str_d34

        #----------------------- D35: ratio of try to NCLOC ------------------------------ #

        try_stat = [re.findall('Try Statement Count:\s(.*)', line) for line in all_lines_txtparsed]

        try_total = sum(try_stat, [])

        g = [elem.replace(" ", "") for elem in try_total]

        try_num = int(g[0])

        result = try_num/NCLOC
        result = round(result,3)

        str_d35 = str(result)
        keywords["D35: ratio of try to NCLOC"] = str_d35

        #----------------------- D36: ratio of try to NCLOC ------------------------------ #

        char1 = [re.findall('[\t\s\n]+char ', line) for line in all_lines_nocomments]
        char1_total = sum(char1, [])
        num1 = len(char1_total)

        char2 = [re.findall('^char ', line)  for line in all_lines_nocomments]
        char2_total = sum(char2, [])
        num2 = len(char2_total)

        char3 = [re.findall('[=({]char ', line) for line in all_lines_nocomments]
        char3_total = sum(char3, [])
        num3 = len(char3_total)

        char_total = num1 + num2 + num3

        result = char_total/NCLOC
        result = round(result,3)

        str_d36 = str(result)
        keywords["D36: ratio of char to NCLOC"] = str_d36

        #----------------------- D37: ratio of final to NCLOC ------------------------------ #

        final1 = [re.findall('[\t\s\n]+final ', line) for line in all_lines_nocomments]
        final1_total = sum(final1, [])
        num1 = len(final1_total)

        final2 = [re.findall('^final ', line) for line in all_lines_nocomments]
        final2_total = sum(final2, [])
        num2 = len(final2_total)

        final3 = [re.findall('[=({]final ', line) for line in all_lines_nocomments]
        final3_total = sum(final3, [])
        num3 = len(final3_total)

        final_total = num1 + num2 + num3

        result = final_total/NCLOC
        result = round(result,3)

        str_d37 = str(result)
        keywords["D37: ratio of final to NCLOC"] = str_d37

        #----------------------- D38: ratio of interface to NCLOC ------------------------------ #

        inter1 = [re.findall('[\t\s\n]+interface ', line) for line in all_lines_nocomments]
        inter1_total = sum(inter1, [])
        num1 = len(inter1_total)

        inter2 = [re.findall('^interface ', line) for line in all_lines_nocomments]
        inter2_total = sum(inter2, [])
        num2 = len(inter2_total)

        inter3 = [re.findall('[=({]interface ', line) for line in all_lines_nocomments]
        inter3_total = sum(inter3, [])
        num3 = len(inter3_total)

        inter_total = num1 + num2 + num3

        result = inter_total/NCLOC
        result = round(result,3)

        str_d38 = str(result)
        keywords["D38: ratio of interface to NCLOC"] = str_d38

        #----------------------- D39: ratio of static to NCLOC ------------------------------ #

        stat1 = [re.findall('[\t\s\n]+static ', line) for line in all_lines_nocomments]
        stat1_total = sum(stat1, [])
        num1 = len(stat1_total)

        stat2 = [re.findall('^static ', line) for line in all_lines_nocomments]
        stat2_total = sum(stat2, [])
        num2 = len(stat2_total)

        stat3 = [re.findall('[=({]static ', line) for line in all_lines_nocomments]
        stat3_total = sum(stat3, [])
        num3 = len(stat3_total)

        stat_total = num1 + num2 + num3

        result = stat_total/NCLOC
        result = round(result,3)

        str_d39 = str(result)
        keywords["D39: ratio of static to NCLOC"] = str_d39

        #----------------------- D40: ratio of void to NCLOC ------------------------------ #

        void_stat = [re.findall('Void Type Count:\s(.*)', line) for line in all_lines_txtparsed]
        void_total = sum(void_stat, [])

        g = [elem.replace(" ", "") for elem in void_total]

        void_num = int(g[0])

        result = void_num/NCLOC
        result = round(result,3)

        str_d40 = str(result)
        keywords["D40: ratio of void to NCLOC"] = str_d40

        #----------------------- D41: ratio of class to NCLOC ------------------------------ #

        class1 = [re.findall('[\t\s\n]+class ', line) for line in all_lines_nocomments]
        class1_total = sum(class1, [])
        num1 = len(class1_total)

        class2 = [re.findall('^class ', line) for line in all_lines_nocomments]
        class2_total = sum(class2, [])
        num2 = len(class2_total)

        class3 = [re.findall('[=({]class ', line) for line in all_lines_nocomments]
        class3_total = sum(class3, [])
        num3 = len(class3_total)

        class_total = num1 + num2 + num3

        result = class_total/NCLOC
        result = round(result,3)

        str_d41 = str(result)
        keywords["D41: ratio of class to NCLOC"] = str_d41

        #----------------------- D42: ratio of finally to NCLOC ------------------------------ #

        finally1 = [re.findall('[\t\s\n]+finally ', line) for line in all_lines_nocomments]
        finally1_total = sum(finally1, [])
        num1 = len(finally1_total)

        finally2 = [re.findall('^finally ', line) for line in all_lines_nocomments]
        finally2_total = sum(finally2, [])
        num2 = len(finally2_total)

        finally3 = [re.findall('[=({]finally ', line) for line in all_lines_nocomments]
        finally3_total = sum(finally3, [])
        num3 = len(finally3_total)

        finally_total = num1 + num2 + num3

        result = finally_total/NCLOC
        result = round(result,3)

        str_d42 = str(result)
        keywords["D42: ratio of finally to NCLOC"] = str_d42

        #----------------------- D43: ratio of long to NCLOC ------------------------------ #

        long1 = [re.findall('[\t\s\n]+finally ', line) for line in all_lines_nocomments]
        long1_total = sum(long1, [])
        num1 = len(long1_total)

        long2 = [re.findall('[\t\s\n]+finally ', line) for line in all_lines_nocomments]
        long2_total = sum(long2, [])
        num2 = len(long2_total)

        long3 = [re.findall('[\t\s\n]+finally ', line) for line in all_lines_nocomments]
        long3_total = sum(long3, [])
        num3 = len(long3_total)

        long_total = num1 + num2 + num3

        result = long_total/NCLOC
        result = round(result,3)

        str_d43 = str(result)
        keywords["D43: ratio of long to NCLOC"] = str_d43

        #----------------------- D44: ratio of strictfp to NCLOC ------------------------------ #

        strictfp1 = [re.findall('[\t\s\n]+strictfp ', line) for line in all_lines_nocomments]
        strictfp1_total = sum(strictfp1, [])
        num1 = len(strictfp1_total)

        strictfp2 = [re.findall('^strictfp ', line) for line in all_lines_nocomments]
        strictfp2_total = sum(strictfp2, [])
        num2 = len(strictfp2_total)

        strictfp3 = [re.findall('[=({]strictfp ', line) for line in all_lines_nocomments]
        strictfp3_total = sum(strictfp3, [])
        num3 = len(strictfp3_total)

        strictfp_total = num1 + num2 + num3

        result = strictfp_total/NCLOC
        result = round(result,3)

        str_d44 = str(result)
        keywords["D44: ratio of strictfp to NCLOC"] = str_d44

        #----------------------- D45: ratio of volatile to NCLOC ------------------------------ #

        volatile1 = [re.findall('[\t\s\n]+volatile ', line) for line in all_lines_nocomments]
        volatile1_total = sum(volatile1, [])
        num1 = len(volatile1_total)

        volatile2 = [re.findall('^volatile ', line) for line in all_lines_nocomments]
        volatile2_total = sum(volatile2, [])
        num2 = len(volatile2_total)

        volatile3 = [re.findall('[=({]volatile ', line) for line in all_lines_nocomments]
        volatile3_total = sum(volatile3, [])
        num3 = len(volatile3_total)

        volatile_total = num1 + num2 + num3

        result = volatile_total/NCLOC
        result = round(result,3)

        str_d45 = str(result)
        keywords["D45: ratio of volatile to NCLOC"] = str_d45


        #----------------------- D46: ratio of const to NCLOC ------------------------------ #

        const1 = [re.findall('[\t\s\n]+const ', line) for line in all_lines_nocomments]
        const1_total = sum(const1, [])
        num1 = len(const1_total)

        const2 = [re.findall('^const ', line) for line in all_lines_nocomments]
        const2_total = sum(const2, [])
        num2 = len(const2_total)

        const3 = [re.findall('[=({]const ', line) for line in all_lines_nocomments]
        const3_total = sum(const3, [])
        num3 = len(const3_total)

        const_total = num1 + num2 + num3

        result = const_total/NCLOC
        result = round(result,3)

        str_d46 = str(result)
        keywords["D46: ratio of const to NCLOC"] = str_d46

        #----------------------- D47: ratio of float to NCLOC ------------------------------ #

        float1 = [re.findall('[\t\s\n]+float ', line) for line in all_lines_nocomments]
        float1_total = sum(float1, [])
        num1 = len(float1_total)

        float2 = [re.findall('^float ', line) for line in all_lines_nocomments]
        float2_total = sum(float2, [])
        num2 = len(float2_total)

        float3 = [re.findall('[=({]float ', line) for line in all_lines_nocomments]
        float3_total = sum(float3, [])
        num3 = len(float3_total)

        float_total = num1 + num2 + num3

        result = float_total/NCLOC
        result = round(result,3)

        str_d47 = str(result)
        keywords["D47: ratio of float to NCLOC"] = str_d47

        #----------------------- D48: ratio of native to NCLOC ------------------------------ #

        native1 = [re.findall('[\t\s\n]+native ', line) for line in all_lines_nocomments]
        native1_total = sum(native1, [])
        num1 = len(native1_total)

        native2 = [re.findall('^native ', line) for line in all_lines_nocomments]
        native2_total = sum(native2, [])
        num2 = len(native2_total)

        native3 = [re.findall('[=({]native ', line) for line in all_lines_nocomments]
        native3_total = sum(native3, [])
        num3 = len(native3_total)

        native_total = num1 + num2 + num3

        result = native_total/NCLOC
        result = round(result,3)

        str_d48 = str(result)
        keywords["D48: ratio of native to NCLOC"] = str_d48

        #----------------------- D49: ratio of super to NCLOC ------------------------------ #

        super_stat = [re.findall('Super Expression Count:\s(.*)', line) for line in all_lines_txtparsed]
        super_total = sum(super_stat, [])

        g = [elem.replace(" ", "") for elem in super_total]

        super_num = int(g[0])

        result = super_num/NCLOC
        result = round(result,3)

        str_d49 = str(result)
        keywords["D49: ratio of super to NCLOC"] = str_d49

        #----------------------- D50: ratio of while to NCLOC ------------------------------ #

        while_stat = [re.findall('While Statement Count:(.*)', line) for line in all_lines_txtparsed]
        while_total = sum(while_stat, [])

        g = [elem.replace(" ", "") for elem in while_total]

        while_num = int(g[0])

        result = while_num/NCLOC
        result = round(result,3)

        str_d50 = str(result)
        keywords["D50: ratio of while to NCLOC"] = str_d50

        # Write results to a .keyword file for each Java file ----------------------- #

        relative_path = java_file.replace(main_directory, "")
        java_file_name = relative_path.split(separator)[-1]

        keyword_str = str()
        for key in keywords:
            keyword_str = keyword_str + key+ " === " + keywords[key] + "\n"

        path = separator.join(java_file.split(separator)[:-1])
        results_filename = path + separator + java_file_name[:-5] + ".keyword"

        with io.open(results_filename, 'w') as waf:
            waf.write(keyword_str)

        all_keywords_dicts.append(keywords)

    # Sum results from each Java file + write to file per author ----------------------- #

    # Only want to construct this list once (since all categories are the same across the files)
    if len(all_keywords) == 0:
        # All keys are the same across the java files
        for key in all_keywords_dicts[0]:
            all_keywords.append(key)

    all_keywords_dict = {key: float(0) for key in all_keywords}

    # Sum up frequencies across all java files in author folder
    for dictionary in all_keywords_dicts:
        for key in dictionary:
            all_keywords_dict[key] = all_keywords_dict[key] + float(dictionary[key])

    # For each author, write the author term frequencies to an arff file
    author_name = author.split(separator)[-1]

    # Generate an .arff file of unigram term frequencies for each author
    author_keyword_str = str()
    for key in all_keywords_dict:
        author_keyword_str = author_keyword_str + key+ " === " + str(all_keywords_dict[key]) + "\n"

    results_filename = author + separator + author_name + "_keywords.arff"
    with io.open(results_filename, 'w') as waf:
        waf.write(author_keyword_str)
