import io
import sys
import os
from collections import OrderedDict
import urllib
import pathlib


def slidingWindow(sequence, winSize, step=1):
    """Returns a generator that will iterate through
    the defined chunks of input sequence.  Input sequence
    must be iterable."""

    temp = list()

    # Verify the inputs
    if not ((type(winSize) == type(0)) and (type(step) == type(0))):
        raise Exception("**ERROR** type(winSize) and type(step) must be int.")

    if step > winSize:
        raise Exception("**ERROR** step must not be larger than winSize.")

    if winSize > len(sequence):
        # raise Exception("**ERROR** winSize must not be larger than sequence length.")
        temp = []
    else:
        try:
            it = iter(sequence)
        except TypeError:
            raise Exception("**ERROR** sequence must be iterable.")

        # Pre-compute number of chunks to emit
        numOfChunks = int(((len(sequence) - winSize) / step) + 1)

        # Do the work
        for i in range(0, numOfChunks * step, step):
            # yield sequence[i:i+winSize]
            temp.append(sequence[i:i + winSize])

    return (temp)


def absoluteFilePaths(directory):
    result = list()
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            result.append(os.path.abspath(os.path.join(dirpath, f)))
    return (result)


ext_py = ["py",  # Python
          ]

ext_c = ["c",  # C
         ]

ext_cpp = ["c++",  # C-plus-plus
           "cpp",  # C-plus-plus
           ]

ext_java = ["java",  # java
            ]

ext_cs = ["c#",  # C sharp
          "cs",  # C sharp
          ]

ext_rb = ["rb",  # ruby
          ]

ext_go = ["go",  # Golang
          ]

ext_pas = ["pas",  # Pascal
           ]

ext_js = ["js",  # Javascript
          ]

ext_lua = ["lua",  # LUA
           ]

ext_swift = ["swift",  # SWIFT
             ]

ext_r = ["r",  # R
         ]

ext_er = ["erl",  # Erlang
          ]

ext_kot = ["kt",  # Kotlin
           ]

ext_has = ["hs",  # Haskell
           ]

ext_cof = ["coffee",  # Coffee
           ]

ext_lisp = ["lisp",  # LISP
            ]

ext_php = ["php",  # PHP
           ]

ext_pl = ["pl",  # Perl
          ]

ext_ts = ["ts",  # TypeScript
          ]

ext_css = ["css",  # CSS
           ]

ext_s = ["s",  # S
         ]

ext_gro = ["groovy",  # groovy
           ]

ext_tcl = ["tcl",  # groovy
           ]

ext_cmake = ["cmake",  # cmake
             ]

ext_dart = ["dart",  # dart
            ]

ext_f90 = ["f90",  # fortran
           ]

ext_gradle = ["gradle",  # gradle
              ]

ext_m = ["m",  # objective-c
         ]

ext_ps1 = ["ps1",  # powershell
           ]

ext_pro = ["pro",  # prolog
           ]

ext_rs = ["rs",  # rust
          ]

ext_smali = ["smali",  # smali
             ]

ext_v = ["v",  # verilog
         ]

extensions = ext_py + ext_cpp + ext_java + ext_cs + ext_rb + ext_go + \
             ext_pas + ext_js + ext_lua + ext_swift + ext_r + ext_er + \
             ext_kot + ext_has + ext_c + ext_cof + ext_lisp + ext_php + \
             ext_pl + ext_ts + ext_css + ext_s + ext_gro + ext_tcl + \
             ext_cmake + ext_dart + ext_f90 + ext_gradle + ext_m + ext_ps1 + \
             ext_pro + ext_rs + ext_smali + ext_v

languages = {"python": ext_py,
             "c": ext_c,
             "c++": ext_cpp,
             "java": ext_java,
             "c#": ext_cs,
             "ruby": ext_rb,
             "go": ext_go,
             "pascal": ext_pas,
             "javascript": ext_js,
             "lua": ext_lua,
             "swift": ext_swift,
             "r": ext_r,
             "erlang": ext_er,
             "kotlin": ext_kot,
             "haskell": ext_has,
             "coffee": ext_cof,
             "lisp": ext_lisp,
             "php": ext_php,
             "perl": ext_pl,
             "typescript": ext_ts,
             "css": ext_css,
             "s": ext_s,
             "groovy": ext_gro,
             "tcl": ext_tcl,
             "cmake": ext_cmake,
             "dart": ext_dart,
             "fortran": ext_f90,
             "gradle": ext_gradle,
             "objective-c": ext_m,
             "powershell": ext_ps1,
             "prolog": ext_pro,
             "rust": ext_rs,
             "smali": ext_smali,
             "verilog": ext_v,
             }

main_folder = str(sys.argv[-1])

mapping_file = main_folder + "_mapping.txt"
outfile_all = main_folder + "_res_sw_xf_all" + ".txt"
outfile_all_gt1 = main_folder + "_res_sw_xf_all_gt1" + ".txt"
outfile_all_gt1_t50 = main_folder + "_res_sw_xf_all_gt1_t50" + ".txt"
outfile_all_t50 = main_folder + "_res_sw_xf_all_t50" + ".txt"

if "\\" in main_folder:
    separator = "\\"
else:
    separator = "/"

# ============================================================================
print("Processing forlder: ", main_folder)

# outfile_all 
with io.open(outfile_all, 'w') as wof:
    wof.write("")

# check if DIR is there
if not os.path.isdir(main_folder):
    raise AssertionError("ERROR: input folder NOT found")

all_files = list()

