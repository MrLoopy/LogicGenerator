# LogicGenerator
Use cvc5 to calculate a generic LUT-structure that matches a logic-function that you predefined.
A detailed explanation of how this code is structured and works can be found in the Studienarbeit of Tobias Linker "Anwendung von SAT-Techniken zur Optimierung
von Logikfunktionen fur die Implementierung auf FPGAs" from 2024.

## Set up environment
To run the code, first you need to set up cvc5. Instructions on how to set it up can be found in the [Manual for setting up cvc5](Manual_for_setting_up_cvc5.md)

## How to use LogicGenerator
To get a better idea of how to use the LogicGenerator, you can have a look at the [demonstration-file](demo.py), the [benchmarks](LogicGenerator/benchmark/) or the [examples](LogicGenerator/examples/). <br />
In the [demonstration-file](demo.py) all the available parameters and functions of the LogicGenerator are presented. <br />
The [benchmarks](LogicGenerator/benchmark/) run the Mux-4 problem and the Conway-game-of-life problem in different modes and versions. <br />
The [examples](LogicGenerator/examples/) implement different logic functions, that can be calculated with the LogicGenerator.
