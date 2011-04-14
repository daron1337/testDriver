#!/usr/bin/env python

## Program:   testDriver
## Module:    testDriver.py
## Language:  Python
## Date:      $Date: 2011/04/13 14:11:27 $
## Version:   $Revision: 0.1 $

from xml.etree import ElementTree as etree
from string import split
import subprocess, shlex


class TestDriver(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.testCases = None
        self.testPlan = {} #test_plan_name:testCasesIds
        self.testingCases = []
        
    def SetTestCases(self, testCases):
        '''
        Setting test cases from testCase xml
        '''
        self.testCases = testCases
        
    def ChooseTestCase(self,testId):
        '''
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
        Loading a test plan defined previously
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
 
    def RunTestCase(self, appPath):
        '''
        '''
        for testCase in self.testingCases:
            print "Running TestCase_%s" % testCase.id
            if testCase.type == str(1):
                self.RunTestCaseType1(appPath,testCase)
            if testCase.type == str(2):
                self.RunTestCaseType2(appPath,testCase)
            if testCase.type == str(3):
                self.RunTestCaseType3(appPath,testCase)
    
    def RunTestCaseType1(self, appPath,testCase):
        '''
        lancia applicazione
        action : richiedi all'utente di compiere un azione
        dandogli un messaggio.
        response: controlla che il log in stdout sia uguale a quello
        memorizzato nella tag response corrispondente all id della action
        '''
        
        testFailed = False
        
        app = subprocess.Popen([appPath],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        for actionId, action in sorted(testCase.actions.iteritems()):
            print action.action
            for responseId, response in sorted(testCase.responses.iteritems()):
                if responseId == actionId:
                    log = response.response
                    #check se il log --> nell'output, se si continua. 
                    
        '''
        if testFailed == False:
            print "Test Case %s passed" % (testCase.id)
            app.kill()
        '''
        
    
    def RunTestCaseType2(self, appPath, testCase):
        '''
        lancia applicazione passando come parametri la stringa della action
        response: controlla che il log in stdout sia uguale a quello
        memorizzato nella tag response corrispondente all id della action
        '''
        testFailed = False
        
        for actionId, action in sorted(testCase.actions.iteritems()):
            appArgs = appPath+' '+action.action
            args = shlex.split(appArgs)
            app = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
            for responseId, response in sorted(testCase.responses.iteritems()):
                if responseId == actionId:
                    log = response.response
                    #check se il log --> nell'output, se si continua. 
        
        '''
        if testFailed == False:
            print "Test Case %s passed" % (testCase.id)
            app.kill()
        '''
        
    
    def RunTestCaseType3(self, appPath, testCase):
        '''
        lancia applicazione passando come parametri la stringa della action
        response: utente deve rispondere YES/NO a un'asserzione (stringa response)
        screenshots screencapture? tk per prendere screen?? tbd
        '''
        testFailed = False
        
        for actionId, action in sorted(testCase.actions.iteritems()):
            appArgs = appPath+' '+action.action
            args = shlex.split(appArgs)
            app = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
            for responseId, response in sorted(testCase.responses.iteritems()):
                if responseId == actionId:
                    print response.response
                    print "YES/NO"  #YES, test passato. No, test Fallito
                    user_answer = raw_input()
                    if user_answer.find('y') != -1:
                        pass
                    else:
                        testFailed = True
                        app.kill()
                        break
                    
        if testFailed == False:
            print "Test Case %s passed" % (testCase.id)
            app.kill()
        
    
        
def indent(elem, level=0):
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