for path, subdirs, files in os.walk(main_folder):
    for name in files:
        all_files.append(pathlib.PurePath(path, name))

bytes_seen = OrderedDict()
byteid = 10000

for item in all_files:

    ext = str(item).split(".")[1]

    if not ext in extensions:
        continue

    with io.open(item, "rb") as f:
        data = f.read()

    chunks = slidingWindow(data, 4)

    if not chunks:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(item)
        print(repr(data))
        print(chunks)
        raise AssertionError("ERROR - chunks list is empty")

    bgrams_count = OrderedDict()
    for xx in chunks:

        encoded = urllib.parse.quote_plus(xx)

        if not encoded in bytes_seen:
            bytes_seen[encoded] = str(byteid)
            byteid = byteid + 1

        if encoded in bgrams_count:
            bgrams_count[encoded] = bgrams_count[encoded] + 1
        else:
            bgrams_count[encoded] = 1

    sorted_x = sorted(bgrams_count.items(), key=lambda kv: kv[1], reverse=True)
    sorted_dict = OrderedDict(sorted_x)

    res_list = list()
    for k, v in sorted_dict.items():
        # code, gram, count
        lres = [str(bytes_seen[k]), str(k), str(v)]

        res = ":".join(lres)
        res_list.append(res)

    relpath = str(item).replace(main_folder, "")
    end_line = " # " + relpath
    final = ",".join(res_list) + end_line

    with io.open(outfile_all, 'a') as waf:
        waf.write(final + "\n")

    print("Processed: ", item)

with io.open(mapping_file, 'w') as wmf:
    for k, v in bytes_seen.items():
        mline = "%s\t%s\n" % (v, k)
        wmf.write(mline)

print(byteid)

# ============================================================================

print("Processing grams with count >1")
print("File : ", outfile_all)

with io.open(outfile_all_gt1, 'w') as wif:
    wif.write("")

found = 0
parsed = 0
with io.open(outfile_all, 'r') as rif:
    for line in rif:
        xline = line.replace("\n", "").strip()
        if xline and (" # " in xline):

            found = found + 1

            relpath = xline.split(" # ")[1].replace("\n", "").strip()

            owner = relpath.split(separator)[-3]

            chunks = xline.split(" # ")[0].split(",")

            chunks_keep = list()
            for item in chunks:

                code = item.split(":")[0]
                data = item.split(":")[1]
                count = int(item.split(":")[2])
                xk = "%s:%s" % (code, data)

                if count > 1:
                    chunks_keep.append(item)

            if len(chunks_keep) > 0:

                jres = ",".join(chunks_keep)
                line = jres + " # " + relpath
                final = line + "\n"

                with io.open(outfile_all_gt1, 'a') as wif:
                    wif.write(final)

                parsed = parsed + 1

            else:
                print("Chunk len 0: ", relpath)

print("Files - found: ", found)
print("Files - parsed: ", parsed)
print("Files - skipped: ", int(found - parsed))

# ============================================================================

print("Processing grams with count >1, pick top 50")
print("File : ", outfile_all)

with io.open(outfile_all_gt1_t50, 'w') as wif:
    wif.write("")

found = 0
parsed = 0
with io.open(outfile_all, 'r') as rif:
    for line in rif:
        xline = line.replace("\n", "").strip()
        if xline and (" # " in xline):

            found = found + 1

            relpath = xline.split(" # ")[1].replace("\n", "").strip()

            owner = relpath.split(separator)[-3]

            chunks = xline.split(" # ")[0].split(",")

            chunks_keep = list()
            for item in chunks:

                code = item.split(":")[0]
                data = item.split(":")[1]
                count = int(item.split(":")[2])
                xk = "%s:%s" % (code, data)

                if count > 1:
                    chunks_keep.append(item)

            if len(chunks_keep) == 0:
                print("Chunk len 0: ", relpath)
            else:
                if len(chunks_keep) > 50:
                    cres = chunks[0:50]

                    jres = ",".join(cres)
                    line = jres + " # " + relpath
                    final = line + "\n"

                else:
                    jres = ",".join(chunks_keep)
                    line = jres + " # " + relpath
                    final = line + "\n"

                with io.open(outfile_all_gt1_t50, 'a') as wif:
                    wif.write(final)

                parsed = parsed + 1

print("Files - found: ", found)
print("Files - parsed: ", parsed)
print("Files - skipped: ", int(found - parsed))

# ============================================================================

print("Processing grams, pick top 50")
print("File : ", outfile_all)

with io.open(outfile_all_t50, 'w') as wif:
    wif.write("")

found = 0
parsed = 0
with io.open(outfile_all, 'r') as rif:
    for line in rif:
        xline = line.replace("\n", "").strip()
        if xline and (" # " in xline):

            found = found + 1

            relpath = xline.split(" # ")[1].strip()
            chunks = xline.split(" # ")[0].split(",")

            if len(chunks_keep) == 0:
                print("Chunk len 0: ", relpath)
            else:
                if len(chunks_keep) > 50:
                    cres = chunks[0:50]

                    jres = ",".join(cres)
                    line = jres + " # " + relpath
                    final = line + "\n"

                else:
                    jres = ",".join(chunks_keep)
                    line = jres + " # " + relpath
                    final = line + "\n"

                with io.open(outfile_all_t50, 'a') as wif:
                    wif.write(final)

                parsed = parsed + 1

print("Files - found: ", found)
print("Files - parsed: ", parsed)
print("Files - skipped: ", int(found - parsed))

# ============================================================================

sys.exit()
