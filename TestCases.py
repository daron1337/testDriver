#!/usr/bin/env python

## Program:   testDriver
## Module:    testCases.py
## Language:  Python
## Date:      $Date: 2011/04/13 11:41:12 $
## Version:   $Revision: 0.1 $

##      This software is distributed WITHOUT ANY WARRANTY; without even 
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
##      PURPOSE.  See the above copyright notices for more information.

from xml.etree import ElementTree as etree

class TestCases(object):
    '''
    classdocs
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
    '''
    
    def __init__(self, id, sd, type):
        '''
        Constructor
        '''
        self.id = id
        self.sd = sd
        self.type = type
        self.requirements = []
        self.actions = {} # actions dictionary, id:action
        self.responses = {} # responses dictionary, id:action
        

class Action(object):
    '''
    '''
    
    def __init__(self, id, action):
        '''
        Constructor
        '''
        self.id = id
        self.action = action      
    
class Response(object):
    '''
    '''
    
    def __init__(self, id, response):
        '''
        Constructor
        '''
        self.id = id
        self.response = response            