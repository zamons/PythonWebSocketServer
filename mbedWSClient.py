import time
import os
import ResizingCanvas
from tkinter import *
from tkinter import messagebox
from datetime import date
from datetime import datetime
""" mbed Client classes

FILENAME
    mbedWSClient.py

DESCRIPTION
    Contains all of the classes used by the PyWsServer to help manage the incoming data from the microcontrollers, and
    to help send commands to them. Individual microcontrolelrs are identified by their IoT ID, NOT IP address.

    Classes:
        MbedWSClient
            Each _connection_ has an instance of the MbedWSClient created. This class manages the connection between
            the server and the microcontroller. If a microcontroller loses its connection and reconnects, a new
            MbedWSClient instance is created for the new connection.
        MbedData
            Each _IoT ID_ has an instance of the MbedData class created. All of the instances are saved in the
            clientDict{} of the MbedWSClient class. When a new ID connects to the server, a new MbedData instance is
            created. Therefore, if a microcontroller loses its connection and reconnects, its data is saved in the same
            instance of MbedData that was created during its _first_ connection to the server.
        IoTVisual
            Each _IoT ID_ has an instance of hte IoTVisual class created. All instances of this class are saved in the
            frameDict{} of the MbedWSClient class. Like the MbedData class, a new IoTVisual class is created for each
            new IoT ID that connects to the server. This class is responsible for the GUI objects associated with each
            IoT devices, and updating the GUI everytime new data is received.

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

DEBUG = 0
INFOMSG = 1

SENDCOUNTERIDX = 1
TEMPIDX = 2
MAXVALUES = 3

TMAX = 125.0
TMIN = -40.0
SAVECOUNTER = 100
DATADIRECTORY = "./Data/"



def debug_msg(msg):
    if DEBUG:
        print('[mbedWSClient : DEBUG] %s' % msg)


def info_msg(msg):
    if INFOMSG:
        print('[mbedWSClient : INFO] %s' % msg)


class MbedWSClient(object):
    frameDict = {}
    clientDict = {}
    lastSaveDict = {}
    lastSaveDate = {}

    def __init__(self, wshandle):
        self.handle = wshandle
        info_msg("Client added to list")

    def append_data(self, data_string, iot_frame):
        info_msg("Received: %s" % data_string)
        # Parse the data:
        data = data_string.split(",")
        # Check to see if the IoTD is in the dictionary:
        IoTID = int(data[0])
        if IoTID in self.clientDict:
            # Check to see if the date has changed:
            # Get the current date:
            current_date = "%d%02d%02d" % (date.today().year, date.today().month, date.today().day)
            if current_date != self.lastSaveDate[IoTID]:
                # Save the data before we append the next day's data:
                self.save_data_to_disk(IoTID)
                self.lastSaveDate[IoTID] = current_date
            # Add data, and update the handle every time in case it changes:
            self.clientDict[IoTID].append_data(data, self.handle)
            debug_msg("New data for Client (%d) received" % IoTID)
        else:
            # create a new entry:
            debug_msg("New Client (%d) data received, adding to dictionary" % IoTID)
            self.clientDict[IoTID] = MbedData(data, self.handle)
            # Add a new canvas to the gui:
            self.frameDict[IoTID] = IoTVisual(iot_frame, IoTID)
            # Add a last save number:
            self.lastSaveDict[IoTID] = 0
            # Add the last save date:
            self.lastSaveDate[IoTID] = "%d%02d%02d" % (date.today().year, date.today().month, date.today().day)
        # Update the GUI:
        self.frameDict[IoTID].updateData(data)
        # Check to see if we need to save the data:
        if (len(self.clientDict[IoTID].data_array[0]) - self.lastSaveDict[IoTID]) > SAVECOUNTER:
            self.save_data_to_disk(IoTID)

    def save_data_to_disk(self, iot_to_save):
        # if iot_to_save = -1, save them all, else just iot_to_save:
        if iot_to_save < 0:
            # Save them all!
            for key in self.clientDict:
                IoTID = self.clientDict[key].ID
                # Check to see if the data directory exists:
                if os.path.isdir(DATADIRECTORY) == FALSE:
                    # Create the data directory:
                    os.mkdir(DATADIRECTORY)
                # Create the filename:
                filename = "%sIoTD%03d_%d%02d%02d.csv" % (DATADIRECTORY, IoTID, date.today().year, date.today().month,
                                                          date.today().day)
                # Open the file and write to it:
                save_file = True
                while save_file:
                    try:
                        fp = open(filename, 'a+')
                        save_file = False
                    except PermissionError:
                        messagebox.showinfo("Permission Error",
                                            "Permission denied when trying to save regular data. Press OK to try again.")
                save_string = ""
                for ii in range(self.lastSaveDict[IoTID], len(self.clientDict[IoTID].data_array[0])):
                    # Create the string to write
                    save_string = "%s%s" % (save_string, datetime.fromtimestamp(
                        self.clientDict[IoTID].data_array[0][ii]).strftime("%H:%M:%S.%f"))
                    for jj in range(1, MAXVALUES):
                        save_string = "%s, %f" % (save_string, self.clientDict[IoTID].data_array[jj][ii])
                    save_string = "%s\n" % save_string
                # Write all of the data in one go:
                fp.write(save_string)
                # Close the file:
                fp.close()
                # Update the counters:
                self.lastSaveDict[IoTID] = len(self.clientDict[IoTID].data_array[0])
        else:
            # save one iot:
            IoTID = iot_to_save
            # Check to see if the data directory exists:
            if os.path.isdir(DATADIRECTORY) == FALSE:
                # Create the data directory:
                os.mkdir(DATADIRECTORY)
            # Create the filename:
            filename = "%sIoTD%03d_%d%02d%02d.csv" % (DATADIRECTORY, IoTID, date.today().year, date.today().month,
                                                      date.today().day)
            # Open the file and write to it:
            fp = open(filename, 'a+')
            save_string = ""
            for ii in range(self.lastSaveDict[IoTID], len(self.clientDict[IoTID].data_array[0])):
                # Create the string to write
                save_string = "%s%s" % (save_string, datetime.fromtimestamp(
                    self.clientDict[IoTID].data_array[0][ii]).strftime("%H:%M:%S.%f"))
                for jj in range(1, MAXVALUES):
                    save_string = "%s, %f" % (save_string, self.clientDict[IoTID].data_array[jj][ii])
                save_string = "%s\n" % save_string
            # Write all of the data in one go:
            fp.write(save_string)
            # Close the file:
            fp.close()
            # Update the counters:
            self.lastSaveDict[IoTID] = len(self.clientDict[IoTID].data_array[0])

    def send_command(self, cmd, value):
        self.handle.send_message("%d, %.5f" % (cmd, value))

    def send_cmdstr(self, cmd):
        self.handle.send_message("%s" % cmd)

    def get_id(self):
        return self.ID

    def is_connected(self):
        return self.handle.is_wsconnected()


class IoTVisual(object):
    def __init__(self, parent_frame, id_num):
        # Create a new canvas for this IoTD:
        debug_msg("Creating a new cavas...")
        self.IoTFrame = Frame(parent_frame, bd=5, relief=SUNKEN)
        self.gsize = Grid.size(parent_frame)
        # Shrink the frame to fit the new widget:
        parent_frame.pack(side=BOTTOM, fill=NONE, expand=NO)
        w = parent_frame.winfo_width()
        h = parent_frame.winfo_height()
        if self.gsize[0] > 0:
            debug_msg("New width: %.3f" % (w * self.gsize[0] / (self.gsize[0] + 1) - 1))
            Grid.grid_propagate(parent_frame, flag=FALSE)
            parent_frame.config(width=(w * self.gsize[0] / (self.gsize[0] + 1) - 1))
            parent_frame.update_idletasks()
        self.IoTFrame.grid(row=0, column=self.gsize[0], sticky=N+S+E+W)
        self.myCanvas = ResizingCanvas.RC(self.IoTFrame, width=100, height=200, bg='grey', highlightthickness=0)
        self.myCanvas.pack(side=TOP, fill=BOTH, expand=YES)
        self.myIoTDLabel = Label(self.IoTFrame, text="IoTD: %d" % id_num)
        self.myIoTDLabel.pack(side=TOP, fill=X)
        self.SendCounterLabelVar = StringVar()
        self.SendCounterLabelVar.set("Waiting for IoTD Send Counter...")
        self.mySendCounterLabel = Label(self.IoTFrame, textvariable=self.SendCounterLabelVar)
        self.mySendCounterLabel.pack(side=TOP, fill=X)
        Grid.columnconfigure(parent_frame, self.gsize[0], weight=1)
        Grid.rowconfigure(parent_frame, 0, weight=1)
        # Re-expand the canvas:
        parent_frame.config(height=h)   # This is needed because the height will reset to 0
        parent_frame.pack(side=BOTTOM, fill=BOTH, expand=YES)

    def updateData(self, data):
        # Get the dimensions of the canvas:
        h = self.myCanvas.winfo_height()
        w = self.myCanvas.winfo_width()
        # Delete everything on the canvas:
        self.myCanvas.delete(ALL)
        # Redraw the voltages:
        Temp = float(data[TEMPIDX])
        nrect = 1
        nr = 0
        # Draw the temperature:
        if Temp > TMIN:
            self.myCanvas.create_rectangle(w/nrect*nr, h, w/nrect*(nr+1), h-h*(Temp-TMIN)/(TMAX-TMIN), fill="red")
            self.myCanvas.create_text(w/(2*nrect)*(1+2*nr), h-h*(Temp-TMIN)/(TMAX-TMIN), anchor=N, text="%.3f deg C" % Temp)
        elif Temp > TMAX:
            self.myCanvas.create_rectangle(w / nrect * nr, h, w / nrect * (nr + 1), 0, fill="red")
            self.myCanvas.create_text(w / (2 * nrect) * (1 + 2 * nr), 0, anchor=N, text="^ %.3f  deg C ^" % Temp)
        else:
            self.myCanvas.create_rectangle(w/nrect*nr, h, w/nrect*(nr+1), h, fill="red")
            self.myCanvas.create_text(w/(2*nrect)*(1+2*nr), h, anchor=S, text="%.3f deg C" % Temp)
        nr += 1
        # Update the labels:
        self.SendCounterLabelVar.set("Send Counter: %.0f" % float(data[SENDCOUNTERIDX]))


class MbedData(object):
    def __init__(self, data, handle):
        # Initialize the data array:
        self.data_array = [[0.0 for ii in range(1)] for ii in range(MAXVALUES)]
        self.ID = int(data[0])
        self.handle = handle
        for ii in range(0, MAXVALUES):
            if ii == 0:
                self.data_array[0][0] = float(time.time())
            else:
                self.data_array[ii][0] = float(data[ii])

    def append_data(self, data, handle):
        # Data is a list of strings
        self.handle = handle
        # Add data:
        for ii in range(0, MAXVALUES):
            if ii == 0:
                self.data_array[0].append(float(time.time()))
            else:
                self.data_array[ii].append(float(data[ii]))
        debug_msg("Data appended to IoTD.")




