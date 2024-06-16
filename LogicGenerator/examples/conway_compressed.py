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
    
    lg.no_LUT = 2
    lg.LUT_inputs = 5
    lg.LUT_outputs = 2
    lg.no_inputs = 7
    lg.no_outputs = 1
    lg.updateInputIndexLength()
    
    def calcConway_7(m_list_in, m_no_out=1):
        # [central_bit, column_0_lsb, c0_msb, c1_lsb, c1_msb, c2_lsb, c2_msb]
        count = 0
        for i in range(1, len(m_list_in)):
            if m_list_in[i] == 1:
                if i == 1 or i == 3 or i == 5:
                    count += 1
                elif i == 2 or i == 4 or i ==6:
                    count += 2
        if m_list_in[0] == 0:
            if count == 3:
                return True
        else:
            count -= 1
            if count > 1 and count < 4:
                return True
        return False
    
    def defaultStartingGuesses(m_no_LUT, m_LUT_inputs, m_LUT_outputs, m_no_inputs, m_no_outputs, m_input_index_length, m_index_final_output, m_index_LUT_inputs, m_index_LUT_outputs):
        # if no starting guesses should be implemented, return an empty list []
        c = []
        #for i in range(0, m_LUT_inputs):
        #    c.append(m_index_LUT_inputs[m_input_index_length * i + i] == True)
        #print(c)
        return c
    
    lg.runSolver(calcConway_7, defaultStartingGuesses)

