#!/usr/bin/env python

## Program:   testDriver
## Module:    Main.py
## Language:  Python
## Date:      $Date: 2011/05/19 09:47:04 $
## Version:   $Revision: 0.1.2 $

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

from TestCases import TestCases
from TestDriver import TestDriver
from TestResults import TestResults
from TestDriverDbApi import TestDriverDbApi
import sys, getopt

try:                                
    opts, args = getopt.getopt(sys.argv[1:], "a:x:c:p:n:l:t:i:d:", ["app=", "xml=", "case=", "plan=", "name=", "caseList=", "timeOut=", "input=", "testrail="]) 
except getopt.GetoptError: 
    print "Error"                                  
    sys.exit(2) 

inputFilesDirName = 'input files'
project = TestCases()
testDriver = TestDriver()
testResults = TestResults()

for opt, arg in opts:
    if opt in ("-a", "--app"):
        appPath = arg 
    if opt in ("-x", "--xml"):
        xml = arg   
        testCases = project.ReadXml(xml)  #read xml
        testDriver.SetTestCases(project)
    if opt in ("-c", "--case"):
        case = arg
        testDriver.ChooseTestCase(case)
    if opt in ("-p", "--plan"):
        plan = arg
        testDriver.GetTestPlan(plan)
    if opt in ("-n", "--name"):
        name = arg
    if opt in ("-l", "--caseList"):
        caseList = arg
        testDriver.SetTestPlan(name,caseList)
    if opt in ("-t", "--timeOut"):
        timeOut = arg
        testDriver.SetTimeOut(timeOut)
    if opt in ("-i", "--input"):
        inputFilesDirName = arg
    if opt in ("-d", "--testrail"):
        testDriver.testRail = True
        runName = arg
        testDriverDbApi = TestDriverDbApi()
        testDriverDbApi.ConnectDb('127.0.0.1','userName','password','dbName')
        testDriverDbApi.SetTestCases(project)
        testDriverDbApi.SetRunName(runName)
        testDriver.SetDbApi(testDriverDbApi)
        
testDriver.SetTmpDirectory(inputFilesDirName)       
testDriver.RunTestCase(appPath)
testResults.SetTestingResults(testDriver)
testResults.RetrieveResults()
testResults.WriteXml()
testResults.WriteTxt()
testDriver.CleanTmpDirectory()
testDriver.testDriverToTestRail()