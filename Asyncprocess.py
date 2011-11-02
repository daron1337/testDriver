
#! /usr/bin/env python

import os
import errno
import signal
import threading
import subprocess

class Process(object):
    '''
    Manager for an asynchronous process.
    The process will be run in the background, and its standard output
    and standard error will be collected asynchronously.

    Since the collection of output happens asynchronously (handled by
    threads), the process won't block even if it outputs large amounts
    of data and you do not call Process.read*().

    Similarly, it is possible to send data to the standard input of the
    process using the write() method, and the caller of write() won't
    block even if the process does not drain its input.

    On the other hand, this can consume large amounts of memory,
    potentially even exhausting all memory available.

    Parameters are identical to subprocess.Popen(), except that stdin,
    stdout and stderr default to subprocess.PIPE instead of to None.
    Note that if you set stdout or stderr to anything but PIPE, the
    Process object won't collect that output, and the read*() methods
    will always return empty strings.  Also, setting stdin to something
    other than PIPE will make the write() method raise an exception.
    '''
    def __init__(self, *params, **kwparams):
        if len(params) <= 3:
            kwparams.setdefault('stdin', subprocess.PIPE)
        if len(params) <= 4:
            kwparams.setdefault('stdout', subprocess.PIPE)
        if len(params) <= 5:
            kwparams.setdefault('stderr', subprocess.PIPE)
        self.__pending_input = []
        self.__collected_outdata = []
        self.__collected_errdata = []
        self.__exitstatus = None
        self.__lock = threading.Lock()
        self.__inputsem = threading.Semaphore(0)
        # Flag telling feeder threads to quit
        self.__quit = False
        self.__process = subprocess.Popen(*params, **kwparams)
    
        if self.__process.stdin:
            self.__stdin_thread = threading.Thread(
            name="stdin-thread",
            target=self.__feeder, args=(self.__pending_input,
                            self.__process.stdin))
            self.__stdin_thread.setDaemon(True)
            self.__stdin_thread.start()
            
        if self.__process.stdout:
            self.__stdout_thread = threading.Thread(
            name="stdout-thread",
            target=self.__reader, args=(self.__collected_outdata,
                            self.__process.stdout))
            self.__stdout_thread.setDaemon(True)
            self.__stdout_thread.start()
            
        if self.__process.stderr:
            self.__stderr_thread = threading.Thread(
            name="stderr-thread",
            target=self.__reader, args=(self.__collected_errdata,
                            self.__process.stderr))
            self.__stderr_thread.setDaemon(True)
            self.__stderr_thread.start()
        
    def __del__(self, __killer=os.kill, __sigkill=signal.SIGKILL):
        if self.__exitstatus is None:
            __killer(self.pid(), __sigkill)

    def pid(self):
        '''
        Return the process id of the process.
        Note that if the process has died (and successfully been waited
        for), that process id may have been re-used by the operating
        system.
        '''
        return self.__process.pid
    
    def kill(self, signal):
        '''
        Send a signal to the process.
        Raises OSError, with errno set to ECHILD, if the process is no
        longer running.
        '''
        if self.__exitstatus is not None:
            # Throwing ECHILD is perhaps not the most kosher thing to do...
            # ESRCH might be considered more proper.
            raise OSError(errno.ECHILD, os.strerror(errno.ECHILD))
        os.kill(self.pid(), signal) 
        
    def terminate(self, graceperiod=1):
        '''
        Terminate the process, with escalating force as needed.
        First try gently, but increase the force if it doesn't respond
        to persuassion.  The levels tried are, in order:
         - close the standard input of the process, so it gets an EOF.
         - send SIGTERM to the process.
         - send SIGKILL to the process.
        '''
        
        if self.__process.stdin:
            self.closeinput()
                
        self.kill(signal.SIGTERM)
        self.kill(signal.SIGKILL)
        
    def __reader(self, collector, source):
        '''
        Read data from source until EOF, adding it to collector.
        '''
        while True:
            try:
                data = os.read(source.fileno(), 65536)
            except AttributeError:
                pass
            self.__lock.acquire()
            collector.append(data)
            self.__lock.release()
            if data == "":
                source.close()
                break
        return

    def __feeder(self, pending, drain):
        '''
        Feed data from the list pending to the file drain.
        '''
        while True:
            self.__inputsem.acquire()
            self.__lock.acquire()
            if not pending and self.__quit:
                drain.close()
                self.__lock.release()
                break
            data = pending.pop(0)
            self.__lock.release()
            drain.write(data)

    def read(self):
        '''
        Read data written by the process to its standard output.
        '''
        self.__lock.acquire()
        outdata = "".join(self.__collected_outdata)
        del self.__collected_outdata[:]
        self.__lock.release()
        return outdata

    def readerr(self):
        '''
        Read data written by the process to its standard error.
        '''
        self.__lock.acquire()
        errdata = "".join(self.__collected_errdata)
        del self.__collected_errdata[:]
        self.__lock.release()
        return errdata

    def readboth(self):
        '''
        Read data written by the process to its standard output and error.
        Return value is a two-tuple ( stdout-data, stderr-data ).
        '''
        self.__lock.acquire()
        outdata = "".join(self.__collected_outdata)
        del self.__collected_outdata[:]
        errdata = "".join(self.__collected_errdata)
        del self.__collected_errdata[:]
        self.__lock.release()
        return outdata,errdata
    
    def _peek(self):
        self.__lock.acquire()
        output = "".join(self.__collected_outdata)
        error = "".join(self.__collected_errdata)
        self.__lock.release()
        return output,error

    def write(self, data):
        '''
        Send data to a process's standard input.
        '''
        if self.__process.stdin is None:
            raise ValueError("Writing to process with stdin not a pipe")
        self.__lock.acquire()
        self.__pending_input.append(data)
        self.__inputsem.release()
        self.__lock.release()

    def closeinput(self):
        '''
        Close the standard input of a process, so it receives EOF.
        '''
        self.__lock.acquire()
        self.__quit = True
        self.__inputsem.release()
        self.__lock.release()     