import os
import pickle
from natsort import natsorted
import glob
from data import AllData
from analyzer import Analyzer

PICKLE_FILE = '../pickle.txt'
DAT_PATH = '../dat/*.dat'


def createDataDict(allFileList):
    dataDict = {}
    # if os.path.isfile(PICKLE_FILE):
    #     with open(PICKLE_FILE, 'rb') as f:
    #         dataDict = pickle.load(f)
    # else:
    count = 1
    for fileName in allFileList:
        print("{} / {} - {} file reading...".format(count, len(allFileList), fileName.split("/")[2]))
        dataDict[fileName] = AllData(fileName)
        count += 1
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(dataDict, f)


    return dataDict


def main():
    allFileList = natsorted(glob.glob(DAT_PATH))
    dataDict = createDataDict(allFileList)
    analyzer = Analyzer(dataDict, allFileList)


if __name__ == "__main__":
    main()
