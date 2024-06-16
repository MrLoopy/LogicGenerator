#!/usr/bin/env python3

import sys, os
# Add the path to the SAT_core folder in order to import the Logic_Generator:
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SAT_core.core import *

if __name__ == '__main__':

    lg = Logic_Generator()

    lg.benchmark = True
    lg.setVersion('parallel')
    lg.setExecutionMode('F')
    lg.printConfig = True
    lg.no_processes = 4
    lg.depth = 2
    
    lg.no_LUT = 2
    lg.LUT_inputs = 4
    lg.LUT_outputs = 1
    lg.no_inputs = 6
    lg.no_outputs = 1
    lg.updateInputIndexLength()
    
    def calcMux(m_list_in, m_no_out = 1):
        if bool(m_list_in[0]) and bool(m_list_in[1]):
            return bool(m_list_in[2])
        if bool(m_list_in[0]) and not bool(m_list_in[1]):
            return bool(m_list_in[3])
        if not bool(m_list_in[0]) and bool(m_list_in[1]):
            return bool(m_list_in[4])
        return bool(m_list_in[5])
    
    def defaultStartingGuesses(m_no_LUT, m_LUT_inputs, m_LUT_outputs, m_no_inputs, m_no_outputs, m_input_index_length, m_index_final_output, m_index_LUT_inputs, m_index_LUT_outputs):
        # if no starting guesses should be implemented, return an empty list []
        c = []
        for i in range(0, m_LUT_inputs):
            c.append(m_index_LUT_inputs[m_input_index_length * i + i] == True)
        #print(c)
        return c
    
    lg.runSolver(calcMux, defaultStartingGuesses)

