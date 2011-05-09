#!/usr/bin/env python

## Program:   testDriver
## Module:    Main.py
## Language:  Python
## Date:      $Date: 2011/04/13 14:23:04 $
## Version:   $Revision: 0.1 $

from TestCases import TestCases
from TestDriver import TestDriver
from TestResults import TestResults
import sys, getopt

#===============================================================================
# -a,--app for setting application path to be tested
#-x,--xml for setting testcases xml file path
#-p,--plan for loading an existing testplan
#-n,--name + -l,--caseList for setting and saving a new testPlan (name, caseIds).
#Example:(-n pippo -l 1,2,3)
#-t, --timeOut for setting a timeOut value (in seconds)
#===============================================================================

try:                                
    opts, args = getopt.getopt(sys.argv[1:], "a:x:c:p:n:l:t:", ["app=", "xml=", "case=", "plan=", "name=", "caseList=", "timeOut="]) 
except getopt.GetoptError: 
    print "Error"                                  
    sys.exit(2) 

project = TestCases()
testDriver = TestDriver()
testResults = TestResults()

########DEFAULT VALUES FOR SW DEVELOPING############
#testCases = project.ReadXml('projects/Tester/TestCases.xml')  
#testDriver.SetTestCases(project)
#testDriver.ChooseTestCase('2')
#testDriver.GetTestPlan('pluto')
#appPath = '/usr/bin/python -u projects/Tester/Tester.py'
####################################################

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
        
testDriver.RunTestCase(appPath)
testResults.SetTestingResults(testDriver)
testResults.RetrieveResults()
testResults.WriteXml()
testResults.WriteTxt()