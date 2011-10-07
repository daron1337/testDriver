'''
Created on Apr 20, 2011

@author: daron1337
'''
from Tkinter import *
import sys, getopt

class Tester(object):
    
    def __init__(self, master, doAction=None, disabled=None):
        '''
        class Constructor
        '''
        
        frame = Frame(master)
        frame.pack()
        self.quit = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.quit.pack(side=LEFT)
        
        if disabled == True:
            self.action = Button(frame, text="Action", command=self.doAction, state=DISABLED)
            self.action.pack(side=LEFT)
        else:
            self.action = Button(frame, text="Action", command=self.doAction)
            self.action.pack(side=LEFT)
        
        if doAction == True:
            self.doAction()
        
        self.Ready()
        
    def Ready(self):
        '''
        '''
        print "Ready"
        
    def doAction(self):
        '''
        '''
        print message
        print "@Log:Tester doAction message=%s" % message

#default Value
message = "Action OK"
doAction = False
disabled = False

try:                                
    opts, args = getopt.getopt(sys.argv[1:], "im:d", ["input", "message=","disabled"]) 
except getopt.GetoptError: 
    print "Error"                                  
    sys.exit(2)
    
for opt, arg in opts:
    if opt in ("-i", "--input"):
        doAction = True
    if opt in ("-m", "--message"):
        message = arg
    if opt in ("-d", "--disabled"):
        disabled = True
root = Tk()

app = Tester(root, doAction, disabled)

root.mainloop()