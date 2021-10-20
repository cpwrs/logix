
"""
User Interface
Author: Carson Powers

Displays the user interface of logix using tkinter 
and deploys modules to create and save logix circuits.
"""

import os 
import json
import tkinter as tk
from PIL import ImageTk, Image


class Home:
    """A class to reporesent the home window of the logix application."""
    
    def __init__(self, root, window):
        """Construct Home window widgets."""

        self.window = window
        self.root = root

        # Create main frame, button to open editor (new project)
        self.frame = tk.Frame(self.window)
        self.open_button = tk.Button(self.frame, text = 'Open Editor', height = 1, width = 25, command = self.open_editor)

        # Add frame and button to Home window
        self.open_button.pack()
        self.frame.pack()

    def open_editor(self):
        """Close the home window, open a new window, and instantiate the Editor class."""

        self.window.destroy()
        self.newWindow = tk.Toplevel(self.root)
        self.app = Editor(self.root, self.newWindow)


# Diagram structure
# Diagram (tk.Canvas)
#    Object
#       '---Input points
#       '---Output points


class Editor:
    """A class to represent the main logix editor."""

    def __init__(self, root, window):
        """Construct the sidebar and diagram and their respective widgets."""

        self.window = window
        self.root = root

        # Create window of size 750x750
        self.window.geometry("750x750")

        # Create Sidebar and Diagram widgets (Frame just holds the Canvas inside it)
        self.sidebar = tk.LabelFrame(self.window, text="Gates")
        self.frame = tk.LabelFrame(self.window, text="Diagram")
        self.diagram = tk.Canvas(self.frame, bg = "#808080")

        # Load data regarding the object names and assets from json file
        self.button_data = json.load(open("src/sidebar.json"))
        
        # Create table to hold each tk button, create table to hold objects
        # Craete dictionary loaded_assets to hold loaded image for each type of object
        # *Avoids garbage collection*
        self.buttons = []
        self.objects = []
        self.loaded_assets = {}
        self.object_grabbed = False

        # Load object asset and create button
        for title in self.button_data["gates"]:
            filename = self.button_data["gates"][title]["asset"]
            dimensions = self.button_data["gates"][title]["dimensions"]
            asset = ImageTk.PhotoImage(Image.open(filename).resize(dimensions))
            self.loaded_assets[title] = asset

            button = tk.Button(self.sidebar, text = title, height = 1, width = 10)
            button.bind("<ButtonPress-1>", self.gate_handler)
            self.buttons.append(button)
        
        # Bind diagram to zoom/pan functions
        self.diagram.bind("<MouseWheel>", self.do_zoom)
        self.diagram.bind('<ButtonPress-1>', self.down_handler)
        self.diagram.bind("<B1-Motion>", self.move_handler)

        # Configure the Editor's grid scaling
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(1, weight= 1)
        self.sidebar.columnconfigure(0,weight = 1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # Add object buttons to the sidebar
        for i in range(len(self.buttons)):
            self.buttons[i].grid(row = i, column = 0, sticky = "EW")
        #Add all other widgets to Editor grid
        self.diagram.grid(row = 0, column = 0, sticky = "NSEW")
        self.sidebar.grid(row = 0, column = 0, sticky = "NS")
        self.frame.grid(row = 0, column = 1, sticky = "NSEW")


    def gate_handler(self, event):
        """Handle gate button click and create respective gate on the diagram."""

        title = event.widget['text']
        gate = self.diagram.create_image(20, 20, image = self.loaded_assets[title])
        # Add to list of canvas objects
        self.objects.append(gate)
        # Move image to top layer
        self.diagram.tag_raise(gate)

    
    # Determines whether the mouse is clicking down on an object, sets self.object_grabbed and returns value
    def is_grabbing_object(self, x, y):
        """
        Determine if (x,y) is within coordinates bounding an object on the diagram.
        Set self.object_grabbed and return boolean based on this determination.

        PARAMETERS
        ----------
        x : int
            x position (pixels)
        y : int
            y position (pixels)
        
        RETURNS
        -------
        bool : If (x,y) was within coordinates bounding an object
        """

        # Loop through each objects, newest to oldest (Top to bottom layer)
        for object in reversed(self.objects):
            coords = self.diagram.bbox(object)
            x1, y1, x2, y2 = coords

            # See if (x,y) is inside these coordinates
            if((x1 < x < x2) and (y1 < y < y2)):
                self.object_grabbed = object
                return True

        self.object_grabbed = False
        return False


    # Handles any ButtonPress-1 on the diagram
    def down_handler(self, event):
        """
        Handle ButtonPress-1 event and retrieve coordinates of event. 
        Determine if ButtonPress-1 was over the background or an object, and set up drag variables accordingly
        """

        # Convert event coords to canvas coords (required due to canvas panning)
        x = int(self.diagram.canvasx(event.x))
        y = int(self.diagram.canvasy(event.y))

        if(self.is_grabbing_object(x, y)):
            #Set starting point of object drag
            self.drag_x = x 
            self.drag_y = y
        else:
            # Set starting point of canvas pan
            self.diagram.scan_mark(event.x, event.y) #Doesn't need converted coordinates



    def move_handler(self, event):
        """Handle movement of the mouse after the ButtonDown-1 event. Move diagram objects or pan diagram accordingly"""

        if(self.object_grabbed):
            # Convert mouse coords to canvas coords
            x = int(self.diagram.canvasx(event.x))
            y = int(self.diagram.canvasy(event.y))

            # Calculate distance moved
            diff_x = x - self.drag_x
            diff_y = y - self.drag_y

            self.drag_x = x
            self.drag_y = y
            self.diagram.move(self.object_grabbed, diff_x, diff_y)
        else:
            # Pan diagram
            self.diagram.scan_dragto(event.x, event.y, gain=1)
    

    def do_zoom(self, event):
        """Zoom diagram based on MouseScroll event"""

        x = self.diagram.canvasx(event.x)
        y = self.diagram.canvasy(event.y)
        factor = 1.001 ** event.delta
        self.diagram.scale(tk.ALL, x, y, factor, factor)
        

def main():
    root = tk.Tk()
    # Don't display root, allows only one window to be open at a time
    root.withdraw()
    window = tk.Toplevel(root)
    app = Home(root, window)
    root.mainloop()

if __name__ == '__main__':
    main()