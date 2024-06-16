#!/usr/bin/env python3

import sys, os
# Add the path to the SAT_core folder in order to import the Logic_Generator:
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SAT_core.core import *

if __name__ == '__main__':

    lg = Logic_Generator()

    lg.benchmark = True
    lg.setVersion('basic')
    lg.setExecutionMode('ZV')
    lg.printConfig = True

    lg.no_LUT = 2
    lg.LUT_inputs = 5
    lg.LUT_outputs = 2
    lg.no_inputs = 9
    lg.no_outputs = 1
    lg.updateInputIndexLength()
    
    def calcConway(m_list_in, m_no_out = 1):
        count = 0
        for i in range(1, len(m_list_in)):
            if m_list_in[i] == 1:
                count += 1
        if m_list_in[0] == 0:
            if count == 3:
                return True
        else:
            if count > 1 and count < 4:
                return True
        return False
    
    def defaultStartingGuesses(m_no_LUT, m_LUT_inputs, m_LUT_outputs, m_no_inputs, m_no_outputs, m_input_index_length, m_index_final_output, m_index_LUT_inputs, m_index_LUT_outputs):
        # if no starting guesses should be implemented, return an empty list []
        c = []
        for i in range(0, m_LUT_inputs):
            c.append(m_index_LUT_inputs[m_input_index_length * i + i] == True)
        return c
    
    lg.runSolver(calcConway, defaultStartingGuesses)

