from tkinter import *
from tkinter import ttk
""" PyWsServer GUI

FILENAME
    gui.py

DESCRIPTION
    This file builds the Server's GUI, and defines callbacks for all of the buttons.

AUTHOR
    Damien Frost

LICENSE
    Copyright (c) 2016 Damien Frost

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

"""

DEBUG = 1
INFOMSG = 1
AllFrames = []
MAJORLABELFONTNAME = "Calibri"
MAAJORLABELFONTSIZE = 13

def debug_msg(msg):
    if DEBUG:
        print('[GUI : DEBUG] %s' % msg)


def info_msg(msg):
    if INFOMSG:
        print('[GUI : INFO] %s' % msg)


class WSGui(object):
    def __init__(self, thread):
        self.root = Tk()
        self.tornado_thread = thread
        # ****************************
        # *** Window Customization ***
        # ****************************
        self.root.title("IoT Server")
        # *********************
        # *** Control Frame ***
        # *********************
        # All of the control instruments should go in this frame!
        self.controlFrame = Frame(self.root)
        self.controlFrame.pack(side=TOP)
        # ***********************
        # *** Server Controls ***
        # ***********************
        self.serverFrame = Frame(self.controlFrame)
        self.serverFrame.pack(side=LEFT)
        # * Label*
        self.serverLabel = Label(self.serverFrame, text="Server Controls", font=(MAJORLABELFONTNAME, MAAJORLABELFONTSIZE))
        self.serverLabel.pack()
        # * Start Button *
        self.startThreadBut = Button(self.serverFrame, text="Start")
        self.startThreadBut.bind("<Button-1>", self.startThreadButCallBack)
        self.startThreadBut.pack()
        # * Stop Button *
        self.stopThreadBut = Button(self.serverFrame, text="Stop")
        self.stopThreadBut.bind("<Button-1>", self.stopThreadButCallBack)
        self.stopThreadBut.pack()
        # ********************
        # *** IoT Controls ***
        # ********************
        self.iotFrame = Frame(self.controlFrame)
        self.iotFrame.pack(side=LEFT)
        # * Label *
        self.iotLabel = Label(self.iotFrame, text="IoTD Controls", font=(MAJORLABELFONTNAME, MAAJORLABELFONTSIZE))
        self.iotLabel.grid(columnspan=2)
        # * iot Variable label *
        self.iotVarLabel = Label(self.iotFrame, text="Variable:")
        self.iotVarLabel.grid(row=2, column=0, sticky=E)
        # * iot value label *
        self.iotValueLabel = Label(self.iotFrame, text="Value:")
        self.iotValueLabel.grid(row=3, column=0, sticky=E)
        # * iot Adr label *
        self.iotAdrLabel = Label(self.iotFrame, text="Address:")
        self.iotAdrLabel.grid(row=4, column=0, sticky=E)
        # * Variable Combo box *
        self.iotVarCombo = ttk.Combobox(self.iotFrame)
        self.iotVarCombo['values'] = "LED"
        self.iotVarCombo.current(0)
        self.iotVarCombo.grid(row=2, column=1, sticky=W)
        # * Value Entry Box *
        self.iotValueEntry = Entry(self.iotFrame)
        self.iotValueEntry.insert(END, "0.0")
        self.iotValueEntry.grid(row=3, column=1, sticky=W)
        # * Address Combo Box *
        self.iotAdrCombo = ttk.Combobox(self.iotFrame)
        self.iotAdrCombo['values'] = ("All", "0", "1", "2")
        self.iotAdrCombo.current(0)
        self.iotAdrCombo.grid(row=4, column=1, sticky=W)
        # * Send button *
        self.iotSendBut = Button(self.iotFrame, text="Send Command to IoTD")
        self.iotSendBut.grid(columnspan=2)
        self.iotSendBut.bind("<Button-1>", self.sendIotCommandCallBack)
        # *******************
        # *** IoT Display ***
        # *******************
        self.iotFrame = Frame(self.root)
        self.iotFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        # * Label *
        self.iotFrameLabel = Label(self.iotFrame, text="IoT Monitor", font=(MAJORLABELFONTNAME, MAAJORLABELFONTSIZE))
        self.iotFrameLabel.pack(side=TOP, fill=X)
        # Create the frame where all of the canvases will be packed against each other on the LEFT:
        self.iotCanvasFrame = Frame(self.iotFrame, bd=5)
        self.iotCanvasFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.tornado_thread.setFrame(self.iotCanvasFrame)

    def start(self):
        self.root.mainloop()

    def startThreadButCallBack(self, event):
        self.tornado_thread.start()

    def stopThreadButCallBack(self, event):
        self.tornado_thread.stop()      # This stops the server
        self.tornado_thread.join()      # This gets the thread to exit, I think
        self.tornado_thread = self.tornado_thread.clone()     # Re-construct the thread so we can restart the server

    def sendIotCommandCallBack(self, event):
        # Create the command string:
        cmd_string = "%s,%s" % (self.iotVarCombo.current()+1, Entry.get(self.iotValueEntry))
        adr = int(self.iotAdrCombo.current()-1)
        debug_msg("adr: %d" % adr)
        self.tornado_thread.send_cmd(-1, cmd_string)


