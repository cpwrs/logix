
"""
Logic Gates
Author: Carson Powers
"""

class gate:
    def __init__(self, num_inputs = 2):
        #Create object on screen
        self.input = [False] * num_inputs
        self.output = False

class or_gate(gate):
    def __init__(self):
        super().__init__()
    
    def logic(self):
        res = self.input[0] or self.input[1]
        self.output = res
        return res

class and_gate(gate):
    def __init__(self):
        super().__init__()

    def logic(self):
        res = self.input[0] and self.input[1]
        self.output = res
        return res

class nor_gate(gate):
    def __init__(self):
        super().__init__()
    
    def logic(self):
        res = not(self.input[0] or self.input[1])
        self.output = res
        return res

class nand_gate(gate):
    def __init__(self):
        super().__init__()

    def logic(self):
        res = not(self.input[0] and self.input[1])
        self.output = res
        return res

class xor_gate(gate):
    def __init__(self):
        super().__init__()

    def logic(self):
        res = self.input[0] != self.input[1] 
        self.output = res
        return res

class xnor_gate(gate):
    def __init__(self):
        super().__init__()

    def logic(self):
        res = (self.input[0] == self.input[1])
        self.output = res
        return res

class not_gate(gate):
    def __init__(self):
        super().__init__(1)

    def logic(self):
        res = not self.inputs[0]
        self.output = res
        return res

class buffer_gate(gate):
    def __init__(self):
        super().__init__(1)

    def logic(self):
        res = self.inputs[0]
        self.output = res
        return res
