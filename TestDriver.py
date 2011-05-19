#!/usr/bin/env python

## Program:   testDriver
## Module:    testDriver.py
## Language:  Python
## Date:      $Date: 2011/05/19 09:43:27 $
## Version:   $Revision: 0.1.2 $

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

try:
    import wx
except:
    print "Screenshot feature not available, please install wxpython package"
from xml.etree import ElementTree as etree
from string import split, lower
from time import time
import sys, shlex, shutil
from asyncproc import Process

class TestDriver(object):
    '''
    TestDriver class runs test cases of different types.
    The application to be tested is launched using
    asynchronous process.
    This class has the following methods:
    SetTmpDirectory: a method for setting local environment for I/O files
    CleaningTmpDirectory: a method for cleaning local environment for I/O files
    SetTestCases: a method for setting test cases.
    ChooseTestCase: a method for choosing specific test case.
    SetTestPlan: a method for creating a new test plan and 
    saving it in a specific xml file.
    GetTestPlan: a method for loading a test plan defined previously.
    SetTimeOut: a method for setting testing timeout value (in seconds).
    RunTestCase: a method for running selected test case calling specific method.
    RunTestCaseType1: a method for running type1 tests.
    RunTestCaseType2: a method for running type2 tests.
    RunTestCaseType3: a method for running type3 tests.
    TakeScreenshot: a method for supporting screenshot feature
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.testCases = None
        self.testPlan = {} #test_plan_name:testCasesIds
        self.testingCases = []
        self.timeOut = 900
        self.tmpDir = None
        
    def SetTmpDirectory(self, inputFilesDirName):
        '''
        Setting temporary directory for I/O files
        '''
        self.tmpDir = "projects/%s/tmp/" % (self.testCases.projectName)
        inputFilesDir = "projects/%s/%s/" % (self.testCases.projectName,inputFilesDirName)
        try:
            shutil.copytree(inputFilesDir, self.tmpDir)
        except OSError:
            shutil.rmtree(self.tmpDir)
            shutil.copytree(inputFilesDir, self.tmpDir)
            
    def CleanTmpDirectory(self):
        '''
        Cleaning temporary directory for I/O files
        '''
        shutil.rmtree(self.tmpDir)
    
    def SetTestCases(self, testCases):
        '''
        Setting test cases from testCase xml.
        '''
        self.testCases = testCases
        
    def ChooseTestCase(self,testId):
        '''
        Choosing specific test case.
        '''
        self.testingCases.append(self.testCases.Cases[testId])

    def SetTestPlan(self, planName, testCasesIds):
        '''
        Setting a test plan. Useful for testing a lot of cases.
        Saving plan in a specific xml file.
        '''
        self.testPlan[planName] = []
        testCasesIds=split(testCasesIds,",")
        self.testPlan[planName][:] = testCasesIds[:]     
        for testId in self.testPlan[planName]:
            self.testingCases.append(self.testCases.Cases[testId])              
        filepath = "projects/%s/plans/%s.xml" % (self.testCases.projectName,planName)
        root = etree.Element("Project", id=self.testCases.projectId, name=self.testCases.projectName, version=self.testCases.projectVersion)
        plan = etree.ElementTree(root)
        testPlan = etree.SubElement(root,"testPlan", name=planName)
        for caseId in testCasesIds:
            tplan = etree.SubElement(testPlan,"testCase")
            tplan.text=str(caseId)
        indent(root)                
        plan.write (filepath, encoding='iso-8859-1')  
        
    def GetTestPlan(self, planName):
        '''
        Loading a test plan defined previously.
        '''
        filepath = "projects/%s/plans/%s.xml" % (self.testCases.projectName,planName)    
        xmldoc = open(filepath)
        xmltree=etree.parse(xmldoc)
        project=xmltree.getroot()
        if self.testCases.projectId != project.attrib['id']:
            pass
        else:
            self.testPlan[planName] = []
            testCasesIds = []
            for ids in project.findall(".//testCase"):
                testCasesIds.append(ids.text)
            self.testPlan[planName][:] = testCasesIds[:]
            for testId in self.testPlan[planName]:
                self.testingCases.append(self.testCases.Cases[testId])
    
    def SetTimeOut (self,timeOut):
        '''
        Setting timeout value (in seconds)
        '''
        self.timeOut = float(timeOut) #timeout in seconds [s]

    def RunTestCase(self, appPath):
        '''
        Running selected test case calling specific method.
        '''
        for testCase in self.testingCases:
            print "\nRunning TestCase_%s" % testCase.id
            print testCase.description
            if testCase.type == str(1):
                self.RunTestCaseType1(appPath,testCase)
            if testCase.type == str(2):
                self.RunTestCaseType2(appPath,testCase)
            if testCase.type == str(3):
                self.RunTestCaseType3(appPath,testCase)
    
    def RunTestCaseType1(self, appPath,testCase):
        '''
        This method runs type1 tests. This kind of test takes asks user to do an
        action and search for a log in the standard output of the
        application to be tested. User can skip any test action using a 
        Keyboard interrupt (CTRL+C)
        If at least one action fails to retrieve its log, the test will fail.
        A timeout has to be set before (default value is 15min).
        '''
        testFailed = False
        testActions = {}
        appArgs = appPath
        args = shlex.split(appArgs)
        app = Process(args)
        try:
            sortedCases = [(k, testCase.actions[k]) for k in sorted(testCase.actions, key=asint)]
            for actionId, action in sortedCases:
                if testFailed == True:
                    break
                startTime = time()
                testActions[actionId] = None
                print "\n", actionId, action.action
                print "Press CTRL-C to skip test"
                while testActions[actionId] == None:
                    outAndErr = app.readboth()
                    for out in outAndErr:
                        for responseId, response in sorted(testCase.responses.iteritems()):
                            if responseId == actionId:
                                log = response.response
                                if out.find(log) != -1:
                                    print "TestCase %s Action %s Passed" % (testCase.id, actionId) 
                                    testActions[actionId] = True
                                if out.find(log) == -1 and time()-startTime>self.timeOut:
                                    print "TestCase %s Action %s Failed" % (testCase.id, actionId)
                                    print "Press q to terminate this test or r to retry it"
                                    userInput = raw_input()  
                                    if userInput == 'q':
                                        app.terminate()
                                        testActions[actionId] = False
                                        testFailed = True
                                    if userInput == 'r':
                                        startTime = time()
                                        print actionId, action.action
                                    if userInput != 'q' and userInput != 'r':
                                        print "Press q to terminate this test or to retry it"
                                        userInput = raw_input()
                                                               
        except KeyboardInterrupt:
            print "\nTestCase %s Action %s Failed" % (testCase.id, actionId)
            app.terminate()
            testActions[actionId] = False
            testFailed = True
        
        for id, t in testActions.iteritems():
            if t == False:
                testFailed = True
                print "TEST %s FAILED, (action %s)" % (testCase.id, id)
                testCase.status = 'FAILED (%s)' % id  

        if testFailed == False:
            print "TEST %s PASSED" % testCase.id
            testCase.status = 'PASSED'
            app.terminate()    
    
    def RunTestCaseType2(self, appPath, testCase):
        '''
        This method runs type2 tests. This kind of test takes as input a list
        of arguments (action) and search for a log in the standard output of the
        application to be tested. User can skip any test actions using a 
        Keyboard interrupt (CTRL+C)
        If at least one action fails to retrieve its log, the test will fail.
        A timeout has to be setted before (default value is 900sec)
        '''       
        testFailed = False
        testActions = {}
        try:
            sortedCases = [(k, testCase.actions[k]) for k in sorted(testCase.actions, key=asint)]
            for actionId, action in sortedCases:
                if testFailed == True:
                    break
                print "Running Action %s, Press CTRL-C to skip test" % actionId    
                testActions[actionId] = None
                appArgs = appPath+' '+action.action
                args = shlex.split(appArgs)          
                app = Process(args)
                startTime = time()              
                while testActions[actionId] == None:   
                    outAndErr = app.readboth()
                    for out in outAndErr:
                        for responseId, response in sorted(testCase.responses.iteritems()):
                            if responseId == actionId:
                                log = response.response
                                if out.find(log) != -1:
                                    print "TestCase %s Action %s Passed" % (testCase.id, actionId) 
                                    testActions[actionId] = True
                                    app.terminate()
                                if out.find(log) == -1 and time()-startTime>self.timeOut:
                                    print "\nTestCase %s Action %s Failed" % (testCase.id, actionId)
                                    app.terminate()
                                    testActions[actionId] = False
                                    testFailed = True 
                                                     
        except KeyboardInterrupt:
            print "\nTestCase %s Action %s Failed" % (testCase.id, actionId)
            app.terminate()
            testActions[actionId] = False
            testFailed = True

        for id, t in testActions.iteritems():
            if t == False:
                testFailed = True
                print "TEST %s FAILED, (action %s)" % (testCase.id, id)
                testCase.status = 'FAILED (%s)' % id 

        if testFailed == False:
            print "TEST %s PASSED" % testCase.id
            testCase.status = 'PASSED'

    def RunTestCaseType3(self, appPath, testCase):
        '''
        This method runs type3 tests. This kind of test takes as input a list
        of arguments (action) and waits for user interaction. User has to answer
        yes or no to an expected statement.
        If at least one action fails (a negative answer from the user), the test will fail.
        '''    
        testFailed = False
        testActions = {}
        sortedCases = [(k, testCase.actions[k]) for k in sorted(testCase.actions, key=asint)]
        for actionId, action in sortedCases:
            if testFailed == True:
                break      
            testActions[actionId] = None
            appArgs = appPath+' '+action.action
            args = shlex.split(appArgs)
            app = Process(args)
            while testActions[actionId] == None:
                for responseId, response in sorted(testCase.responses.iteritems()):
                    if responseId == actionId:
                        print "\n", response.response
                        print "YES/NO"  #YES, test passato. No, test Fallito
                        user_answer = lower(raw_input())
                        if user_answer.find('y') != -1:
                            print "TestCase %s Action %s Passed\n" % (testCase.id, actionId)
                            self.TakeScreenshot(testCase.id, actionId)
                            app.terminate()
                            testActions[actionId] = True
                        if user_answer.find('n') != -1:
                            app.terminate()
                            testActions[actionId] = False
                            testFailed = True
                        if user_answer.find('n') == -1 and user_answer.find('y') == -1:
                            pass
                        
        for id, t in testActions.iteritems():
            if t == False:
                testFailed = True
                print "TEST %s FAILED, (action %s)" % (testCase.id, id)
                self.TakeScreenshot(testCase.id, id)
                testCase.status = 'FAILED (%s)' % id 

        if testFailed == False:
            print "TEST %s PASSED" % testCase.id
            self.TakeScreenshot(testCase.id)
            testCase.status = 'PASSED'
            
    def TakeScreenshot(self, testCaseId, actionId=None):
        '''
        This method takes a screenshot.
        '''
        
        thisApp = wx.App( redirect=False )      # Need to access WX functionality without MainLoop().
    
        # Capture the entire primary Desktop screen.
        captureBmapSize = (wx.SystemSettings.GetMetric( wx.SYS_SCREEN_X ), 
                           wx.SystemSettings.GetMetric( wx.SYS_SCREEN_Y ) )
                           
        captureStartPos = (0, 0)    # Arbitrary U-L position anywhere within the screen
        bitmap = ScreenCapture( captureStartPos, captureBmapSize )
        
        folder = 'projects/%s/results/' % (self.testCases.projectName)
        if actionId == None:
            fileBasename = 'test%s' %(testCaseId)
        else:
            fileBasename = 'test%s_action_%s' %(testCaseId,actionId)
        fileExt = '.png'
        filename = folder + fileBasename + fileExt
        bitmap.SaveFile( filename, wx.BITMAP_TYPE_PNG )

def asint(s):
    '''
    This function convert a sting into integer.
    It's used for sorting a dictionary with key 
    represented with string numbers.
    '''
    try: 
        return int(s), ''
    except ValueError:
        return sys.maxint, s

def indent(elem, level=0):
    '''
    This functions is used for xml write indentation if
    lxml package is not provided.
    '''
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def ScreenCapture( captureStartPos, captureBmapSize ):
    """
    General Desktop screen portion capture - partial or entire Desktop.
    Any particular Desktop screen size is :
        screenRect = wx.Display( n ).GetGeometry()      
    """
    scrDC = wx.ScreenDC()
    scrDcSize = scrDC.Size

    # Cross-platform adaptations :
    scrDcBmap     = scrDC.GetAsBitmap()
    scrDcBmapSize = scrDcBmap.GetSize()
    
    # Check if scrDC.GetAsBitmap() method has been implemented on this platform.
    if   scrDcBmapSize == (0, 0) :      # Not implemented :  Get the screen bitmap the long way.

        # Create a new empty (black) destination bitmap the size of the scrDC. 
        scrDcBmap = wx.EmptyBitmap( *scrDcSize )    # Overwrite the invalid original assignment.
        scrDcBmapSizeX, scrDcBmapSizeY = scrDcSize

        # Create a DC tool that is associated with scrDcBmap.
        memDC = wx.MemoryDC( scrDcBmap )

        # Copy (blit, "Block Level Transfer") a portion of the screen bitmap 
        #   into the returned capture bitmap.
        # The bitmap associated with memDC (scrDcBmap) is the blit destination.

        memDC.Blit( 0, 0,                           # Copy to this start coordinate.
                    scrDcBmapSizeX, scrDcBmapSizeY, # Copy an area this size.
                    scrDC,                          # Copy from this DC's bitmap.
                    0, 0,                    )      # Copy from this start coordinate.

        memDC.SelectObject( wx.NullBitmap )     # Finish using this wx.MemoryDC.
                                                # Release scrDcBmap for other uses.        
    else :
        # This platform has scrDC.GetAsBitmap() implemented.
        scrDcBmap = scrDC.GetAsBitmap()     # So easy !  Copy the entire Desktop bitmap.
   
    return scrDcBmap.GetSubBitmap( wx.RectPS( captureStartPos, captureBmapSize ) )