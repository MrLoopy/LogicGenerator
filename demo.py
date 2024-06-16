#!/usr/bin/env python3

from LogicGenerator.SAT_core.core import *

if __name__ == '__main__':

    #
    # Initialize an instance of the LogicGenerator
    #
    lg = Logic_Generator()

    #
    # test if cvc5 is set up correct and can be executed
    #
    lg.testCvc5()
    
    #
    # you can use the logging-function of LG (input needs to be a string)
    #
    lg.log("Hello World!")

    #
    # run the default settings with the default-example (4-Mux)
    #
    lg.runDefault()

    #
    # change parameters of LG if needed and fit them to your specific problem
    #
    lg.setVersion('parallel')       # Version can be basic, inc or parallel, recommended: parallel
    lg.setExecutionMode('F')        # Mode can be F or ZV, recommended: F
    lg.printConfig = True           # should a LUT-structure be printed if one is found, recommended: True
    lg.benchmark = False            # if True, only output the final meassured time, recommended: False
    lg.no_processes = 4             # How many parallel Processes should be started, only applicable if version == parallel
    lg.depth = 2                    # How many parameters should set different processes appart, must be fitted to no_processes

    lg.no_LUT = 2                   # numer of generated LUTs
    lg.LUT_inputs = 4               # numer of generated inputs per LUT
    lg.LUT_outputs = 1              # numer of generated outputs per LUT
    lg.no_inputs = 6                # numer of global inputs of the problem
    lg.no_outputs = 1               # numer of global outputs of the problem

    #
    # print the current parameters of LG
    #
    lg.printParameters()
    
    #
    # write a calcOutput-function, that needs to be given to the LG when running
    # it. From a list of inputs and the number of the output, return if this
    # output should be True or False for that input-configuration
    #
    def calcMux(m_list_in, m_no_out = 1):
        if bool(m_list_in[0]) and bool(m_list_in[1]):
            return bool(m_list_in[2])
        if bool(m_list_in[0]) and not bool(m_list_in[1]):
            return bool(m_list_in[3])
        if not bool(m_list_in[0]) and bool(m_list_in[1]):
            return bool(m_list_in[4])
        return bool(m_list_in[5])

    #
    # write starting-guesses for the solver. If not wanted, return an empty list []
    # a common example is to connect the first inputs to the first LUT
    #
    def defaultStartingGuesses(m_no_LUT, m_LUT_inputs, m_LUT_outputs, m_no_inputs, m_no_outputs, m_input_index_length, m_index_final_output, m_index_LUT_inputs, m_index_LUT_outputs):
        # if no starting guesses should be implemented, return an empty list []
        c = []
        for i in range(0, m_LUT_inputs):
            c.append(m_index_LUT_inputs[m_input_index_length * i + i] == True)
        #print(c)
        return c

    #
    # run the solver with the priviously defined output-function,
    # starting-guesses nd parameters
    #    
    lg.runSolver(calcMux, defaultStartingGuesses)
    

