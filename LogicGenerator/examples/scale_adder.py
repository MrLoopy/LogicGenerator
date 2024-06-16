#!/usr/bin/env python3

import sys, os
# Add the path to the SAT_core folder in order to import the Logic_Generator:
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SAT_core.core import *

if __name__ == '__main__':

    lg = Logic_Generator()

    lg.setVersion('parallel')
    lg.setExecutionMode('F')
    lg.printConfig = True
    lg.benchmark = False
    lg.no_processes = 4
    lg.depth = 2
    
    lg.no_LUT = 3
    lg.LUT_inputs = 5
    lg.LUT_outputs = 2
    lg.no_inputs = 5
    lg.no_outputs = 3
    lg.updateInputIndexLength()
    
    def calcAdd(m_list_in, m_no_out = 1):
        # m_no_out[0]=LSB
        count = 0
        for i in range(0, len(m_list_in)):
            if m_list_in[i] == 1:
                count += 1
        return bool((int)(count / (2 ** m_no_out)) % 2)
    
    def defaultStartingGuesses(m_no_LUT, m_LUT_inputs, m_LUT_outputs, m_no_inputs, m_no_outputs, m_input_index_length, m_index_final_output, m_index_LUT_inputs, m_index_LUT_outputs):
        # if no starting guesses should be implemented, return an empty list []
        c = []
        for i in range(0, m_LUT_inputs):
            c.append(m_index_LUT_inputs[m_input_index_length * i + i] == True)
        #print(c)
        return c
    
    lg.runSolver(calcAdd, defaultStartingGuesses)

