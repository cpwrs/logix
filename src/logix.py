
"""
Logix
Author: Carson Powers

Displays the user interface of logix using tkinter 
and deploys modules to create and save logix circuits.
"""

import os 
import json
import tkinter as tk
from tkinter.constants import X
from PIL import ImageTk, Image


class Home:
    """A class to represent the home window of the logix application."""
    
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
        self.object_data = json.load(open("src/objects.json"))
        
        # Create table to hold each tk button, create dictionary to hold objects
        # Create dictionary loaded_assets to hold loaded image for each type of object
        # *Avoids garbage collection and helps to reference tag names*
        self.buttons = []
        self.objects = []
        self.edges = []
        self.loaded_assets = {} # key = title, value = asset

        # Create variables to control the state of diagram actions
        self.state = False #State of object grabbed (node, object, or canvas)
        self.grabbed_object = False
        self.temp_edge = False


        # Load object asset and create button
        # Start by loading gate objects
        gate_dimensions = self.object_data["gates"]["dimensions"]
        for title in self.object_data["gates"]["gate_types"]:
            filename = "assets/" + title + ".png"
            asset = ImageTk.PhotoImage(Image.open(filename).resize(gate_dimensions))
            self.loaded_assets[title] = asset

            button = tk.Button(self.sidebar, text = title, height = 1, width = 10)
            button.bind("<ButtonPress-1>", self.gate_handler)
            self.buttons.append(button)
        
        # Bind diagram to zoom/pan functions
        self.diagram.bind("<MouseWheel>", self.do_zoom)
        self.diagram.bind("<ButtonPress-1>", self.down_handler)
        self.diagram.bind("<ButtonRelease-1>", self.up_handler)
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
        # Add all other widgets to Editor grid
        self.diagram.grid(row = 0, column = 0, sticky = "NSEW")
        self.sidebar.grid(row = 0, column = 0, sticky = "NS")
        self.frame.grid(row = 0, column = 1, sticky = "NSEW")


    def gate_handler(self, event):
        """Handle gate button click and create respective gate and nodes on the diagram."""

        title = event.widget['text']
        num_inputs = self.object_data["gates"]["gate_types"][title]
        node_fill = self.object_data["gates"]["node_fill"]

        gate = self.diagram.create_image(0, 0, image = self.loaded_assets[title])
        self.diagram.tag_raise(gate)
        self.objects.append(gate)

        # Create input nodes
        if num_inputs == 1:
            x0, y0, x1, y1 = self.object_data["gates"]["input_node_position"]
            node = self.diagram.create_oval(x0, y0, x1, y1, fill = node_fill)
            self.diagram.addtag_withtag("input", node)
            self.diagram.addtag_withtag("gate" + str(gate), node)
            self.diagram.tag_raise(node)
            self.objects.append(node)
        else:
            for i in range(len(self.object_data["gates"]["two_input_node_positions"])):
                x0, y0, x1, y1 = self.object_data["gates"]["two_input_node_positions"][i]
                node = self.diagram.create_oval(x0, y0, x1, y1, fill = node_fill)
                self.diagram.addtag_withtag("input", node)
                self.diagram.addtag_withtag("gate" + str(gate), node)
                self.diagram.tag_raise(node)
                self.objects.append(node)
        
        # Create output node
        x0, y0, x1, y1 = self.object_data["gates"]["output_position"]
        output = self.diagram.create_oval(x0, y0, x1, y1, fill = node_fill)
        self.diagram.addtag_withtag("output", output)
        self.diagram.addtag_withtag("gate" + str(gate), output)
        self.diagram.tag_raise(output)
        self.objects.append(output)

    
    def contains_xy(self, coords, x, y):
        """Determine if (x,y) is within coordinates"""

        x1, y1, x2, y2 = coords
        if((x1 < x < x2) and (y1 < y < y2)):
            return True
        else:
            return False

    
    def find_center_coords(self, coords):
        """Determine center (x,y) of x1, y1, x2, y2"""

        x1, y1, x2, y2 = coords
        x = (x1+x2)/2
        y = (y1+y2)/2
        return(x, y)


    def is_node(self, object):
        """Determine if object contains a tag denoting it as a node"""

        tags = self.diagram.gettags(object)
        for tag in tags:
            if tag == "input" or tag == "output":
                return(True)
        return(False)


    def check_grab_state(self, x, y):
        """
        Determine if (x,y) is within coordinates bounding an object, a node or just the diagram.
        Return this determination as a "state" string.

        PARAMETERS
        ----------
        x : int
            x position (pixels)
        y : int
            y position (pixels)
        
        RETURNS
        -------
        state : If (x,y) was within coordinates bounding an object, node, or diagram
        """
        # Loop through each objects, newest to oldest (Top to bottom layer)
        for object in reversed(self.objects):
            # Get object coordinates
            coords = self.diagram.bbox(object)

            if self.contains_xy(coords, x, y):
                self.grabbed_object = object
                tags = self.diagram.gettags(object)
                for tag in tags:
                    #Only allow "tag" state from outputs!
                    if tag == "output":
                        return("node")
                    elif tag == "input":
                        return("canvas")
                return("object")
        return("canvas")


    def down_handler(self, event):
        """
        Handle <ButtonPress-1> event and retrieve coordinates of event. 
        Determine if <ButtonPress-1> was over the background or an object, and set up drag variables accordingly
        """

        # Convert event coords to canvas coords (required due to canvas panning)
        x = int(self.diagram.canvasx(event.x))
        y = int(self.diagram.canvasy(event.y))
        # Set state of mouse grab
        self.state = self.check_grab_state(x, y)

        if(self.state == "object"):
            #Set starting point of object drag
            self.drag_x = x 
            self.drag_y = y
        elif(self.state == "canvas"):
            # Set starting point of canvas pan
            self.diagram.scan_mark(event.x, event.y) #Doesn't need converted coordinates
        elif(self.state == "node"):
            #Find center coords, start edge line
            c_x, c_y = self.find_center_coords(self.diagram.coords(self.grabbed_object))
            self.temp_edge = self.diagram.create_line(c_x, c_y, c_x, c_y, width = 3)


    def up_handler(self, event):
        """
        Handle the <ButtonRelease-1> event and consequent object actions.
        Select an object or complete an edge accordingly.
        """

        # Convert mouse coords to canvas coords
        x = int(self.diagram.canvasx(event.x))
        y = int(self.diagram.canvasy(event.y))

        if self.state == "node":
            # Complete edge if it ends on another node
            edge = self.temp_edge
            valid = False
            # Find gate of starting node
            start_gate = self.diagram.gettags(self.grabbed_object)[1][4]
            # Check if mouse is over a valid final node
            for object in reversed(self.objects):
                # Filter out non-nodes
                if self.is_node(object):
                    # Filter out objects mouse isnt touching
                    if self.contains_xy(self.diagram.bbox(object), x, y):
                        #Find gate final node is attached to
                        end_gate = self.diagram.gettags(object)[1][4]
                        #Filter out final nodes on the same gate
                        if not(start_gate == end_gate):
                            #Final node found! Create final edge
                            valid = True
                            self.edges.append(edge)

                            #Adjust edge coords to final position
                            x0, y0 = self.find_center_coords(self.diagram.coords(self.grabbed_object))
                            x1, y1 = self.find_center_coords(self.diagram.coords(object))
                            self.diagram.coords(edge, x0, y0, x1, y1)

                            #Create tags that describe the two nodes the edge conects
                            start_tag = "start" + str(self.grabbed_object)
                            end_tag = "end" + str(object)
                            self.diagram.addtag_withtag(start_tag, edge)
                            self.diagram.addtag_withtag(end_tag, edge)
                            print(self.diagram.gettags(edge))
            
            if valid == False:
                self.diagram.delete(self.temp_edge)
                            
        #Reset grab variables
        self.object_grabbed = False
        self.temp_edge = False
        self.state = False

        
    def move_handler(self, event):
        """
        Handle movement of the mouse after the <B1-Motion> event. 
        Move diagram objects, pan diagram, or create an edge accordingly.
        """

        # Convert mouse coords to canvas coords
        x = int(self.diagram.canvasx(event.x))
        y = int(self.diagram.canvasy(event.y))

        if(self.state == "object"):
            # Calculate distance moved
            diff_x = x - self.drag_x
            diff_y = y - self.drag_y

            # Reset drag, move object
            self.drag_x = x
            self.drag_y = y
            self.diagram.move(self.grabbed_object, diff_x, diff_y)
            
            # Move objects nodes
            for node in self.diagram.find_withtag("gate" + str(self.grabbed_object)):
                self.diagram.move(node, diff_x, diff_y)
                # Move nodes edges
                # Find edges that start at node
                for edge in self.diagram.find_withtag("start" + str(node)):
                    print("found edge"+str(edge))
                    #Find current coords and update
                    x0, y0, x1, y1 = self.diagram.coords(edge)
                    self.diagram.coords(edge, x0 + diff_x, y0 + diff_y, x1, y1)
                # Find edges that end at node
                for edge in self.diagram.find_withtag("end" + str(node)):
                    print("found edge"+str(edge))
                    # Find current coords and update
                    x0, y0, x1, y1 = self.diagram.coords(edge)
                    self.diagram.coords(edge, x0, y0, x1 + diff_x, y1 + diff_y)

        elif(self.state == "canvas"):
            # Pan diagram
            self.diagram.scan_dragto(event.x, event.y, gain=1)

        elif(self.state == "node"):
            # Find original x, y
            x0, y0 = self.find_center_coords(self.diagram.coords(self.grabbed_object))
            # Update line coords
            self.diagram.coords(self.temp_edge, x0, y0, x, y)
    

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