import numpy as np
from enum import Enum
import os, re, sys, math

class AllData:
    def __init__(self, fileName):
        self.datFileName = fileName
        self.datData = DatData(self.datFileName)
        outputFileName = self.datData.config["outputFile"].strip()
        self.resultData = ResultData(outputFileName)
        self.adjustData = AdjustData(outputFileName)
        self.collisionData = CollisionData(outputFileName)
        self.retransmitData = RetransmitData(outputFileName)

    def getDistance(self):
        txPos = self.datData.config["transmitter"].centerPosition
        rxPos = self.datData.config["receiver"].centerPosition
        return int(txPos.calcDistance(rxPos))

    def getMean(self):
        return self.resultData.mean_

    def getMedian(self):
        return self.resultData.med_

    def getJitter(self):
        return self.resultData.std_

    def getTxDuplication(self):
        moleculeParams = self.datData.config["moleculeParams"]
        for mp in moleculeParams:
            if mp.typeOfMolecule is MoleculeType.INFO:
                return mp.duplication

    def getRetransmissionPlotData(self):
        Y = self.retransmitData.retransmitNumData
        X = np.arange(0, len(Y), 1, dtype=int)

        return X, Y

    def getCollisionPlotData(self):
        y = self.collisionData.collisionNumData
        yMax = np.max(y)
        step = 1000
        X = np.arange(0, yMax + step, step, dtype=int)
        Y = []

        for i in range(len(X) - 1):
            start = X[i]
            end = X[i + 1]
            tmp = [j for j in y if j > start and j <= end]
            Y.append(len(tmp))
        Y.append(0)

        return X, Y

    def getCollisionNum(self):
        return self.collisionData.collisionSum / len(self.collisionData.collisionStep)

    def getRetransmissionNum(self):
        return sum(self.retransmitData.retransmitNum) / len(self.retransmitData.retransmitStep)

class DatData:
    def __init__(self, fileName):
        self.fileName = fileName
        self.parseFile()

    def parseFile(self):
        self.config = {}
        self.config["moleculeParams"] = []
        self.config["microtubuleParams"] = []
        with open(self.fileName, 'r') as f:
            for line in f:
                if line[0] == '*' or line[0] == '\n':
                    continue
                key, val = line.split(' ', 1)
                if key in ["transmitter", "receiver"]:
                    self.config[key] = NanoMachine(val)
                elif key in ["intermediateNode"]:
                    self.config[key] = IntermediateNode(val)
                elif key in ["moleculeParams"]:
                    self.config[key].append(MoleculeParams(val))
                elif key in ["microtubuleParams"]:
                    self.config[key].append(MicrotubuleParams(val))
                elif key in ["probDRail", "stepLengthX", "stepLengthY", "stepLengthZ",
                             "packetStepLengthX", "packetStepLengthY", "packetStepLengthZ",
                             "packetDiameter"]:
                    self.config[key] = float(val)
                elif key in ["outputFile"]:
                    self.config[key] = val
                elif key in ["FEC"]:
                    self.config[key] = FEC(val)
                else:
                    self.config[key] = int(val)


class AdjustData:
    def __init__(self, fileName):
        self.fileName = "../result/adjust_batch_" + fileName
        if not os.path.isfile(self.fileName):
            return
        self.parseFile()
        # self.createGraphData()

    def parseFile(self):
        self.adjustStep = []
        self.adjustNumTx = []
        self.adjustNumRx = []

        with open(self.fileName, 'r') as f:
            for line in f:
                steps = []
                adjustTx = []
                adjustRx = []

                datas = line.split(',')
                for data in datas:
                    step, tx, rx = data.split('/')
                    steps.append(int(step))
                    adjustTx.append(int(tx))
                    adjustRx.append(int(rx))

                self.adjustStep.append(steps)
                self.adjustNumTx.append(adjustTx)
                self.adjustNumRx.append(adjustRx)

class ResultData:
    def __init__(self, fileName):
        self.fileName = "../result/batch_" + fileName
        self.parseFile()

        self.min_ = np.min(self.steps)
        self.max_ = np.max(self.steps)
        self.mean_ = np.mean(self.steps)
        self.std_ = np.std(self.steps)
        self.med_ = np.median(self.steps)

    def parseFile(self):
        stepArray = []
        with open(self.fileName, 'r') as f:
            for line in f:
                stepArray.append(line.strip())

        self.steps = np.array(stepArray, dtype=int)
        # print(self.steps)

