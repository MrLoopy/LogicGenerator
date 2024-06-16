
import sys, os
import datetime
import time
import logging
import multiprocessing
from cvc5.pythonic import *

class Logic_Generator:
    def __init__(self):
        #
        # setup loggeroutput time, date, file name and info abiut debug- or release-mode
        #
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, datefmt="%H:%M:%S")
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            logging.info("Logic_Generator created by %s in mode DEBUG at %s", os.path.basename(sys.argv[0]), datetime.datetime.now())
        else:
            logging.info("Logic_Generator created by %s in mode RELEASE at %s", os.path.basename(sys.argv[0]), datetime.datetime.now())
        
        #
        # instantiate all needed parameters
        #
        self.__version = 'parallel'
        self.__exe_mode = 'F'
        self.printConfig = True
        self.benchmark = False
        self.no_processes = 4
        self.depth = 2
        self.no_LUT = 2
        self.LUT_inputs = 4
        self.LUT_outputs = 1
        self.no_inputs = 6
        self.no_outputs = 1
        self.updateInputIndexLength()
    def testCvc5(self):
        x, y = Reals('x y')
        solve(0 < x, 0 < y, x + y < 1, x <= y)
        s = Solver()
        s.add(0 < x, 0 < y, x + y < 1, x <= y)
        s.check()
        logging.info("Solver: %s", s.last_result)
        logging.info("Call from %s at %s", os.path.basename(sys.argv[0]), datetime.datetime.now())
    
    def updateInputIndexLength(self):
        self.input_index_length = self.no_inputs + ((self.no_LUT - 1) * self.LUT_outputs)
    
    def log(self, m_message):
        logging.info(m_message)
    def printParameters(self):
        self.updateInputIndexLength()
        logging.info("Current configuration of the Logic_Generator")
        logging.info("version: %s", self.__version)
        logging.info("exe_mode: %s", self.__exe_mode)
        logging.info("printConfig: %s", self.printConfig)
        logging.info("benchmark: %s", self.benchmark)
        logging.info("no_processes: %s", self.no_processes)
        logging.info("depth: %s", self.depth)
        logging.info("self.no_LUT: %s", self.no_LUT)
        logging.info("LUT_inputs: %s", self.LUT_inputs)
        logging.info("LUT_outputs: %s", self.LUT_outputs)
        logging.info("self.no_inputs: %s", self.no_inputs)
        logging.info("no_outputs: %s", self.no_outputs)
        logging.info("input_index_length: %s", self.input_index_length)
    def setVersion(self, m_version):
        #
        # The version can only be changed by function to make sure a valid version is entered (basic, inc or parallel)
        #
        if m_version == 'basic' or m_version == 'inc' or m_version == 'parallel':
            self.__version = m_version
            if not self.benchmark:
                logging.info("Version set to %s", self.__version)
        else:
            logging.error("ERROR: Invalid Version entered: '%s'", m_version)
            logging.error("ERROR: Has to be 'basic', 'inc' or 'parallel'")
    def setExecutionMode(self, m_exe_mode):
        #
        # The execution mode can only be changed by function to make sure a valid execution mode is entered (F or ZV)
        #
        if m_exe_mode == 'F' or m_exe_mode == 'ZV':
            self.__exe_mode = m_exe_mode
            if not self.benchmark:
                logging.info("Execution_mode set to %s", self.__exe_mode)
        else:
            logging.error("ERROR: Invalid Execution_mode entered: '%s'", m_exe_mode)
            logging.error("ERROR: Has to be 'F' or 'ZV'")

    def runDefault(self):
        def defaultStartingGuesses(m_no_LUT, m_LUT_inputs, m_LUT_outputs, m_no_inputs, m_no_outputs, m_input_index_length, m_index_final_output, m_index_LUT_inputs, m_index_LUT_outputs):
            # if no starting guesses should be implemented, return an empty list []
            c = []
            for i in range(0, m_LUT_inputs):
                c.append(m_index_LUT_inputs[m_input_index_length * i + i] == True)
            #print(c)
            return c
        def defaultCalcOutput(m_list_in, m_no_out = 1):
            if bool(m_list_in[0]) and bool(m_list_in[1]):
                return bool(m_list_in[2])
            if bool(m_list_in[0]) and not bool(m_list_in[1]):
                return bool(m_list_in[3])
            if not bool(m_list_in[0]) and bool(m_list_in[1]):
                return bool(m_list_in[4])
            return bool(m_list_in[5])
        self.runSolver(defaultCalcOutput, defaultStartingGuesses)
    def runSolver(self, m_calcOutput, m_createStartingGuesses):
        #
        # Store the function to use for the Output-calculation and the starting-guesses
        # The handling of the starting-guesses has to account for all default options
        #
        self.__calcOutput = m_calcOutput
        self.__createStartingGuesses = m_createStartingGuesses
            
        #
        # Update InputIndexLength in case it has not been updated by the user
        #
        self.updateInputIndexLength()
        
        #
        # make sure the LUT is not larger than the whole problem (this would cause errors in createLutInputConstraints())
        #
        if self.no_inputs < self.LUT_inputs:
            logging.error("ERROR: Number of global Inputs can not be lower than the LUT Size")
            return 0

        #
        # In case of invalid version or exe_mode give Error (should not be able to happen)
        #
        if self.__version != 'basic' and self.__version != 'inc' and self.__version != 'parallel':
            logging.error("ERROR: unexpected version: %s", self.__version)
            return 0
        elif self.__exe_mode != 'F' and self.__exe_mode != 'ZV':
            logging.error("ERROR: unexpected execution mode: %s", self.__exe_mode)
            return 0
        #
        # Check which version should be run and execute corresponding function
        #
        elif self.__version == 'basic':
            self.__runBasic()
        elif self.__version == 'inc':
            self.__runInc()
        elif self.__version == 'parallel':
            self.__runParallel()
        else:
            logging.error("ERROR: unexpected case in 'runSolver()'")

    def __runBasic(self):
        #
        # Start timer and print parameters of the given problem (if not benchmark)
        #
        start_process = time.perf_counter()
        if not self.benchmark:
            logging.info("Start Execution\tGlobal I / O: %s / %s\tLUTs / I / O: %s / %s / %s\tidx length: %s", self.no_inputs, self.no_outputs, self.no_LUT, self.LUT_inputs, self.LUT_outputs, self.input_index_length)

        #
        # Generate all indices that are independent of F and ZV
        #
        index_final_output = []
        for i in range(0, self.no_LUT * self.LUT_outputs * self.no_outputs):
            index_final_output.append(Bool('fOut' + str(i)))
        index_LUT_inputs = []
        for i in range(0, (self.no_LUT * self.LUT_inputs * self.input_index_length)):
            index_LUT_inputs.append(Bool('Linx' + str(i)))
        index_LUT_outputs = []
        for i in range(0, self.no_LUT * self.LUT_outputs * (2 ** self.LUT_inputs)):
            index_LUT_outputs.append(Bool('Loutx' + str(i)))
        #
        # Switch between F and ZV, generate the respective variables and output their sizes (if not benchmark)
        #
        if self.__exe_mode == 'F':
            if not self.benchmark:
                logging.info("generated xout[%s], xin[%s], xfinal[%s]", len(index_LUT_outputs), len(index_LUT_inputs), len(index_final_output))
        elif self.__exe_mode == 'ZV':
            internal_inputs = []
            for i in range(0, self.no_LUT * self.LUT_inputs * (2 ** self.no_inputs)):
                internal_inputs.append(Bool('IntIn' + str(i)))
            internal_outputs = []
            for i in range(0, self.no_LUT * self.LUT_outputs * (2 ** self.no_inputs)):
                internal_outputs.append(Bool('IntOut' + str(i)))
            if not self.benchmark:
                logging.info("generated xout[%s], xin[%s], xfinal[%s], intIn[%s], intOut[%s]", len(index_LUT_outputs), len(index_LUT_inputs), len(index_final_output), len(internal_inputs), len(internal_outputs))
        else:
            logging.error("ERROR: unexpected execution mode")
            return 0

        #
        # Instantiate Solver
        #
        self.__sol = Solver()
        
        #
        # Start timer for the generation of the clauses
        #
        start_generateClauses = time.perf_counter()

        #
        # Generate the constraints for the final outputs for each final output
        #
        for g_out in range(0, self.no_outputs):
            self.__sol.append(self.__createFinalOutputConstraints(index_final_output, g_out))
        
        #
        # Generate the constraints for the Inputs of the LUTs for each LUT
        #
        for lut in range(0, self.no_LUT):
            self.__sol.append(self.__createLutInputConstraints(index_LUT_inputs, lut))
        
        #
        # Generate Starting-Guesses
        #
        startingGuesses = self.__createStartingGuesses(self.no_LUT, self.LUT_inputs, self.LUT_outputs, self.no_inputs, self.no_outputs, self.input_index_length, index_final_output, index_LUT_inputs, index_LUT_outputs)
        for guess in startingGuesses:
            self.__sol.append(guess)

        #
        # Generate LUT-Clauses
        #
        for case in range(0, 2 ** self.no_inputs):
            #
            # calculate the configuration of global inputs for each case
            #
            inputs = []
            for exp in range(self.no_inputs - 1, -1, -1):
                inputs.append((int)(case / (2 ** exp)) % 2)

            #
            # Switch between F and ZV
            #
            if self.__exe_mode == 'F':
                #
                # for each LUT, create the input-clauses for each input and the output-clauses for each output
                # store all clauses in the corresponding 'internal_Xput_formulas' list
                # in createInternalInputFormula only internal_output_formulas of previous LUTs need to be used (already in the list)
                # in createInternalOutputFormular only internal_input_formulas of the same LUT need to be used (already in the list)
                #
                internal_input_formulas = []
                internal_output_formulas = []
                for lut in range(0, self.no_LUT):
                    for ins in range(0, self.LUT_inputs):
                        internal_input_formulas.append(self.__F_createLutInputFormula(index_LUT_inputs, inputs, internal_output_formulas, lut, ins))
                    for outs in range(0, self.LUT_outputs):
                        internal_output_formulas.append(self.__F_createLutOutputFormular(index_LUT_outputs, internal_input_formulas, lut, outs))
                #
                # for each global Output, calculate the expected value with calcOutput
                # create the final-output-clauses, set equal to the expected value and add to the solver
                #
                for g_out in range(0, self.no_outputs):
                    out = self.__calcOutput(inputs, g_out)
                    self.__sol.append(out == self.__F_createFinalOutputFormula(index_final_output, internal_output_formulas, g_out))
                    
            elif self.__exe_mode == 'ZV':
                #
                # for each LUT, create the input-clauses for each input and the output-clauses for each output
                # add all clauses directly to the solver
                #
                for lut in range(0, self.no_LUT):
                    for ins in range(0, self.LUT_inputs):
                        self.__sol.append(self.__ZV_createLutInputFormula(index_LUT_inputs, internal_inputs, internal_outputs, inputs, lut, ins, case))
                    for outs in range(0, self.LUT_outputs):
                        self.__sol.append(self.__ZV_createLutOutputFormula(index_LUT_outputs, internal_inputs, internal_outputs, lut, outs, case))

                #
                # for each global Output, calculate the expected value with calcOutput
                # create the final-output-clauses, set equal to the expected value and add to the solver
                #
                for g_out in range(0, self.no_outputs):
                    out = self.__calcOutput(inputs, g_out)
                    self.__sol.append(out == self.__ZV_createFinalOutputFormula(index_final_output, internal_outputs, g_out, case))
            else:
                logging.error("ERROR: unexpected execution mode")
                return 0

        #
        # Stop timer for the generation of the clauses and output it if not benchmark
        #
        end_generateClauses = time.perf_counter()    
        if not self.benchmark:
            logging.info("Clause Generation took:\t%s s", end_generateClauses - start_generateClauses)
        
        #
        # Run the Solver with the previous added clauses and time the duration of the execution (output if not benchmark)
        #
        start_solveClauses = time.perf_counter()
        self.__sol.check()
        end_solveClauses = time.perf_counter()
        if not self.benchmark:
            logging.info("Solving took:\t\t%s s", end_solveClauses - start_solveClauses)
            logging.info("Result is: %s", self.__sol.last_result)
        
        #
        # Print the found LUT configuration (if result == sat and not benchmark)
        #
        if not self.benchmark:
            if self.__sol.last_result == sat:
                if self.printConfig:
                    self.__printResultingLutConfiguration(self.__sol.model(), index_final_output, index_LUT_inputs, index_LUT_outputs)
                else:
                    logging.info("Printing of resulting Config is turned off")
            else:
                logging.info("No solution was found")
            logging.info("Result is: %s", self.__sol.last_result)
        
        #
        # Stop timer for the whole process and output program-name, total time, time for clause-generation and time of solving
        #
        end_process = time.perf_counter()
        logging.info("End Program %s - Gen: %s s - Solve: %s s - Total: %s s", os.path.basename(sys.argv[0]), end_generateClauses - start_generateClauses, end_solveClauses - start_solveClauses, end_process - start_process)
    def __runInc(self):
        #
        # Start timer and print parameters of the given problem (if not benchmark)
        #
        start_process = time.perf_counter()
        time1 = start_process
        if not self.benchmark:
            logging.info("Start Execution\tGlobal I / O: %s / %s\tLUTs / I / O: %s / %s / %s\tidx length: %s", self.no_inputs, self.no_outputs, self.no_LUT, self.LUT_inputs, self.LUT_outputs, self.input_index_length)

        #
        # Generate all indices that are independent of F and ZV
        #
        index_final_output = []
        for i in range(0, self.no_LUT * self.LUT_outputs * self.no_outputs):
            index_final_output.append(Bool('fOut' + str(i)))
        index_LUT_inputs = []
        for i in range(0, (self.no_LUT * self.LUT_inputs * self.input_index_length)):
            index_LUT_inputs.append(Bool('Linx' + str(i)))
        index_LUT_outputs = []
        for i in range(0, self.no_LUT * self.LUT_outputs * (2 ** self.LUT_inputs)):
            index_LUT_outputs.append(Bool('Loutx' + str(i)))
        #
        # Switch between F and ZV, generate the respective variables and output their sizes (if not benchmark)
        #
        if self.__exe_mode == 'F':
            if not self.benchmark:
                logging.info("generated xout[%s], xin[%s], xfinal[%s]", len(index_LUT_outputs), len(index_LUT_inputs), len(index_final_output))
        elif self.__exe_mode == 'ZV':
            internal_inputs = []
            for i in range(0, self.no_LUT * self.LUT_inputs * (2 ** self.no_inputs)):
                internal_inputs.append(Bool('IntIn' + str(i)))
            internal_outputs = []
            for i in range(0, self.no_LUT * self.LUT_outputs * (2 ** self.no_inputs)):
                internal_outputs.append(Bool('IntOut' + str(i)))
            if not self.benchmark:
                logging.info("generated xout[%s], xin[%s], xfinal[%s], intIn[%s], intOut[%s]", len(index_LUT_outputs), len(index_LUT_inputs), len(index_final_output), len(internal_inputs), len(internal_outputs))
        else:
            logging.error("ERROR: unexpected execution mode")
            return 0

        #
        # Instantiate Solver
        #
        self.__sol = Solver()
        
        #
        # Generate the constraints for the final outputs for each final output
        #
        for g_out in range(0, self.no_outputs):
            self.__sol.append(self.__createFinalOutputConstraints(index_final_output, g_out))
        
        #
        # Generate the constraints for the Inputs of the LUTs for each LUT
        #
        for lut in range(0, self.no_LUT):
            self.__sol.append(self.__createLutInputConstraints(index_LUT_inputs, lut))
        
        #
        # Generate Starting-Guesses
        #
        startingGuesses = self.__createStartingGuesses(self.no_LUT, self.LUT_inputs, self.LUT_outputs, self.no_inputs, self.no_outputs, self.input_index_length, index_final_output, index_LUT_inputs, index_LUT_outputs)
        for guess in startingGuesses:
            self.__sol.append(guess)

        #
        # Start Loop of generating LUT-clauses and running the solver
        #
        for case in range(0, 2 ** self.no_inputs):
            #
            # calculate the configuration of global inputs for each case
            #
            inputs = []
            for exp in range(self.no_inputs - 1, -1, -1):
                inputs.append((int)(case / (2 ** exp)) % 2)

            #
            # Switch between F and ZV
            #
            if self.__exe_mode == 'F':
                #
                # for each LUT, create the input-clauses for each input and the output-clauses for each output
                # store all clauses in the corresponding 'internal_Xput_formulas' list
                # in createInternalInputFormula only internal_output_formulas of previous LUTs need to be used (already in the list)
                # in createInternalOutputFormular only internal_input_formulas of the same LUT need to be used (already in the list)
                #
                internal_input_formulas = []
                internal_output_formulas = []
                for lut in range(0, self.no_LUT):
                    for ins in range(0, self.LUT_inputs):
                        internal_input_formulas.append(self.__F_createLutInputFormula(index_LUT_inputs, inputs, internal_output_formulas, lut, ins))
                    for outs in range(0, self.LUT_outputs):
                        internal_output_formulas.append(self.__F_createLutOutputFormular(index_LUT_outputs, internal_input_formulas, lut, outs))
                #
                # for each global Output, calculate the expected value with calcOutput
                # create the final-output-clauses, set equal to the expected value and add to the solver
                #
                for g_out in range(0, self.no_outputs):
                    out = self.__calcOutput(inputs, g_out)
                    self.__sol.append(out == self.__F_createFinalOutputFormula(index_final_output, internal_output_formulas, g_out))
                    
            elif self.__exe_mode == 'ZV':
                #
                # for each LUT, create the input-clauses for each input and the output-clauses for each output
                # add all clauses directly to the solver
                #
                for lut in range(0, self.no_LUT):
                    for ins in range(0, self.LUT_inputs):
                        self.__sol.append(self.__ZV_createLutInputFormula(index_LUT_inputs, internal_inputs, internal_outputs, inputs, lut, ins, case))
                    for outs in range(0, self.LUT_outputs):
                        self.__sol.append(self.__ZV_createLutOutputFormula(index_LUT_outputs, internal_inputs, internal_outputs, lut, outs, case))

                #
                # for each global Output, calculate the expected value with calcOutput
                # create the final-output-clauses, set equal to the expected value and add to the solver
                #
                for g_out in range(0, self.no_outputs):
                    out = self.__calcOutput(inputs, g_out)
                    self.__sol.append(out == self.__ZV_createFinalOutputFormula(index_final_output, internal_outputs, g_out, case))
            else:
                logging.error("ERROR: unexpected execution mode")
                return 0
            
            #
            # Run the Solver with the constraint-clauses and the clauses from previous case-loops
            # check the result of the solver. For UNSAT the execution can be stopped. For SAT a status is printed
            #
            self.__sol.check()
            if self.__sol.last_result == unsat:
                abort_process = time.perf_counter()    
                if not self.benchmark:
                    logging.info("Execution failed in step %s after %s s. No solution could be found", case, abort_process - start_process)
                break
            else:
                time2 = time.perf_counter()
                if not self.benchmark:
                    logging.info("[%s/%s]\tDelta: %s s", 2 ** self.no_inputs, case, time2 - time1)
                time1 = time2
            
        #
        # Print the found LUT configuration (if not benchmark)
        #
        if not self.benchmark:
            if self.__sol.last_result == sat:
                if self.printConfig:
                    self.__printResultingLutConfiguration(self.__sol.model(), index_final_output, index_LUT_inputs, index_LUT_outputs)
                else:
                    logging.info("Printing of resulting Config is turned off")
            else:
                logging.info("No solution was found")
            logging.info("Result is: %s", self.__sol.last_result)
        
        #
        # Stop timer for the whole process and output program-name, total time
        #
        end_process = time.perf_counter()
        logging.info("End Program %s with %s after %s s", os.path.basename(sys.argv[0]), self.__sol.last_result, end_process - start_process)
    def __runParallel(self):
        #
        # Start timer and print parameters of the given problem (if not benchmark)
        #
        start_main = time.perf_counter()
        deltaT = start_main
        if not self.benchmark:
            logging.info("Main: Start Execution")

        #
        # Setup empty lists that are needed to start the processes
        #
        coms = []
        steps = []
        procs = []
        for index in range(self.no_processes):
            #
            # Initialize shared variables for communication between Main and Processes
            #
            coms.append(multiprocessing.Value('i', 0))
            steps.append(multiprocessing.Value('i', 0))
            #
            # Initialize Processes with function and pass parameters and shared Values
            #
            procs.append(multiprocessing.Process(target=self.__parallelSolvingFunction,
                                                 args=(index, self.depth, self.no_processes, coms[index], steps[index])))
            #
            # Start Processes
            #
            procs[index].start()

        #
        # Start Main-Control-Loop that supervises the running processes
        # run the loop until running == False
        # inside the loop keep iterating though all processes and check the status of each one
        #
        running = True
        steps_mem = [0 for i in range(self.no_processes)]
        while running:
            stop = True
            for i in range(self.no_processes):
                #
                # If the com-value of a process == 1, this process has ended with a found solution SAT
                # in that case all processes are being terminated and running is stopped
                #
                if coms[i].value == 1:
                    if not self.benchmark:
                        logging.info("Main: P%s found a solution", i)
                    for index in range(self.no_processes):
                        procs[index].terminate()
                    if not self.benchmark:
                        logging.info("Main: all remaining processes have been terminated")
                    running = False
                    stop = False
                    break
                #
                # If the com-value of a process == 0, this process is still running and trying
                # to find a solution. Therefore the program needs to go on and the loop will
                # not be stopped in the next iteration: stop is set False
                #
                if coms[i].value == 0:
                    stop = False
                #
                # If the current step of a process does not fit to its last stored step, all
                # steps are updated and the current status is printed to the console
                #
                if steps_mem[i] != steps[i].value:
                    for k in range(0, self.no_processes):
                        steps_mem[k] = steps[k].value
                    current_main = time.perf_counter()
                    if not self.benchmark:
                        logging.info("Main: at %.8s: %s - %s D: %.8s", current_main - start_main, 2 ** self.no_inputs, steps_mem, current_main - deltaT)
                    deltaT = current_main
            #
            # stop is only True, if none of the processes are in com == 1 (SAT) or com == 0 (running)
            # Therefore all processes must be in com == -1, which means they terminated with UNSAT
            # In that case all processes are being terminated and running is stopped
            #
            if stop:
                if not self.benchmark:
                    logging.info("Main: all processes ended without a valid solution")
                for index in range(self.no_processes):
                    procs[index].terminate()
                if not self.benchmark:
                    logging.info("Main: all processes have been terminated")
                running = False
                break

        #
        # Wait until all Processes have ended and only then continue the program
        #
        for index in range(self.no_processes):
            procs[index].join()
        
        #
        # Stop timer for the whole process and output program-name, total time, time for clause-generation and time of solving
        #
        end_main = time.perf_counter()
        logging.info("Main: End Program %s after %s s", os.path.basename(sys.argv[0]), end_main - start_main)

    def __parallelSolvingFunction(self, idx, m_depth, m_no_processes, m_com, m_steps):
        #
        # Start timer and print parameters of the given problem (if not benchmark)
        #
        start_process = time.perf_counter()
        if not self.benchmark:
            logging.info("P%s: Start Process\tGlobal I / O: %s / %s\tLUTs / I / O: %s / %s / %s\tidx length: %s", idx, self.no_inputs, self.no_outputs, self.no_LUT, self.LUT_inputs, self.LUT_outputs, self.input_index_length)

        #
        # Generate all indices that are independent of F and ZV
        #
        index_final_output = []
        for i in range(0, self.no_LUT * self.LUT_outputs * self.no_outputs):
            index_final_output.append(Bool('fOut' + str(i)))
        index_LUT_inputs = []
        for i in range(0, (self.no_LUT * self.LUT_inputs * self.input_index_length)):
            index_LUT_inputs.append(Bool('Linx' + str(i)))
        index_LUT_outputs = []
        for i in range(0, self.no_LUT * self.LUT_outputs * (2 ** self.LUT_inputs)):
            index_LUT_outputs.append(Bool('Loutx' + str(i)))
        #
        # Switch between F and ZV, generate the respective variables and output their sizes (if not benchmark)
        #
        if self.__exe_mode == 'F':
            if not self.benchmark:
                logging.info("P%s: generated xout[%s], xin[%s], xfinal[%s]", idx, len(index_LUT_outputs), len(index_LUT_inputs), len(index_final_output))
        elif self.__exe_mode == 'ZV':
            internal_inputs = []
            for i in range(0, self.no_LUT * self.LUT_inputs * (2 ** self.no_inputs)):
                internal_inputs.append(Bool('IntIn' + str(i)))
            internal_outputs = []
            for i in range(0, self.no_LUT * self.LUT_outputs * (2 ** self.no_inputs)):
                internal_outputs.append(Bool('IntOut' + str(i)))
            if not self.benchmark:
                logging.info("P%s: generated xout[%s], xin[%s], xfinal[%s], intIn[%s], intOut[%s]", idx, len(index_LUT_outputs), len(index_LUT_inputs), len(index_final_output), len(internal_inputs), len(internal_outputs))
        else:
            logging.error("P%s: ERROR: unexpected execution mode", idx)
            return 0

        #
        # Instantiate Solver
        #
        sol = Solver()
        
        #
        # Generate the constraints for the final outputs for each final output
        #
        for g_out in range(0, self.no_outputs):
            sol.append(self.__createFinalOutputConstraints(index_final_output, g_out))
        
        #
        # Generate the constraints for the Inputs of the LUTs for each LUT
        #
        for lut in range(0, self.no_LUT):
            sol.append(self.__createLutInputConstraints(index_LUT_inputs, lut))
        
        #
        # Generate Starting-Guesses
        #
        startingGuesses = self.__createStartingGuesses(self.no_LUT, self.LUT_inputs, self.LUT_outputs, self.no_inputs, self.no_outputs, self.input_index_length, index_final_output, index_LUT_inputs, index_LUT_outputs)
        for guess in startingGuesses:
            sol.append(guess)

        #
        # Calculate a set of parameters, that are unique for each process
        # Generate Process-specific clauses from these parameters to divide the search space between them
        # full_depth_processes is the numer of processes that use all parameters
        # All other processes only use depth - 1 parameters
        #
        full_depth_processes = 2 * m_no_processes - (2 ** m_depth)
        param = []
        for i in range(m_depth):
            if idx >= full_depth_processes:
                if i != m_depth - 1:
                    param.append((int)((idx - full_depth_processes) / (2 ** (m_depth - i - 2))) % 2)
                    sol.append(bool((int)((idx - full_depth_processes) / (2 ** (m_depth - i - 2))) % 2) == index_LUT_outputs[i])
            else:
                param.append((int)(((2 ** m_depth) - idx - 1) / (2 ** (m_depth - i - 1))) % 2)
                sol.append(bool((int)(((2 ** m_depth) - idx - 1) / (2 ** (m_depth - i - 1))) % 2) == index_LUT_outputs[i])
        if not self.benchmark:
            logging.info("P%s: Parameters %s", idx, param)

        #
        # Start Loop of generating LUT-clauses and running the solver
        #
        for case in range(0, 2 ** self.no_inputs):
            #
            # calculate the configuration of global inputs for each case
            #
            inputs = []
            for exp in range(self.no_inputs - 1, -1, -1):
                inputs.append((int)(case / (2 ** exp)) % 2)

            #
            # Switch between F and ZV
            #
            if self.__exe_mode == 'F':
                #
                # for each LUT, create the input-clauses for each input and the output-clauses for each output
                # store all clauses in the corresponding 'internal_Xput_formulas' list
                # in createInternalInputFormula only internal_output_formulas of previous LUTs need to be used (already in the list)
                # in createInternalOutputFormular only internal_input_formulas of the same LUT need to be used (already in the list)
                #
                internal_input_formulas = []
                internal_output_formulas = []
                for lut in range(0, self.no_LUT):
                    for ins in range(0, self.LUT_inputs):
                        internal_input_formulas.append(self.__F_createLutInputFormula(index_LUT_inputs, inputs, internal_output_formulas, lut, ins))
                    for outs in range(0, self.LUT_outputs):
                        internal_output_formulas.append(self.__F_createLutOutputFormular(index_LUT_outputs, internal_input_formulas, lut, outs))
                #
                # for each global Output, calculate the expected value with calcOutput
                # create the final-output-clauses, set equal to the expected value and add to the solver
                #
                for g_out in range(0, self.no_outputs):
                    out = self.__calcOutput(inputs, g_out)
                    sol.append(out == self.__F_createFinalOutputFormula(index_final_output, internal_output_formulas, g_out))
                    
            elif self.__exe_mode == 'ZV':
                #
                # for each LUT, create the input-clauses for each input and the output-clauses for each output
                # add all clauses directly to the solver
                #
                for lut in range(0, self.no_LUT):
                    for ins in range(0, self.LUT_inputs):
                        sol.append(self.__ZV_createLutInputFormula(index_LUT_inputs, internal_inputs, internal_outputs, inputs, lut, ins, case))
                    for outs in range(0, self.LUT_outputs):
                        sol.append(self.__ZV_createLutOutputFormula(index_LUT_outputs, internal_inputs, internal_outputs, lut, outs, case))

                #
                # for each global Output, calculate the expected value with calcOutput
                # create the final-output-clauses, set equal to the expected value and add to the solver
                #
                for g_out in range(0, self.no_outputs):
                    out = self.__calcOutput(inputs, g_out)
                    sol.append(out == self.__ZV_createFinalOutputFormula(index_final_output, internal_outputs, g_out, case))
            else:
                logging.error("P%s: ERROR: unexpected execution mode", idx)
                return 0
            
            #
            # Update the current case of the process to communicate it to Main
            #
            m_steps.value = case
            
            #
            # Run the Solver with the constraint-clauses and the clauses from previous case-loops
            #
            sol.check()
            
            #
            # check the result of the solver
            # If UNSAT, the result is printed to the console and communicated to Main
            # The execution is stopped
            #
            if sol.last_result == unsat:
                abort_process = time.perf_counter()
                if not self.benchmark:
                    logging.info("P%s: [%s/%s]\tend with %s after %s s", idx, 2 ** self.no_inputs, case, sol.last_result, abort_process - start_process)
                    logging.info("P%s: Solving the problem with LUT-Output-Indices %s not possible", idx, param)
                    logging.info("P%s: set com Value to -1 and exit", idx)
                m_com.value = -1
                return False

        #
        # If SAT and not benchmark, print the found LUT configuration
        #
        if sol.last_result == sat and not self.benchmark:
            if self.printConfig:
                self.__printResultingLutConfiguration(sol.model(), index_final_output, index_LUT_inputs, index_LUT_outputs, idx)
            else:
                logging.info("P%s: Printing of resulting Config is turned off")
        #
        # Stop timer and output result and total time
        #
        end_process = time.perf_counter()
        logging.info("P%s: End Process with %s after %s s", idx, sol.last_result, end_process - start_process)
        #
        # Communicate the result to Main and stop the process
        #
        if sol.last_result == sat:
            logging.debug("P%s: set com Value to 1 and exit", idx)
            m_com.value = 1
        else:
            logging.debug("P%s: set com Value to -1 and exit", idx)
            m_com.value = -1
        return True

    def __createFinalOutputConstraints(self, m_idx_final_out, m_no_output):
        offset = self.no_LUT * self.LUT_outputs
        c = []
        temp = []
        c.append(Or(m_idx_final_out[offset * m_no_output : offset * (m_no_output + 1)]))
        for i in range(0, offset):
            for k in range(0, offset):
                if i != k and not [i, k] in temp and not [k, i] in temp:
                    temp.append([i, k])
                    c.append(True == Or(Not(m_idx_final_out[m_no_output * offset + i]),
                                        Not(m_idx_final_out[m_no_output * offset + k])))
        if len(c) > 1:
            return And(c)
        else:
            if len(c) < 1:
                c.append(True == m_idx_final_out[0])
            return c[0]
    def __createLutInputConstraints(self, m_idx_LUT_in, m_no_LUT):
        index_offset = m_no_LUT * self.LUT_inputs * self.input_index_length
        c = []
        for no_in in range(0, self.LUT_inputs):
            # At Least One of each LUT-Input
            c.append(Or(m_idx_LUT_in[index_offset + no_in * self.input_index_length
                                   : index_offset + (no_in + 1) * self.input_index_length]))
            temp = []
            for i in range(0, self.input_index_length):
                for k in range(0, self.input_index_length):
                    if i != k and not [i, k] in temp and not [k, i] in temp:
                        temp.append([i, k])
                        # At Most One of each LUT-Input
                        c.append(Or(Not(m_idx_LUT_in[index_offset + no_in * self.input_index_length + i]),
                                    Not(m_idx_LUT_in[index_offset + no_in * self.input_index_length + k])))
        for x in range(0, self.input_index_length):
            temp = []
            for i in range(0, self.LUT_inputs):
                for k in range(0, self.LUT_inputs):
                    if i != k and not [i, k] in temp and not [k, i] in temp:
                        temp.append([i, k])
                        # At Most One of each Signal in self.input_index_length
                        c.append(Or(Not(m_idx_LUT_in[index_offset + i * self.input_index_length + x]),
                                    Not(m_idx_LUT_in[index_offset + k * self.input_index_length + x])))
        return And(c)
    
    def __F_createLutInputFormula(self, m_idx_LUT_in, m_global_inputs, m_int_output_formulas, m_no_LUT, m_no_input):
        # I = Or((A and X1), (B and X2), ... , (O0 and Xi), ...)
        index_offset = m_no_LUT * self.LUT_inputs * self.input_index_length + m_no_input * self.input_index_length
        c = []
        for i in range(0, len(m_global_inputs)):
            c.append(And(bool(m_global_inputs[i]), m_idx_LUT_in[index_offset + i]))
        for i in range(0, m_no_LUT * self.LUT_outputs):
            c.append(And(m_int_output_formulas[i], m_idx_LUT_in[index_offset + len(m_global_inputs) + i]))
        return Or(c)
    def __F_createLutOutputFormular(self, m_idx_LUT_out, m_int_input_formulas, m_no_LUT, m_no_output):
        # O = Or((not_I0 and not_I1 and Ox0), (not_I0 and I1 and Ox1), ...)
        c = []
        for i in range(0, 2 ** self.LUT_inputs):
            m_temp_bool = []
            m_temp_in = []
            for j in range(self.LUT_inputs - 1, -1, -1):
                m_temp_bool.append((int)(i / (2 ** j)) % 2)
            for k in range(0, self.LUT_inputs):
                if bool(m_temp_bool[k]):
                    m_temp_in.append(m_int_input_formulas[m_no_LUT * self.LUT_inputs + k])
                else:
                    m_temp_in.append(Not(m_int_input_formulas[m_no_LUT * self.LUT_inputs + k]))
            m_temp_in.append(m_idx_LUT_out[m_no_LUT * self.LUT_outputs * (2 ** self.LUT_inputs) + m_no_output * (2 ** self.LUT_inputs) + i])
            c.append(And(m_temp_in))
        return Or(c)
    def __F_createFinalOutputFormula(self, m_idx_final_out, m_int_output_formulas, m_no_out):
        offset = self.no_LUT * self.LUT_outputs
        c = []
        for i in range(0, offset):
            c.append(And(m_int_output_formulas[i], m_idx_final_out[m_no_out * offset + i]))
        if len(c) > 1:
            return Or(c)
        else:
            return c[0]
    
    def __ZV_createLutInputFormula(self, m_idx_LUT_in, m_internal_in, m_internal_out, m_global_inputs, m_no_LUT, m_no_input, m_case):
        # I = Or((A and X1), (B and X2), (C and X3), ...)
        index_offset = m_no_LUT * self.LUT_inputs * self.input_index_length + m_no_input * self.input_index_length
        case_in_offset = m_case * self.no_LUT * self.LUT_inputs
        case_out_offset = m_case * self.no_LUT * self.LUT_outputs
        c = []
        for i in range(0, len(m_global_inputs)):
            c.append(And(bool(m_global_inputs[i]),
                         m_idx_LUT_in[index_offset + i]))
        for i in range(0, m_no_LUT * self.LUT_outputs):
            c.append(And(m_internal_out[case_out_offset + i],
                         m_idx_LUT_in[index_offset + len(m_global_inputs) + i]))
        return m_internal_in[case_in_offset + m_no_LUT * self.LUT_inputs + m_no_input] == Or(c)
    def __ZV_createLutOutputFormula(self, m_idx_LUT_out, m_internal_in, m_internal_out, m_no_LUT, m_no_output, m_case):
        # O0 = Or((not_I0 and not_I1 and Ox0), (not_I0 and I1 and Ox1), ...)
        case_in_offset = m_case * self.no_LUT * self.LUT_inputs
        case_out_offset = m_case * self.no_LUT * self.LUT_outputs
        c = []
        for i in range(0, 2 ** self.LUT_inputs):
            config = []
            c2 = []
            for j in range(0, self.LUT_inputs):
                config.append((int)(i / (2 ** (self.LUT_inputs - 1 - j))) % 2)
            for k in range(0, self.LUT_inputs):
                if bool(config[k]):
                    c2.append(m_internal_in[m_no_LUT * self.LUT_inputs + k + case_in_offset])
                else:
                    c2.append(Not(m_internal_in[m_no_LUT * self.LUT_inputs + k + case_in_offset]))
            c2.append(m_idx_LUT_out[m_no_LUT * self.LUT_outputs * (2 ** self.LUT_inputs)
                                  + m_no_output * (2 ** self.LUT_inputs) + i])
            c.append(And(c2))
        return m_internal_out[case_out_offset + m_no_LUT * self.LUT_outputs + m_no_output] == Or(c)
    def __ZV_createFinalOutputFormula(self, m_idx_final_out, m_internal_out, m_no_out, m_case):
        # fO0 = Or((O0 and Fx0), (O1 and Fx1), (O2 and Fx2), ...)
        output_offset = self.no_LUT * self.LUT_outputs
        case_out_offset = m_case * self.no_LUT * self.LUT_outputs
        c = []
        for i in range(0, output_offset):
            c.append(And(m_internal_out[case_out_offset + i],
                         m_idx_final_out[m_no_out * output_offset + i]))
        if len(c) > 1:
            return Or(c)
        else:
            return c[0]
    
    def __printResultingLutConfiguration(self, m, m_idx_final_out, m_idx_LUT_in, m_idx_LUT_out, m_process='-'):
        logging.info("P%s: Printing resulting LUT configuration", m_process)
        for lut in range(0, self.no_LUT):
            s_ins = ''
            for ins in range(0, self.LUT_inputs):
                for x in range(0, self.input_index_length):
                    if m[m_idx_LUT_in[lut * self.LUT_inputs * self.input_index_length + ins * self.input_index_length + x]]:
                        if x > self.no_inputs - 1:
                            if len(s_ins) > 0:
                                s_ins += ', '
                            s_ins += str(x - self.no_inputs)
                        else:
                            if len(s_ins) > 0:
                                s_ins += ', '
                            s_ins += str(chr(65 + x))
            logging.info("%s\t%s", m_process, s_ins)
            
            for case in range(0, 2 ** self.LUT_inputs):
                inputs = []
                outputs = []
                for exp in range(self.LUT_inputs - 1, -1, -1):
                    inputs.append((int)(case / (2 ** exp)) % 2)
                for outs in range(0, self.LUT_outputs):
                    outputs.append(m[m_idx_LUT_out[lut * self.LUT_outputs * (2 ** self.LUT_inputs) + outs * (2 ** self.LUT_inputs) + case]])
                logging.info("%s\t%s %s\t- %s", m_process, inputs, outputs, case)
                
            g_outputs = ''
            for lut_outs in range(0, self.LUT_outputs):
                used = False
                for g_outs in range(0, self.no_outputs):
                    if m[m_idx_final_out[g_outs * self.no_LUT * self.LUT_outputs + lut * self.LUT_outputs + lut_outs]]:
                        g_outputs += 'f: '
                        g_outputs += str(g_outs)
                        used = True
                if not used:
                    g_outputs += '---'
            logging.info("%s\t[%s]", m_process, g_outputs)

