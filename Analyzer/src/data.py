import numpy as np
from enum import Enum
import re
import os

class AllData:
    def __init__(self, fileName):
        self.datFileName = fileName
        self.datData = DatData(self.datFileName)
        outputFileName = self.datData.config["outputFile"].strip()
        self.resultData = ResultData(outputFileName)
        self.adjustData = AdjustData(outputFileName)
        self.collisionData = CollisionData(outputFileName)
        self.retransmitData = RetransmitData(outputFileName)

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


        print(self.retransmitStep)


class Position:
    def __init__(self, args):
        self.x = int(args[0])
        self.y = int(args[1])
        self.z = int(args[2])

    def toString(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)

class MicrotubuleParams:
    def __init__(self, val):
        args = [i for i in re.split(r"[,( )]", val) if i != '']
        self.start_position = Position(args[0:3])
        self.end_position = Position(args[3:6])

    def toString(self):
        return "{} {}".format(self.start_position.toString(), self.end_position.toString())

class MoleculeParams:
    def __init__(self, val):
        args = [i for i in re.split(r"[ ]", val) if i != '']
        self.duplication = int(args[0])
        self.type_of_molecule = MoleculeType[args[1]]
        self.size = 1
        if self.type_of_molecule != MoleculeType["NOISE"]:
            self.type_of_movement = MovementType[args[2]]
            self.adaptive_change_number = int(args[3])
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
        if self.type_of_molecule != MoleculeType["NOISE"]:
            return "{} {} {} {} {}".format(self.duplication, self.type_of_molecule.name, self.type_of_movement.name, self.adaptive_change_number, self.size)
        else:
            return "{} {} {}".format(self.duplication, self.type_of_molecule.name, self.size)

class IntermediateNode:
    def __init__(self, val):
        args = [i for i in re.split(r"[,( )]", val) if i != '']
        self.center_position = Position(args[0:3])
        self.size = int(args[3])
        self.info_release_position = Position(args[4:7])
        self.ack_release_position = Position(args[7:10])

    def toString(self):
        return "{} {} {} {}".format(self.center_position.toString(), self.size, self.info_release_position.toString(), self.ack_release_position.toString())

class NanoMachine:
    def __init__(self, val):
        args = [i for i in re.split(r"[,( )]", val) if i != '']
        self.center_position = Position(args[0:3])
        self.size = int(args[3])
        self.release_position = Position(args[4:7])

    def toString(self):
        return "{} {} {}".format(self.center_position.toString(), self.size, self.release_position.toString())

class FEC:
    def __init__(self, val):
        args = [i for i in re.split(r"[,( )]", val) if i != '']
        self.type = args[0]
        self.require_packet = int(args[1])
        self.rate = float(args[2])

class MoleculeType(Enum):
    INFO = 0
    ACK = 1
    NOISE = 2

class MovementType(Enum):
    PASSIVE = 0
    ACTIVE = 1