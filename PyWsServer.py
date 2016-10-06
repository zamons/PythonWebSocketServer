import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import mbedWSClient
import gui
import threading
""" Simple WebSocket server GUI that uses the Tornado WebSocket handler.

FILENAME
    PyWsServer.py

DESCRIPTION
    This is a simple WebSocket server GUI that uses the Tornado WebSocket handler. It is designed to work with
    microcontrollers programmed with the software available: https://developer.mbed.org/users/defrost/code/IoT_Ex/
    After executing this main file, a GUI will load. Press 'Start' to start the server running. It will listen for
    WebSocket connections on port 4444. When a microcontroller has connected, it will send data to the server every
    3 seconds. The server will save the data to a .csv file every 100 samples from the microcontroller. Pressing the
    'Stop' button will force the server to save all data from memory to disk.
    You can also send data to all connected microcontrollers or a single microcontroller. Currently the only feature
    implemented is the ability to turn on and off an LED on the microcontroller. Set the "Value:" textbox to 1, and the
    "Address:" textbox to "All", and press the 'Send Command to IoTD' button to turn on the LED on all connected
    microcontrollers.
    Messages are output to the console for debugging purposes.

REQUIREMENTS
    Files:
        gui.py
        mbedWSClient.py
        ResizingCanvas.py
        Tornado installed

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

# This is where we keep a list of connected IoTDs
Devices = []
# This is the frame where the graphs are added:
IoTDVisualFrame = []

DEBUG = 0
INFOMSG = 1


def debug_msg(msg):
    if DEBUG:
        print('[IoT : DEBUG] %s' % msg)


def info_msg(msg):
    if INFOMSG:
        print('[IoT : INFO] %s' % msg)


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        info_msg('New connection.')
        Devices.append(mbedWSClient.MbedWSClient(self))
        self.index = len(Devices) - 1

    def on_message(self, message):
        # Saving message:
        debug_msg("Received at index: %d message: %s" % (self.index, message))
        Devices[self.index].append_data(message, IoTDVisualFrame[0])
        # self.write_message(message[::-1])

    def send_message(self, message):
        # Send a message to the client:
        debug_msg("sending message: %s" % message)
        self.write_message(message)

    def on_close(self):
        info_msg('connection closed')

    def check_origin(self, origin):
        return True

    def is_wsconnected(self):
        if self.ws_connection is None:
            return False
        else:
            return True


class TornadoThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.application = tornado.web.Application([(r'/ws', WSHandler)])
        self.http_server = tornado.httpserver.HTTPServer(self.application)
        self.http_server.listen(4444)

    def run(self):
        info_msg("Start a tornado")
        myIP = socket.gethostbyname(socket.gethostname())
        info_msg("*** Websocket Server Started at %s ***" % myIP)
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        info_msg("Stop a tornado")
        tornado.ioloop.IOLoop.instance().stop()
        self.http_server.close_all_connections()
        self.http_server.stop()
        # Save any data left in memory:
        for handler in Devices:
            handler.save_data_to_disk(-1)

    def send_cmd(self, adr, cmd):
        # Send a command string to an IoTD:
        if adr == -1:
            # send the command to all of the IoTDs:
            for handler in Devices:
                if handler.is_connected():
                    handler.send_cmdstr(cmd)

        else:
            # Send it to a particular IoTD.
            # First find the IoTD we are interested in:
            cmd_sent = -1
            # In reality, the outer for loop only goes through once sing the clientDict is a 'global'
            # variable amongst all of the handlers in Devices:
            for handler in Devices:
                for key in handler.clientDict:
                    IoTDID = handler.clientDict[key].ID
                    debug_msg("IoTDID: %d, clientDict[key].ID: %d, key: %d" % (IoTDID, handler.clientDict[key].ID, key))
                    if IoTDID == adr:
                        # This logic is a bit circular and dirty, but it works:
                        if handler.clientDict[key].handle.is_wsconnected():
                            handler.clientDict[key].handle.send_message(cmd)
                            cmd_sent = 1
                        else:
                            info_msg("Connection to IoTD with address: %d lost." % adr)
                            cmd_sent = 0
                        break
                if cmd_sent != -1:
                    break
            if cmd_sent == -1:
                info_msg("IoTD %d is not connected. Command not sent." % adr)

    def clone(self):
        return TornadoThread()

    def setFrame(self, some_frame):
        IoTDVisualFrame.append(some_frame)


MyThread = TornadoThread()
WebSocketGui = gui.WSGui(MyThread)

if __name__ == "__main__":
    # Start the GUI:
    WebSocketGui.start()


