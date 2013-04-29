#!/usr/bin/env python

## Program:   testDriver
## Module:    TestResults.py
## Language:  Python
## Date:      $Date: 2012/02/10 10:01:27 $
## Version:   $Revision: 0.1.6 $

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

from xml.etree import ElementTree as etree
import os

class TestResults(object):
    '''
    TestResults class writes testing results in a .xml file
    and in a .txt file.
    This class has the following methods:
    SetTestingResults: a method for setting results from testRuns class
    RetrieveResults: a method for retrieving testResults
    WriteTxt: a method for writing results in a .txt file
    WriteXml: a method for writing results in a .xml file
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.testCases = None
        self.testPlanName = None
        self.testedCases = None
        self.testPlanName = None
        self.results = {} #test:result
        self.mainDir = None
    
    def SetTestingResults(self, testRuns):
        '''
        Setting testRuns class
        '''
        self.testCases = testRuns.testCases
        self.mainDir = testRuns.mainDir
        if testRuns.testPlan:
            self.testPlanName = testRuns.testPlan.keys()[0]
            self.testedCases = testRuns.testPlan[self.testPlanName]
        else:
            self.testedCases = testRuns.testingCases[0].id
        
    def RetrieveResults(self):
        '''
        This method retrieves test results
        '''
        for c in self.testCases.Cases.itervalues():
            for t in self.testedCases:
                if c.id == t:
                    self.results[c] = c.status
    
    def ReadTxt(self, txt_path):
        '''
        This method read test results txt file for a single
        case or a complete test plan.
        '''
        results = {} #id,status
        
        text_file = open(txt_path, "r")       
        while True:
            text = text_file.readline()
            if text.startswith("case"):
                row = text.split(':')
                caseId = row[0][4:]
                result = row[1]
                results[caseId]=result
            if text == "":
                break
        text_file.close()
        
        for case_id, case in self.testCases.Cases.iteritems():
            for c,r in results.iteritems():
                print case_id, c, type(case_id), type(c)
                if case_id == c:
                    case.status = r 
        return results       
    
    def WriteTxt(self):
        '''
        This method writes test results related to a single
        test case or a complete test plan into a txt file
        '''
        test_list =[]
        if self.testPlanName:
            name = 'plan_%s'% self.testPlanName
        else:
            name = 'case_%s' % self.testedCases
        for c in self.testCases.Cases.itervalues():
            test_list.append(c.id)
        test_list.sort()  
        if self.mainDir != 'projects/':
            txtpath = self.mainDir+"results/%s.txt" % name
            if not os.path.exists (self.mainDir+"results/"):
                os.mkdir(self.mainDir+"results/")
        else:
            txtpath = "projects/%s/results/%s.txt" % (self.testCases.projectName,name)
            if not os.path.exists ("projects/%s/" % self.testCases.projectName):
                os.mkdir("projects/%s/" % self.testCases.projectName)
        text_file = open(txtpath, "w")
        text_file.write("Project Id:%s, Name:%s, Version:%s\n" % (self.testCases.projectId, self.testCases.projectName, self.testCases.projectVersion))
        text_file.write("TestResults for %s\n" % name)
        for case in test_list:
            for c in self.testCases.Cases.itervalues():
                if c.id == case:
                    for t in self.testedCases:
                        if c.id == t:
                            if self.results[c]:
                                text_file.write('case%s: ' % c.id + str(c.status))
                                text_file.write("\n")
        text_file.close()     
        
    def WriteXml(self):
        '''
        This method writes test results related to a single
        test case or a complete test plan into an xml file
        '''
        test_list = []
        if self.testPlanName:
            name = 'plan_%s'% self.testPlanName
        else:
            name = 'case_%s' % self.testedCases
        for c in self.testCases.Cases.itervalues():
            test_list.append(c.id)
        test_list.sort()   
        if self.mainDir != 'projects/':
            filepath = self.mainDir+"results/%s.txt" % name
            if not os.path.exists (self.mainDir+"results/"):
                os.mkdir(self.mainDir+"results/")
        else:
            filepath = "projects/%s/results/%s.txt" % (self.testCases.projectName,name)
            if not os.path.exists ("projects/%s/" % self.testCases.projectName):
                os.mkdir("projects/%s/" % self.testCases.projectName)
        
        root = etree.Element("Project", id=self.testCases.projectId, name=self.testCases.projectName, version=self.testCases.projectVersion)
        results = etree.ElementTree(root)
        testResults = etree.SubElement(root,"testResults", id=str(name))
        testCases = etree.SubElement(testResults,"testCases")
        
        for case in test_list:
            for c in self.testCases.Cases.itervalues():
                if c.id == case:
                    for t in self.testedCases:
                        if c.id == t:
                            if self.results[c]:
                                testCase = etree.SubElement(testCases,"testCase", id=str(c.id),sd=str(c.sd),type=str(c.type))
                                result = etree.SubElement(testCase,"result")
                                result.text = str(c.status)
        indent(root)                
        results.write (filepath, encoding='iso-8859-1')
        
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