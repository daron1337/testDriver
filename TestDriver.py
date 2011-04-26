#!/usr/bin/env python

## Program:   testDriver
## Module:    testDriver.py
## Language:  Python
## Date:      $Date: 2011/04/13 14:11:27 $
## Version:   $Revision: 0.1 $

from xml.etree import ElementTree as etree
from string import split
import subprocess, shlex, sys
from threading import Thread
from Tkinter import *

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

    def Skip(self):
        '''
        '''
        self.root = Tk()
        frame = Frame(self.root)
        frame.pack()
        self.skipButton = Button(frame, text="SKIP", fg="red", command=self.doSkip)
        self.skipButton.pack(side=LEFT)
        self.root.mainloop()

    def doSkip(self):
        '''
        '''
        self.shouldStopPollingThread = True
        self.root.quit()

    def PollApp(self,app,testCase,actionId,testActions):
        '''
        '''
        while app.poll() is None:
            if self.shouldStopPollingThread:
                print "OK"
                self.root.quit()
                app.returncode = 0
                app.kill()
                break
            out = app.stdout.readline()
            for responseId, response in sorted(testCase.responses.iteritems()):
                if responseId == actionId:
                    log = response.response
                    if out.find(log) != -1:
                        print "TestCase %s Action %s Passed" % (testCase.id, actionId) 
                        testActions[actionId] = True
                        app.returncode = 0
                        app.kill()
                        self.root.quit()

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
        #TODO: da fixare!
        
        testFailed = False
        appArgs = appPath
        args = shlex.split(appArgs)
        app = subprocess.Popen(args, stdout=subprocess.PIPE)
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

        #TODO: kill process se tutto ok o se fallisce qualcosa!


        testFailed = False
        testActions = {}

        for actionId, action in sorted(testCase.actions.iteritems()):
            testActions[actionId] = False
            appArgs = appPath+' '+action.action
            args = shlex.split(appArgs)
            app = subprocess.Popen(args, stdout=subprocess.PIPE)
            self.shouldStopPollingThread = False
            pollingThread = Thread(target=self.PollApp,args=(app,testCase,actionId,testActions))
            pollingThread.start()
            #Chiama funzione che aspetta input da utente, se utente schiaccia Skip, shouldStopPollingThread diventa True
            self.Skip()

        for t in testActions.itervalues():
            if t == False:
                testFailed = True
                print "TEST %s FAILED, (action %s)" % (testCase.id, actionId)

        if testFailed == False:
            print "TEST %s PASSED" % testCase.id

    def RunTestCaseType3(self, appPath, testCase):
        '''
        lancia applicazione passando come parametri la stringa della action
        response: utente deve rispondere YES/NO a un'asserzione (stringa response)
        screenshots screencapture? tk per prendere screen?? tbd
        '''
        
        #TODO: screenshot!
         
        testFailed = False
        
        for actionId, action in sorted(testCase.actions.iteritems()):
            if testFailed  == False:
                appArgs = appPath+' '+action.action  
                args = shlex.split(appArgs)
                app = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
                for responseId, response in sorted(testCase.responses.iteritems()):
                    if responseId == actionId:
                        print response.response
                        print "YES/NO"  #YES, test passato. No, test Fallito
                        user_answer = raw_input()
                        if user_answer.find('y') != -1:
                            print "TestCase %s Action %s Passed\n" % (testCase.id, actionId)
                            app.kill()
                        else:
                            testFailed = True
                            app.kill()
                            print "TEST %s FAILED, (action %s)" % (testCase.id, actionId)
                            break
                        
        if testFailed == False:
            print "Test Case %s passed" % (testCase.id)
            app.kill()

class SkipTest(object):
    
    def __init__(self, master):
        '''
        class Constructor
        '''
        
        frame = Frame(master)
        frame.pack()
        self.skip = Button(frame, text="SKIP", fg="red", command=self.doSkip)
        self.skip.pack(side=LEFT)

    def doSkip(self):
        '''
        '''
        self.shouldStopPollingThread = True
        #self.root.quit()

        
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