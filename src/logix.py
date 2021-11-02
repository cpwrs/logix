
"""
Logix
Author: Carson Powers

Displays the user interface of logix using tkinter 
and deploys modules to create and save logix circuits.
"""

import os 
import json
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from ttkthemes import ThemedStyle
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
        self.window.configure(background="#181818")

        style = ThemedStyle(self.window)
        style.set_theme("equilux")

        # Create Sidebar and Diagram widgets (Frame just holds the Canvas inside it)
        self.sidebar = ttk.LabelFrame(self.window, text = "Objects", padding = 4)
        self.gate_frame = ttk.LabelFrame(self.sidebar, text = "Gates", padding = 4)
        self.gate_buttons = []
        self.input_frame = ttk.LabelFrame(self.sidebar, text = "Inputs", padding = 4)
        self.input_buttons = []

        self.frame = ttk.LabelFrame(self.window, text="Diagram", padding = 2)
        self.diagram = tk.Canvas(self.frame, bg = "#404040")
        
        # Create menu widget with themed menubuttons
        # TODO: Add cascade options and functionality
        self.menu = tk.Menu(self.window)
        self.window.config(menu = self.menu)
        self.file_menu = tk.Menu(self.menu)
        self.edit_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label = "File", menu = self.file_menu)
        self.menu.add_cascade(label = "Edit", menu = self.edit_menu)

        # Load data regarding the object names and assets from json file
        self.object_data = json.load(open("src/objects.json"))
        self.gate_data = self.object_data["gates"]
        self.input_data = self.object_data["inputs"]
        
        # Create table to hold each tk button, create table to hold objects
        # Create dictionary loaded_assets to hold loaded image for each type of object
        # *Avoids garbage collection and helps to reference tag names*
        self.objects = []
        self.nodes = []
        self.edges = []
        self.loaded_assets = {} # key = title, value = asset

        # Create variables to control the state of diagram actions
        self.state = False #State of object grabbed (node, object, or canvas)
        self.grabbed_object = False
        self.temp_edge = False

        # Load object asset and create button
        # Start by loading gate objects
        gate_dimensions = self.gate_data["dimensions"]
        for title in self.object_data["gates"]["gate_types"]:
            filename = "assets/" + title + ".png"
            asset = ImageTk.PhotoImage(Image.open(filename).resize(gate_dimensions))
            self.loaded_assets[title] = asset

            button = ttk.Button(self.gate_frame, text = title, width = 10)
            button.bind("<ButtonPress-1>", self.draw_gate)
            self.gate_buttons.append(button)

        #Next, load input objects and create their buttons
        for input in self.input_data:
            default_filename = self.input_data[input]["default_asset"]
            dimensions = self.input_data[input]["dimensions"]
            img = Image.open(default_filename).resize(dimensions)
            print(img.mode)
            asset = ImageTk.PhotoImage(img)
            self.loaded_assets[input] = asset

            if self.input_data[input].get("changed_asset"):
                changed_filename = self.input_data[input]["changed_asset"]
                asset = ImageTk.PhotoImage(Image.open(changed_filename).resize(dimensions))
                self.loaded_assets[(input + "_changed")] = asset

            button = ttk.Button(self.input_frame, text = input, width = 10)
            button.bind("<ButtonPress-1>", self.draw_input)
            self.input_buttons.append(button)
        
        # Bind diagram to zoom/pan functions
        self.diagram.bind("<MouseWheel>", self.do_zoom)
        self.diagram.bind("<ButtonPress-1>", self.down_handler)
        self.diagram.bind("<ButtonRelease-1>", self.up_handler)
        self.diagram.bind("<B1-Motion>", self.move_handler)

        # Configure the Editor's grid scaling
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(1, weight= 1)

        self.sidebar.rowconfigure(0,weight = 0)
        self.sidebar.rowconfigure(1, weight = 1)
        self.sidebar.columnconfigure(0, weight = 1)

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # Add object buttons to the sidebar
        for i in range(len(self.gate_buttons)):
            self.gate_buttons[i].grid(row = i, column = 0, sticky = "EW")
        for i in range(len(self.input_buttons)):
            self.input_buttons[i].grid(row = i, column = 0, sticky = "EW")
        # Add all other widgets to Editor grid
        self.diagram.grid(row = 0, column = 0, sticky = "NSEW")
        self.sidebar.grid(row = 0, column = 0, sticky = "NS")
        self.gate_frame.grid(row = 0, column = 0, sticky = "NSEW")
        self.input_frame.grid(row = 1, column = 0, sticky = "NSEW")
        self.frame.grid(row = 0, column = 1, sticky = "NSEW")


    def draw_node(self, coords, color, type, object_id):
        """
        Create a node on the diagram and appropriately tag it.
        
        PARAMETERS
        ----------
        coords : table
                 x0, y0, x1, y1 position (pixels)
        color : string
                node fill color (hexadecimal)
        type : string
               type of node ("input" or "output")
        object_id: tagOrId
                 integer id of object the node is being attached to
        """

        # Create node at coords with color
        x0, y0, x1, y1 = coords
        node = self.diagram.create_oval(x0, y0, x1, y1, fill = color)

        # Add node tags
        self.diagram.addtag_withtag(type, node)
        self.diagram.addtag_withtag("object" + str(object_id), node)
        self.diagram.tag_raise(node)
        self.nodes.append(node)


    def draw_gate(self, event):
        """
        Handle gate button click and create respective gate and nodes on the diagram.
        Appropriately tag gate.
        """

        title = event.widget['text']
        num_inputs = self.gate_data["gate_types"][title]
        node_fill_color = self.gate_data["node_fill"]

        gate = self.diagram.create_image(0, 0, image = self.loaded_assets[title])
        self.diagram.tag_raise(gate)
        self.objects.append(gate)

        # Create input nodes
        if num_inputs == 1:
            coords = self.gate_data["input_node_position"]
            self.draw_node(coords, node_fill_color, "input", gate)
        else:
            for i in range(num_inputs):
                coords = self.gate_data["two_input_node_positions"][i]
                self.draw_node(coords, node_fill_color, "input", gate)
        
        # Create output node
        coords = self.gate_data["output_position"]
        self.draw_node(coords, node_fill_color, "output", gate)


    def draw_input(self, event):
        """
        Handle input button click and create the correct object on the diagram.
        Appropriately tag input object and add output node
        """

        title = event.widget['text']
        node_fill_color = self.object_data["gates"]["node_fill"]

        input = self.diagram.create_image(0, 0, image = self.loaded_assets[title])
        self.diagram.tag_raise(input)
        self.objects.append(input)

        output_coords = self.input_data[title]["output_position"]
        self.draw_node(output_coords, node_fill_color, "output", input)

    
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
        # Loop through nodes, newest to oldest
        for node in reversed(self.nodes):
            tags = self.diagram.gettags(node)
            touched = False
            output = False
            for tag in tags:
                if tag == "current":
                    touched = True
                if tag == "output":
                    output = True
            if touched and output:
                self.grabbed_object = node
                return("node")

        # Loop through each objects, newest to oldest
        for object in reversed(self.objects):
            tags = self.diagram.gettags(object)
            touched = False
            for tag in tags:
                if tag == "current":
                    self.grabbed_object = object
                    return("object")

        # If not grabbing a node or object, return state canvas
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
            # Check if a valid edge was drawn, complete edge
            valid_edge = False
            edge = self.temp_edge
            start_node = self.grabbed_object
            start_node_tags = self.diagram.gettags(start_node)
            for tag in start_node_tags:
                if "object" in tag:
                    start_gate = int(tag[6])

            # Conditions to meet for valid edge:
            # - Start node can't be the same as end node
            # - End node can't be on same gate as start node
            # - End node can't be an output
            # - end node can't already have an input
            # - Currently under mouse

            for node in reversed(self.nodes):
                new_node = False
                new_gate = False
                is_input = False
                has_input = False
                coords = self.diagram.coords(node)

                #Filters out nodes not being touched
                if self.contains_xy(coords, x, y): 
                    if node != start_node:
                        new_node = True

                    tags = self.diagram.gettags(node)
                    print(tags)
                    for tag in tags:
                        if tag == "input":
                            is_input = True
                        elif ("object" in tag) and (int(tag[6]) != start_gate):
                            new_gate = True
                        elif tag == "has_input":
                            has_input = True

                    if new_node and new_gate and is_input and not(has_input):
                        valid_edge = True
                        self.edges.append(edge)

                        # Adjust edge coords to final position
                        x0, y0 = self.find_center_coords(self.diagram.coords(self.grabbed_object))
                        x1, y1 = self.find_center_coords(self.diagram.coords(node))
                        self.diagram.coords(edge, x0, y0, x1, y1)

                        # Create tags that describe the two nodes the edge conects
                        start_tag = "start" + str(self.grabbed_object)
                        end_tag = "end" + str(node)
                        self.diagram.addtag_withtag(start_tag, edge)
                        self.diagram.addtag_withtag(end_tag, edge)
                        self.diagram.addtag_withtag("has_input", node)

            if valid_edge == False:
                self.diagram.delete(self.temp_edge)
                            
        # Reset grab variables
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
            for node in self.diagram.find_withtag("object" + str(self.grabbed_object)):
                self.diagram.move(node, diff_x, diff_y)
                # Move nodes edges
                # Find edges that start at node
                for edge in self.diagram.find_withtag("start" + str(node)):
                    # Find current coords and update
                    x0, y0, x1, y1 = self.diagram.coords(edge)
                    self.diagram.coords(edge, x0 + diff_x, y0 + diff_y, x1, y1)
                # Find edges that end at node
                for edge in self.diagram.find_withtag("end" + str(node)):
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