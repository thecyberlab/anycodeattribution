import io
import os
import hashlib
import zlib
import math
from skimage.feature import local_binary_pattern
import collections
import sys

import ntpath
import os.path
import csv
import numpy as np
from skimage.feature import graycomatrix, graycoprops
from skimage import io as ioski

from chardet.universaldetector import UniversalDetector

input_Dataset = str(sys.argv[-1])
preprocess_file_stats = input_Dataset + "_IG_stats.csv"

# ============================================================================
# settings for LBP
radius = 3
n_points = 8 * radius
METHOD = 'uniform'

def highlight_bars(bars, indexes):
    for i in indexes:
        bars[i].set_facecolor('r')

def absoluteFilePaths(directory):
    result = list()
    for dirpath ,_ ,filenames in os.walk(directory):
        for f in filenames:
            result.append(os.path.abspath(os.path.join(dirpath, f)))
    return(result)

def dirwalk_depth1(top):
    dirs, nondirs = [], []
    for name in os.listdir(top):
        (dirs if os.path.isdir(os.path.join(top, name)) else nondirs).append(name)
    return(top, dirs, nondirs)

def get_file_hash(file_abspath):

    # BUF_SIZE to read data in chunks of 64kb
    BUF_SIZE = 65536

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()

    with io.open(file_abspath, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
            sha256.update(data)
    result = [md5.hexdigest().upper(),
              sha1.hexdigest().upper(),
              sha256.hexdigest().upper()]
    return(result)

def file_len(fname):
    lines = 0
    with io.open(fname, 'r', encoding="utf-8", errors="ignore") as f:
        for line in f:
            lines = lines + 1
    return(lines)


def guess_chardet(file_abspath):

    detector = UniversalDetector()
    with io.open(file_abspath, 'rb') as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    chardet_result = detector.result
    encoding = chardet_result["encoding"]
    confidence = chardet_result["confidence"]
    result = [encoding, confidence]
    return(result)


def get_crc32(fileName):
    prev = 0
    for eachLine in io.open(fileName ,"rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X " %(prev & 0xFFFFFFFF)

def shannon_entropy(file_abspath):

    # read the whole file into a byte array
    with io.open(file_abspath, "rb") as f:
        # byteArr = map(ord, f.read())
        byteArr = list(f.read())
    fileSize = len(byteArr)

    freqList = []
    for b in range(256):
        ctr = 0
        for byte in byteArr:
            if byte == b:
                ctr += 1
        freqList.append(float(ctr) / fileSize)

    ent = 0.0
    for freq in freqList:
        if freq > 0:
            ent = ent + freq * math.log(freq, 2)
    ent = round(-ent, 4)
    return(ent)

def zlib_compratio(file_abspath):

    with io.open(file_abspath, "rb") as f:
        data = f.read()

    comp = len(zlib.compress(data))
    fsize = os.stat(item).st_size

    # ratio of file sizes: (size-of-gzipped)/(size-of-original)
    ratio = round((comp / fsize), 4)
    return(ratio)

def get_allsubdirs(directory):
    result = [x[0] for x in os.walk(directory)]
    return(result)

def CountFrequency(arr):
    return collections.Counter(arr)

# ============================================================================

# CREATE DIRECTORY STRUCTURE

subfolders_by_lines = ["0-1",
                       "2-5",
                       "6-10",
                       "11-20",
                       "21-30",
                       "31-40",
                       "41-50",
                       "51-60",
                       "61-70",
                       "71-80",
                       "81-90",
                       "91-100",
                       "101-200",
                       "201-300",
                       "301-400",
                       "401-500",
                       "501-1000",
                       "1001-3000",
                       "3001-up" ,]

# get 1-level deep subfolders to get authors
wtop, walldirs, wnondirs = dirwalk_depth1(input_Dataset)

# get list of files
xall_files = absoluteFilePaths(input_Dataset)
all_files = list()
for item in xall_files:
    if not item.endswith(".png"):
        all_files.append(item)

xall_files = None
del(xall_files)

csv_head = "FilePath,Basename,Author,Extension,Encoding,Confidence,Shannon,Height,Width,"
csv_head = csv_head +  "L1,L2,L3,L4,L5,L6,L7,L8,L9,L10,L11,L12,L13,L14,L15,L16,L17,L18,L19,L20,L21,L22,L23,L24,L25,L26,L27,L28,L29,L30,L31,L32,L33,L34,L35,L36,L37,L38,L39,L40,L41,L42,L43,L44,L45,L46,L47,L48,L49"
with io.open(preprocess_file_stats, 'w') as wlf:
    wlf.write(csv_head + "\n")

print("Parsing is started")
for item in all_files:

    bname = ntpath.basename(item)
    ext = bname.split(".")[1]
    author = item.replace(input_Dataset, "").split("/")[-3]
    # guess character-set
    charset = guess_chardet(item)
    guess_enc = charset[0]
    guess_conf = charset[1]

    imageAddr = item.split(".")[0] +"_IGFilter_L" +".png"
    shan_ent = shannon_entropy(imageAddr)
    grayImg = ioski.imread(imageAddr)

    image = ioski.imread(imageAddr)
    lbp = local_binary_pattern(image, n_points, radius, METHOD)

    lbpList = list()

    freq = collections.OrderedDict(sorted(CountFrequency(lbp.ravel()).items()))
    count = 0.0
    for count in range(0 ,25):
        lbpList.append(freq.get(count, 0))

    height = grayImg.shape[0]
    width = grayImg.shape[1]

    result = [item, bname, author ,ext, guess_enc, guess_conf, shan_ent ,height ,width  ]
    distances = [1, 2, 3 ,4]
    angles = [0  ]  # , np.pi/4, np.pi/2, 3*np.pi/4]

    properties = ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation', 'ASM']

    glcm = graycomatrix(grayImg,
                        distances=distances,
                        angles=angles,
                        symmetric=True,
                        normed=True)

    feats = np.hstack([graycoprops(glcm, prop).ravel() for prop in properties])
    result = result + (feats.tolist())  # + str(glcm.max()).tolist()
    result = result + lbpList

    # open the csv file as write, OVERWRITE AT EACH RUN
    with io.open(preprocess_file_stats, 'a') as outcsv:
        # configure writer to write standard csv file
        writer = csv.writer(outcsv,
                            delimiter=',',
                            quotechar='|',
                            quoting=csv.QUOTE_MINIMAL,
                            lineterminator='\n')

        # WRITE CSV ROWS
        writer.writerow(result)

print("Parsing is done")