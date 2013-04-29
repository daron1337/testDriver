#!/usr/bin/env python

## Program:   testDriver
## Module:    testDriver.py
## Language:  Python
## Date:      $Date: 2012/02/10 10:01:27 $
## Version:   $Revision: 0.1.6 $

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

from TestCases import TestCases
from TestRuns import TestRuns
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
                  help="TestCases related to the new Testplan defined with -n or --newPlanName option. A list of test cases can be defined using an interval (case1_Id:caseN_Id) or a set of cases (case1_Id,case2_Id,case3_Id,case6_Id,case8_Id).")
parser.add_option("-l", "--readyLog", action="store",dest='readyLog', type="string", default=None,
                  help="Setting the log for the main application in case of automated test with command option. By default is not active.")
parser.add_option("-w", "--waitConnection", action="store", dest='connection', default='3000',
                  help="If active, testDriver will try to connect to the main app until it is ready before launching tests. By default connection will use port 3000")
parser.add_option("-t", "--timeOut", action="store",dest='timeOut', type="string", default="900",
                  help="TimeOut value (in seconds) which will be used for automated tests. By default timeOut = 900 seconds.")
parser.add_option("-i", "--input", action="store",dest='inputFilesDirName', type="string", default="input files",
                  help="Name of the directory which contains input files for the application. This directory has to be located into its project folder. By default is defined as 'input files'.")
parser.add_option("-d", "--mainDir", action="store",dest='mainDirectory', type="string", default=None,
                  help="Name of the directory in which you want to have subfolders plans and results. By default is defined as 'projects/project_name'. If you want subfolders located in main testDriver directory just type 'main'")
parser.add_option("-r", "--testRail", action="store_true",dest='testRail', default=False,
                  help="Activate testDriver to TestRail API. By default is not active.")
parser.add_option("-k", "--kill", action="store",dest='userDefinedKill', type="string", default=None,
                  help="Setting user-defined instruction for killing the main testing application. By default is none and main application will be killed using the standard terminate() method from the Asyncproc.py Class.")
parser.add_option("-m", "--sleepingTime", action="store",dest='sleepingTime', type="int", default=1,
                  help="Sleeping time (in seconds) which will be used for command type actions tests. By default sleepingTime = 1 second.")
parser.add_option("-e", "--exportResults", action="store", type="string", dest='export', default=None,
                  help="Exporting test plan results to testRail db using the API.")

(options, args) = parser.parse_args()

#Setting input files directory
inputFilesDirName = options.inputFilesDirName

#Creating a new project to be tested
project = TestCases()
testRuns = TestRuns()
testResults = TestResults()

#Setting main working directory
if options.mainDirectory is not None:
    testRuns.SetMainDirectory(options.mainDirectory)

#Exporting results to testRail
if options.export:
    print "Exporting results to testRail"
    if options.xml is None:
        sys.exit("Error, please specify the path to the testCases xml file.")  
    testCases = project.ReadXml(options.xml)  #setting the testCases xml file
    #testRuns.SetTestCases(project)
    from TestDriverDbApi import TestDriverDbApi
    testRuns.testRail = True
    testDriverDbApi = TestDriverDbApi()
    testDriverDbApi.ConnectDb('127.0.0.1','testrail','password','dbName')
    testDriverDbApi.SetTestCases(project)
    testDriverDbApi.SetRunName(options.plan)
    
    testResults.ReadTxt(options.export)
    
    testRuns.SetDbApi(testDriverDbApi)
    
    
    testRuns.testDriverToTestRail()
    sys.exit("DONE")

#Setting the log for the main application in case of automated test with command option.
if options.readyLog is not None:
    testRuns.readyLog = options.readyLog
    
#Setting the log for the main application in case of automated test with command option.
testRuns.SetConnection(options.connection)

#Setting userDefinedKill command and sleepingTime
if options.userDefinedKill is not None:
    testRuns.SetUserDefinedKill(options.userDefinedKill)
testRuns.SetSleepingTime(options.sleepingTime)

#Setting application path and its testcases xml files
if options.appPath is None:
    sys.exit("Error, please specify the path to the application which has to be tested.")  
appPath = options.appPath #setting application path
if options.xml is None:
    sys.exit("Error, please specify the path to the testCases xml file.")  
testCases = project.ReadXml(options.xml)  #setting the testCases xml file
testRuns.SetTestCases(project)

#Choosing a specific test case, a specific test plan or creates a new one.
TestSpecified = False
if options.case is not None:
    testRuns.ChooseTestCase(options.case)
    TestSpecified = True
if options.plan is not None:
    testRuns.GetTestPlan(options.plan)
    TestSpecified = True
if options.newPlanName is not None and options.newPlanCases is not None:    
    testRuns.SetTestPlan(options.newPlanName,options.newPlanCases)
    TestSpecified = True
if TestSpecified is False:
    sys.exit("Error, please specify an existing test case/test plan or create a new test plan.")  

#Setting a new timeout value
testRuns.SetTimeOut(options.timeOut)

#Activating testDriver to testRail API
if options.testRail is True:
    from TestDriverDbApi import TestDriverDbApi
    testRuns.testRail = True
    testDriverDbApi = TestDriverDbApi()
    testDriverDbApi.ConnectDb('127.0.0.1','userName','password','dbName')
    testDriverDbApi.SetTestCases(project)
    testDriverDbApi.SetRunName(options.plan)
    testRuns.SetDbApi(testDriverDbApi)

#Setting temporary directory for I/O files   
testRuns.SetTmpDirectory(inputFilesDirName)   

#Running the testcase(s)    
testRuns.RunTestCase(appPath)

#Retrieving and writing results into output files.
testResults.SetTestingResults(testRuns)
testResults.RetrieveResults()
testResults.WriteXml()
testResults.WriteTxt()

#Clean the temporary directory folder.
testRuns.CleanTmpDirectory()

#If testDriver to testRail options is active the API is executed.
testRuns.testDriverToTestRail()