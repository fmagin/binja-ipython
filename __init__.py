
import threading
import sys
import signal
# this is the heavy monkey-patching that actually works
# i.e. you can start the kernel fine and connect to it e.g. via
# ipython console --existing
signal.signal = lambda *args, **kw: None

from binaryninja import *

import os
from ipykernel import connect_qtconsole
import ctypes

#from IPython.kernel.zmq.kernelapp import IPKernelApp
from ipykernel.kernelapp import IPKernelApp


def redirect_stdio():
    # Ipython uses sys.__stdout__ which leads to problem at least on windows if it isn't replaced
    # TODO: There should be a better way that doesn't break the binja integrated shell
    sys.__stdout__ = os.open(os.devnull, 'w')

class KernelWrapper():
    def __init__(self):
        self.app = IPKernelApp.instance()
        return

    def start(self):
        self.thread = threading.Thread(target=self._run_kernel)
        self.thread.start()

    def _run_kernel(self):
        self.app.init_signal = lambda *args, **kw: None
        redirect_stdio()
        self.app.initialize()
        self.app.start()


    def inject_interrupt(self, bv):
        thread_obj = self.thread
        exception = KeyboardInterrupt
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_obj.ident), ctypes.py_object(exception))


    def spawn_qt(self, bv):
        connect_qtconsole(argv=["--no-confirm-exit",])
        return





kw = KernelWrapper()

kw.start()


PluginCommand.register("Binja IPython: Start QT Shell", "Binja IPython", kw.spawn_qt)
PluginCommand.register("Binja IPython: Interrupt", "Binja IPython", kw.inject_interrupt)



