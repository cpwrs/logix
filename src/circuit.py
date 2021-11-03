"""
Circuit
Author: Carson Powers

The circuit class creates and controls a directed graph 
that represents the logix gate diagram in logix.
"""

import networkx as nx


class Circuit:
    """A class to represent a circuit object. (graph of connected inputs, gates, and outputs"""

    def __init__(self):
        """Initialize the circuit graph and define logic functions."""

        self.graph = nx.DiGraph()

        self.logic = {
            "or": (lambda in1, in2: in1 or in2),
            "and": (lambda in1, in2: in1 and in2),
            "not": (lambda in1: not(in1)),
            "nor": (lambda in1, in2: not(in1 or in2)),
            "nand": (lambda in1, in2: not(in1 and in2)),
            "xor": (lambda in1, in2: in1 != in2),
            "xnor": (lambda in1, in2: in1 == in2),
            "buffer": (lambda in1: in1)
        }


    def change_output(self, id, val):
        """
        Function to change the output of an edge with zero inputs
        Ex: An input switch on the diagram.
        """

        self.graph.nodes[id]["output"] = val
        self.update(id)


    def update(self, start_id):
        """Recursive function that updates all out nodes"""

        # Find out edges
        for edge in self.graph.out_edges(start_id):
            curr_output = self.graph.nodes[start_id]["output"] # Current output of node start_id
            input_position = self.graph.edges[edge[0], edge[1]]["position"] # "Position" (top or bottom of gate = 0 or 1) of input
            out_node_id = edge[1] # Out node id based on out edge tuple

            # Applt logic to node, run update on each out node
            self.logicize_node(out_node_id, input_position, curr_output)
            self.update(out_node_id)


    def logicize_node(self, id, input_position, input_value):
        """Apply logic to node with new input value at certain input position"""

        node = self.graph.nodes[id]

        #Only apply logic if it has any (only gates do)
        if node["logic"]:
            # Set new input value
            node["input"][input_position] = input_value
            
            logic_type = node["logic"]
            inputs = node["input"]
            
            # Set output
            if len(inputs) == 2:
                output = self.logic[logic_type](inputs[0], inputs[1])
            else:
                output = self.logic[logic_type](inputs[0])
            self.graph.nodes[id]["output"] = output


    def add_node(self, id, logic, num_inputs, output = False):
        """
        Add node to directed graph with id as the name.
        Create attributes for the inputs and output.
        """

        self.graph.add_node(id, logic = logic, input = [False] * num_inputs, output = output)
    

    def add_edge(self, start_id, end_id, position):
        """
        Add edge to the directed graph given ids of start and end nodes.
        "Position" (0 or 1) denotes if the edge is going to a top or bottom input of a gate.
        """

        self.graph.add_edge(start_id, end_id, position = position)
        self.update(start_id)
        