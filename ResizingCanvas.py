from tkinter import *
""" Canvas that re-sizes when the window size changes

FILENAME
    ResizingCanvas.py

DESCRIPTION
    This is a subclass of Canvas that will automatically resize when the window re-sizes.

AUTHOR
    ebarr
    from:
    http://stackoverflow.com/questions/22835289/how-to-get-tkinter-canvas-to-dynamically-resize-to-window-width
"""


class RC(Canvas):
    """A subclass of Canvas for dealing with resizing of windows"""
    def __init__(self, parent, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)
