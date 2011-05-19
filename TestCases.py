#!/usr/bin/env python

## Program:   testDriver
## Module:    testCases.py
## Language:  Python
## Date:      $Date: 2011/05/19 09:44:12 $
## Version:   $Revision: 0.1.2 $

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

from xml.etree import ElementTree as etree

class TestCases(object):
    '''
    TestCases class reads xml input file setting
    actions and responses for each case into TestCase object.
    Each testCases object is identified by project Id, name and version.
    This class has the following methods:
    ReadXml: a method for reading xml input file.
    ListCases: a method for printing a summary of test cases.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.projectId = None
        self.projectName = None
        self.projectVersion = None
        self.xmlPath = None
        self.Cases = {} #test cases dictionary, id:case
        
    def ReadXml(self, xmlpath):
        '''
        Reading xml input file.
        '''
        self.xmlPath = xmlpath
        xmldoc = open(xmlpath)
        xmltree=etree.parse(xmldoc)
        project=xmltree.getroot()
        self.projectId = project.attrib['id']
        self.projectName = project.attrib['name']
        self.projectVersion = project.attrib['version']   
        for tc in project.findall(".//testCase"):
            case = TestCase(tc.attrib['id'],tc.attrib['sd'],tc.attrib['type'])
            for descr in tc.findall(".//description"):
                case.description = descr.text
            for req in tc.findall(".//requirement"):
                case.requirements.append(req.text)
            for act in tc.findall(".//action"):
                actionElement = Action(act.attrib['id'],act.text)
                case.actions[actionElement.id]= actionElement
            for resp in tc.findall(".//response"):
                responseElement = Response(resp.attrib['id'],resp.text)
                case.responses[responseElement.id]= responseElement
            self.Cases[case.id] = case
        return self.Cases
               
    def ListCases(self):
        '''
        Printing a summary of test cases.
        '''
        print "Project",self.projectId,self.projectName,"version",self.projectVersion
        print "#####################"
        for c in self.Cases.itervalues():
            print "Case:",c.id,"sequence_diagram:",c.sd,"type:",c.type
            print "Requirements:\n",
            for req in c.requirements:
                print req
            for a in c.actions.itervalues():
                print "action:",a.id, a.action   
                for r in c.responses.itervalues():
                    if a.id == r.id:
                        print "response:",r.id, r.response
            print "#####################"

        
class TestCase(object):
    '''
    TestCase class represents specific test case identified by:
    id: unique Id.
    sd: sequence diagram id related to this test case.
    type: test case type (1,2,3).
    description: a short description of this test case.
    requirements: list of requirements related to this test case.
    actions: dictionary of actions to be executed.
    responses: dictionary of responses to be expected for each action.
    '''
    
    def __init__(self, id, sd, type):
        '''
        Constructor
        '''
        self.id = id
        self.sd = sd
        self.type = type
        self.requirements = []
        self.description = None
        self.actions = {} # actions dictionary, id:action
        self.responses = {} # responses dictionary, id:action
        self.status = None
        

class Action(object):
    '''
    Action class represents each action of a test case and it is
    identified by an unique id and composed by an action.
    '''
    
    def __init__(self, id, action):
        '''
        Constructor
        '''
        self.id = id
        self.action = action      
    
class Response(object):
    '''
    Response class represents each response of a test case and it is
    identified by an unique id and composed by a response.
    '''
    
    def __init__(self, id, response):
        '''
        Constructor
        '''
        self.id = id
        self.response = response            