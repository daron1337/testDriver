#!/usr/bin/env python

## Program:   testDriver
## Module:    Main.py
## Language:  Python
## Date:      $Date: 2011/04/13 14:23:04 $
## Version:   $Revision: 0.1 $


from TestCases import TestCases
from TestDriver import TestDriver

project = TestCases()  #new project to be tested

testCases = project.ReadXml('projects/pippo/testCases.xml')  #read xml
#project.ListCases()                              #std out list cases

testDriver = TestDriver()
testDriver.SetTestCases(project)


'''NEW PLAN'''
testDriver.SetTestPlan('pluto2','1,2,3')
'''GET PLAN'''
testDriver.GetTestPlan('pluto')
'''SINGLE TEST'''
testDriver.ChooseTestCase('2')

