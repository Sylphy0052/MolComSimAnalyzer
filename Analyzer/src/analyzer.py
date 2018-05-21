from enum import Enum
import sys

COLOR_LIST = ['r', 'b', 'g', 'm', 'y', 'k', 'c', 'r', 'b', 'g', 'm', 'y', 'k', 'c']
STYLE_LIST = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', '-.', ':', '-']

class XValue(Enum):
   DISTANCE = 0
   DUPLICATION = 1
   ALL = 2

class YValue(Enum):
    MEAN = 0

class Mode(Enum):
    pass



class Analyzer:
    def __init__(self, dataDict, allFileList):
        self.dataDict = dataDict
        self.allFileList = allFileList

    def getValue(self, data, value):
        if value is XValue.DISTANCE:
            return data.getDistance()
        elif value is YValue.MEAN:
            return data.getMean()
        elif value is XValue.DUPLICATION:
            return data.getTxDuplication()
        else:
            print("Not Define")
            sys.exit(1)

    def getLabel(self, data, value):
        if value is XValue.DISTANCE:
            return "d={}".format(data.getDistance())
        elif value is XValue.Duplication:
            return "".format("SW-ARQ{}-{}".format(data.getTxDuplication(), data.getTxDuplication()))
        else:
            print("Not Define")
            sys.exit(1)

    def classifyDataFile(self, fileList, labelValue):
        if labelValue is XValue.ALL:
            return [self.allFileList]

        labels = []

        # make labels
        for fileName in fileList:
            data = self.dataDict[fileName]
            label = self.getValue(data, labelValue)

            if label in labels:
                pass
            else:
                labels.append(label)

        classifyFiles = [[] for i in range(len(labels))]

        for fileName in fileList:
            data = self.dataDict[fileName]
            label = self.getValue(data, labelValue)
            for i in range(len(labels)):
                if labels[i] == label:
                    classifyFiles[i].append(fileName)

        return classifyFiles

    def getLabelValues(self, xValue, yValue, labelValue, fileList):
        X = []
        labels = []

        for fileName in fileList:
            print(fileName)
            data = self.dataDict[fileName]
            x = self.getValue(data, xValue)
            label = self.getValue(data, labelValue)
            if not x in X:
                X.append(x)
            if not label in labels:
                labels.append(label)

        Y = [[] for i in range(len(labels))]
        for fileName in fileList:
            data = self.dataDict[fileName]
            x = self.getValue(data, xValue)
            y = self.getValue(data, yValue)
            label = self.getValue(data, labelValue)
            for i in range(len(labels)):
                if label == labels[i]:
                    Y[i].append(y)
                    continue
        return [X, Y, labels]

    def drawSpecificGraph(self, xValue, yValue, labelValue, classifyValue):
        # グラフことにファイル名を分ける
        classifyFileList = self.classifyDataFile(self.allFileList, classifyValue)

        for fileList in classifyFileList:
            X, Y, labels = self.getLabelValues(xValue, yValue, labelValue, fileList)




    def drawGraph(self):
        self.drawSpecificGraph(XValue.DISTANCE, YValue.MEAN, XValue.DUPLICATION, XValue.ALL)
