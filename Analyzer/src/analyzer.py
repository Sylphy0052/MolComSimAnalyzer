from enum import Enum
import sys, os
import matplotlib.pyplot as plt
from matplotlib import ticker

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
        print("Analyze Datas")
        self.dataDict = dataDict
        self.allFileList = allFileList

    def getValue(self, data, value):
        if value is XValue.DISTANCE:
            return data.getDistance()
        elif value is XValue.DUPLICATION:
            return data.getTxDuplication()
        elif value is YValue.MEAN:
            return data.getMean()
        else:
            print("Not Define")
            sys.exit(1)

    def getLabel(self, data, value):
        if value is XValue.DISTANCE:
            return "d={}".format(data.getDistance())
        elif value is XValue.DUPLICATION:
            return "SW-ARQ{}-{}".format(data.getTxDuplication(), data.getTxDuplication())
        else:
            print("Not Define {} in getLabel".format(value.name))
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
            label = self.getLabel(data, labelValue)
            if not x in X:
                X.append(x)
            if not label in labels:
                labels.append(label)

        Y = [[] for i in range(len(labels))]
        for fileName in fileList:
            data = self.dataDict[fileName]
            y = self.getValue(data, yValue)
            label = self.getLabel(data, labelValue)
            for i in range(len(labels)):
                if label == labels[i]:
                    Y[i].append(y)
                    continue

        return [X, Y, labels]

    def defineDirectoryPath(self, xValue, yValue, classifyValue):
        dirPath = "../compare{}_by_{}".format(yValue.name, xValue.name)
        if classifyValue is not XValue.ALL:
            dirPath += "_each_{}".format(classifyValue.name)
        dirPath = dirPath.lower()

        if not os.path.isdir(dirPath):
            os.makedirs(dirPath)

        return dirPath

    def defineFigName(self, classifyValue, data):
        figName = ""
        if classifyValue is XValue.ALL:
            figName = "all.png"
        else:
            if classifyValue is XValue.DISTANCE:
                figName = "TxRx{}.png".format(data.getDistance())
            else:
                print("Not Define {} in defineFigName".format(classifyValue.name))
                sys.exit(1)

        return figName

    def defineXlabel(self, xValue):
        if xValue is XValue.DISTANCE:
            return "Tx-Rx distance(um)"
        else:
            print("Not define {} in defineXlabel".format(xValue.name))
            sys.exit(1)

    def defineYlabel(self, yValue):
        if yValue is YValue.MEAN:
            return "Mean RTT (s)"
        else:
            print("Not define {} in defineYlabel".format(yValue.name))
            sys.exit(1)


    def drawLineGraph(self, X, Y, labels, xValue, yValue, isMath, figName):
        for i in range(len(Y)):
            plt.plot(X, Y[i], color=COLOR_LIST[i], label=labels[i], markersize="5", linestyle=STYLE_LIST[i])

        if xValue is XValue.DISTANCE:
            plt.xticks(X)
            plt.legend(loc='upper left')
        else:
            print("Not define {} in drawLineGraph".format(xValue.name))
            sys.exit(1)

        plt.xlabel(self.defineXlabel(xValue))
        plt.ylabel(self.defineYlabel(yValue))
        plt.grid(True)

        if isMath:
            plt.gca().yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
            plt.gca().ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

        plt.savefig(figName)
        plt.close('all')

    def drawSpecificGraph(self, xValue, yValue, labelValue, classifyValue):
        dirName = self.defineDirectoryPath(xValue, yValue, classifyValue)
        print("Make figure in {}".format(dirName))
        # グラフことにファイル名を分ける
        classifyFileList = self.classifyDataFile(self.allFileList, classifyValue)

        for fileList in classifyFileList:
            figName = dirName + "/" + self.defineFigName(classifyValue, self.dataDict[fileList[0]])
            print("Make figure {}".format(figName))
            X, Y, labels = self.getLabelValues(xValue, yValue, labelValue, fileList)
            isMath = False
            if max(max(Y)) > 10 ** 5:
                isMath = True

            self.drawLineGraph(X, Y, labels, xValue, yValue, isMath, figName)
        print("Finish making figure in {}".format(dirName))



    def drawGraph(self):
        self.drawSpecificGraph(XValue.DISTANCE, YValue.MEAN, XValue.DUPLICATION, XValue.ALL)
