#!/usr/bin/env python

## Program:   testDriver
## Module:    Main.py
## Language:  Python
## Date:      $Date: 2011/10/10 10:26:13 $
## Version:   $Revision: 0.1.3 $

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

from TestCases import TestCases
from TestDriver import TestDriver
from TestResults import TestResults
from optparse import OptionParser
import sys

parser = OptionParser()

parser.add_option("-a", "--app", action="store",dest='appPath', type="string", default=None,
                  help="Application path. Required.")
parser.add_option("-x", "--xml", action="store",dest='xml', type="string", default=None,
                  help="TestCases xml file related to application. Required.")
parser.add_option("-c", "--case", action="store",dest='case', type="string", default=None,
                  help="Specific test case id to be tested.")
parser.add_option("-p", "--plan", action="store",dest='plan', type="string", default=None,
                  help="Specific test plan representing a set of test cases. Use the plan name as argument.")
parser.add_option("-n", "--newPlanName", action="store",dest='newPlanName', type="string", default=None,
                  help="Name for the new test plan. Testcases related to the new plan have to be defined with -l or --newPlanCases option.")
parser.add_option("-s", "--newPlanCases", action="store",dest='newPlanCases', type="string", default=None,
                  help="TestCases related to the new Testplan defined with -n or --newPlanName option. A list of test cases can be defined,")
parser.add_option("-l", "--readyLog", action="store",dest='readyLog', type="string", default="ReadyForTestDriver",
                  help="Setting the log for the main application in case of automated test with command option. By default is defined as 'ReadyForTestDriver'.")
parser.add_option("-t", "--timeOut", action="store",dest='timeOut', type="string", default="900",
                  help="TimeOut value (in seconds) which will be used for automated tests. By default timeOut = 900 seconds.")
parser.add_option("-i", "--input", action="store",dest='inputFilesDirName', type="string", default="input files",
                  help="Name of the directory which contains input files for the application. This directory has to be located into its project folder. By default is defined as 'input files'.")
parser.add_option("-r", "--testRail", action="store_true",dest='testRail', default=False,
                  help="Activate testDriver to TestRail API. By default is not active.")


(options, args) = parser.parse_args()

#Setting input files directory
inputFilesDirName = options.inputFilesDirName

#Creating a new project to be tested
project = TestCases()
testDriver = TestDriver()
testResults = TestResults()

#Setting the log for the main application in case of automated test with command option.
testDriver.readyLog = options.readyLog

#Setting application path and its testcases xml files
if options.appPath is None:
    sys.exit("Error, please specify the path to the application which has to be tested.")  
appPath = options.appPath #setting application path
if options.xml is None:
    sys.exit("Error, please specify the path to the testCases xml file.")  
testCases = project.ReadXml(options.xml)  #setting the testCases xml file
testDriver.SetTestCases(project)

#Choosing a specific test case, a specific test plan or creates a new one.
TestSpecified = False
if options.case is not None:
    testDriver.ChooseTestCase(options.case)
    TestSpecified = True
if options.plan is not None:
    testDriver.GetTestPlan(options.plan)
    TestSpecified = True
if options.newPlanName is not None and options.newPlanCases is not None:    
    testDriver.SetTestPlan(options.newPlanName,options.newPlanCases)
    TestSpecified = True
if TestSpecified is False:
    sys.exit("Error, please specify an existing test case/test plan or create a new test plan.")  

#Setting a new timeout value
testDriver.SetTimeOut(options.timeOut)

#Activating testDriver to testRail API
if options.testRail is True:
    from TestDriverDbApi import TestDriverDbApi
    testDriver.testRail = True
    testDriverDbApi = TestDriverDbApi()
    testDriverDbApi.ConnectDb('127.0.0.1','userName','password','dbName')
    testDriverDbApi.SetTestCases(project)
    testDriverDbApi.SetRunName(options.plan)
    testDriver.SetDbApi(testDriverDbApi)

#Setting temporary directory for I/O files   
testDriver.SetTmpDirectory(inputFilesDirName)   

#Running the testcase(s)    
testDriver.RunTestCase(appPath)

#Retrieving and writing results into output files.
testResults.SetTestingResults(testDriver)
testResults.RetrieveResults()
testResults.WriteXml()
testResults.WriteTxt()

#Clean the temporary directory folder.
testDriver.CleanTmpDirectory()

#If testDriver to testRail options is active the API is executed.
testDriver.testDriverToTestRail()