class CollisionData:
    def __init__(self, fileName):
        self.fileName = "../result/collision_batch_" + fileName
        if not os.path.isfile(self.fileName):
            return
        self.parseFile()

        self.collisionAllStep = []
        for i in range(len(self.collisionStep)):
            self.collisionAllStep.extend([int(j) for j in self.collisionStep[i] if int(j) != 0])

        step = sorted(self.collisionAllStep)
        self.collisionNumData = step

        self.collisionSum = len(self.collisionAllStep)

    def parseFile(self):
        self.collisionStep = []
        self.collisionAA = []
        self.collisionAI = []
        self.collisionAN = []
        self.collisionII = []
        self.collisionIN = []

        with open(self.fileName, 'r') as f:
            for line in f:
                datas = line.split(',')
                self.collisionStep.append(datas[0].split('/'))
                self.appendCollision(datas[1].split('/'))

    def appendCollision(self, datas):
        self.collisionAA = datas[0]
        self.collisionAI = datas[1]
        self.collisionAN = datas[2]
        self.collisionII = datas[3]
        self.collisionIN = datas[4]


class RetransmitData:
    def __init__(self, fileName):
        self.fileName = "../result/retransmission_batch_" + fileName
        if not os.path.isfile(self.fileName):
            return
        self.parseFile()

        self.maxRetransmitNum = np.max(self.retransmitNum)
        self.minRetransmitNum = np.min(self.retransmitNum)

        self.retransmitNum = sorted(self.retransmitNum)
        self.retransmitNumData = []

        for i in range(self.maxRetransmitNum + 1):
            num = len([j for j in self.retransmitNum if i == j])
            self.retransmitNumData.append(num)

    def parseFile(self):
        self.retransmitFailureCount = 0
        self.retransmitStep = []
        self.retransmitTxStep = []
        self.retransmitRxStep = []
        self.retransmitNum = []

        with open(self.fileName, 'r') as f:
            for line in f:
                datas = line.split(',')

                if datas[0] == "F":
                    self.retransmitFailureCount += 1

                self.retransmitStep.append(datas[1].split('/')[1:])
                self.retransmitNum.append(len(datas[1]) - 1)

                if len(datas) == 4:
                    self.retransmitTxStep.append(datas[2].split('/')[1:])
                    self.retransmitRxStep.append(datas[3].split('/')[1:])
                else:
                    self.retransmitTxStep.append([])
                    self.retransmitRxStep.append([])

class Position:
    def __init__(self, args):
        self.x = int(args[0])
        self.y = int(args[1])
        self.z = int(args[2])

    def toString(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)

    def calcDistance(self, toPos):
        delX = self.x - toPos.x
        delY = self.y - toPos.y
        delZ = self.z - toPos.z
        return math.sqrt(delX ** 2 + delY ** 2 + delZ ** 2)

class MicrotubuleParams:
    def __init__(self, val):
        args = [i for i in re.split(r"[,( )]", val) if i != '']
        self.startPosition = Position(args[0:3])
        self.endPosition = Position(args[3:6])

    def toString(self):
        return "{} {}".format(self.startPosition.toString(), self.endPosition.toString())

class MoleculeParams:
    def __init__(self, val):
        args = [i for i in re.split(r"[ ]", val) if i != '']
        self.duplication = int(args[0])
        self.typeOfMolecule = MoleculeType[args[1]]
        self.size = 1
        if self.typeOfMolecule != MoleculeType["NOISE"]:
            self.typeOfMovement = MovementType[args[2]]
            self.adaptiveChangeNumber = int(args[3])
            if len(args) == 5:
                self.size = float(args[4])
            else:
                self.size = float(1)
        else:
            if len(args) == 3:
                self.size = float(args[2])
            else:
                self.size = float(1)

    def toString(self):
        if self.typeOfMolecule != MoleculeType["NOISE"]:
            return "{} {} {} {} {}".format(self.duplication, self.typeOfMolecule.name, self.typeOfMovement.name, self.adaptiveChangeNumber, self.size)
        else:
            return "{} {} {}".format(self.duplication, self.typeOfMolecule.name, self.size)

class IntermediateNode:
    def __init__(self, val):
        args = [i for i in re.split(r"[,( )]", val) if i != '']
        self.centerPosition = Position(args[0:3])
        self.size = int(args[3])
        self.infoReleasePosition = Position(args[4:7])
        self.ackReleasePosition = Position(args[7:10])

    def toString(self):
        return "{} {} {} {}".format(self.centerPosition.toString(), self.size, self.infoReleasePosition.toString(), self.ackReleasePosition.toString())

class NanoMachine:
    def __init__(self, val):
        args = [i for i in re.split(r"[,( )]", val) if i != '']
        self.centerPosition = Position(args[0:3])
        self.size = int(args[3])
        self.releasePosition = Position(args[4:7])

    def toString(self):
        return "{} {} {}".format(self.centerPosition.toString(), self.size, self.releasePosition.toString())

class FEC:
    def __init__(self, val):
        args = [i for i in re.split(r"[,( )]", val) if i != '']
        self.type = args[0]
        self.requirePacket = int(args[1])
        self.rate = float(args[2])

class MoleculeType(Enum):
    INFO = 0
    ACK = 1
    NOISE = 2

class MovementType(Enum):
    PASSIVE = 0
    ACTIVE = 1