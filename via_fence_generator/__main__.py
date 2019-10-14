from .viafence import *
from .viafence_dialogs import *

import os
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import wx
import copy

argParser = argparse.ArgumentParser()
argParser.add_argument("--dialog",      dest="dialog",      metavar="DIALOGNAME", help="Show Dialog with <DIALOGNAME>")
argParser.add_argument("--runtests",    dest="runtests",    action="store_true", default=0, help="Execute testing all json test files in 'tests' subdirectory")
argParser.add_argument("--test",        dest="test",        metavar="TESTNAME", help="Loads <TESTNAME> from 'tests' directory, runs it and shows/stores the result into the test file")
argParser.add_argument("--store",       dest="store",       action="store_true", default=0, help="When running a test, stores the result as known-good")
argParser.add_argument("--verbose",     dest="verbose",     action="store_true", default=0, help="Verbose plotting the inner workings of the algorithm")
args = argParser.parse_args()

def compareTests(testDict, refDict):
    testPts = testDict['viaPoints']
    refPts = refDict['viaPoints']
    matchedPts = [point for point in testPts if point in refPts]
    return True if len(testPts) == len(refPts) == len(matchedPts) else False

def loadTest(testFilename):
    with open(testFilename, 'r') as file:
        return json.load(file)

def storeTest(testFilename, testDict):
    with open(testFilename, 'w') as file:
        json.dump(testDict, file, indent=4, sort_keys=True)

def runTest(testDict, verboseFunc):
    viaOffset = testDict['viaOffset']
    viaPitch = testDict['viaPitch']
    pathList = testDict['pathList']

    newDict = copy.deepcopy(testDict)
    newDict['viaPoints'] = generateViaFence(pathList, viaOffset, viaPitch, verboseFunc)

    return newDict

def printTestResult(testName, refDict, testDict):
    print("{}: {} (Ref/Test Vias: {}/{})".format(
        testName, "PASSED" if compareTests(refDict, testDict) else "FAILED",
        len(refDict['viaPoints']), len(testDict['viaPoints']) ))

def verbosePlot(object, isPoints = False, isPaths = False, isPolygons = False):
    import numpy as np
    import matplotlib.pyplot as plt
    for child in object:
        data = np.array(child)
        if isPolygons:
            plt.fill(data.T[0], data.T[1], facecolor='grey', alpha=0.3, linestyle='--', linewidth=1)
        elif isPaths:
            plt.plot(data.T[0], data.T[1], linestyle='-', linewidth=3)
        elif isPoints:
            plt.plot(data.T[0], data.T[1], linestyle='', marker='x', markersize=10, mew=3)

def main():
    testDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tests')
    verboseFunc = verbosePlot if args.verbose else lambda *args,**kwargs:None

    if (args.dialog):
        # Load and show dialog
#        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        app = wx.App()
        className = globals()[args.dialog]
        className(None).Show()
        print("Starting wxApp Now. Exit using Ctrl+C")
        app.MainLoop()

    elif (args.test):
        # Load a test file, run the algorithm and show/store the result for later testing
        testFile = os.path.join(testDir, args.test) + ".json"
        ref = loadTest(testFile)
        test = runTest(ref, verboseFunc)

        printTestResult(args.test, ref, test)

        if (args.store): storeTest(testFile, test)

        for path in test['pathList']:
            plt.plot(np.array(path).T[0], np.array(path).T[1], linewidth=5)

        for via in test['viaPoints']:
            plt.plot(via[0], via[1], 'o', markersize=10)

        plt.axes().set_aspect('equal','box')
        plt.ylim(plt.ylim()[::-1])
        plt.savefig(os.path.join(testDir, args.test) + '.png')
        plt.show()
    elif (args.runtests):
        # Run all tests in 'tests' subdirectory
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        testDir = scriptDir + "/" + 'tests'
        testsPassed = 0
        testsTotal = 0

        for file in os.listdir(testDir):
            if file.endswith(".json"):
                testName = os.path.basename(file)
                ref = loadTest(os.path.join(testDir, file))
                test = runTest(ref, verboseFunc)

                printTestResult(testName, ref, test)

                if compareTests(ref, test): testsPassed += 1
                testsTotal += 1

        print("----\n{}/{} tests PASSED".format(testsPassed, testsTotal))

        assert testsPassed == testsTotal

        if testsPassed == testsTotal: exit(0) 
        else: exit(1)


main()
