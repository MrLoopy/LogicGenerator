# Manual for setting up cvc5
The Python code can be written in any IDE. To run it, first cvc5 has to be installed with all its dependencies. How to set the python API of cvc5-1.1.1 up on Linux is
described below. Also, some tips and tricks are given if you want to set the environment up on a remote server, like Epic. For further help, if you want to set up an
other version of cvc5 or if you want to set it up on macOS or Windows, read [the documentation of cvc5](https://cvc5.github.io/docs/cvc5-1.1.1/installation/installation.html):

- The repository of cvc5 needs to be cloned on your local machine. This is needed to build and install it in the next steps. If you have git installed, you can clone the repository with:
```git clone https://github.com/cvc5/cvc5.git```
- You need to make sure that some required tools and libraries are installed on your machine or you have to install them yourself:
  - Python >= 3.6 and <= 3.10
  - GNU C and C++ (gcc and g++, >= 7) or Clang (>= 5)
  - CMake >= 3.9
  Some other packages can be installed with `pip install` if they are not already present:
  - tomli
  - pyparsing
  - Cython >= 3.0.0
  - scikit-build
  - pytest
  If you are working on Epic (or on a system were you do not have full admin rights), the scrips are not installed in `/usr/bin` because you usually do not have permission to
  that folder, but in your local directory `/shares/nct-home/<Uni_ID>/.local/bin`. This will be important later, because cvc5 will need this Path to find the libraries.
-  Next, in your bash-console navigate into the repository you cloned, into cvc5. Here you will soon run `./configure.sh` with specific flags that specify how cvc5 needs to be configured. The needed flags are:
  - The bindings for python need to be activated, so that the python API can be used. This is done by the flag:
    ```--python-bindings```
  - Libraries that are installed in a non-standard location need to be linked. The paths to these libraries (like `/shares/nct-home/<Uni\_ID>/.local/bin`) needs to be given with the flag:
    ```--dep-path=<dep_path>```
  - Since you have no access to `/usr/bin` and your installed libraries were installed in `.local/bin`, also cvc5 itself can not be installed to the default location `/usr/bin`. Therefore
    an alternative location to install cvc5 to needs to be given. This can be the same location as the other libraries are installed to `/shares/nct-home/<Uni_ID>/.local`. The path is given with the flag:
    ```--prefix=<install_path>```
  - Cvc5 needs even more dependencies to function. These are underlying tools that are used when solving different problems, like a SAT solver, arithmetic libraries and so on. These can be
    downloaded and installed automatically with the flag:
    ```--auto-download```
  The complete command therefor looks like this (your paths may differ):
  ```./configure.sh --auto-download --python-bindings --dep-path=/shares/nct-home/<Uni_ID>/.local/bin --prefix=/shares/nct-home/<Uni_ID>/.local```
  The libraries that are downloaded and build automatically should be put into `cvc5/build/deps`. The libs that should be dwonloaded are:
  - GMP, a GNU Multi-Precision arithmetic library.
  - CaDiCaL, the standard SAT solver for cvc5. Optionally, two other SAT solvers can be used. This needs to be done in the previous step by an additional flag for `./configure.sh`. The
    optional solvers that can also be downloaded automatically are CryptoMiniSat and Kissat. More information in the documentation of cvc5.
  - Poly, a polynomial library.
  - SymFPU, which adds support for the theory of floating point numbers.
- After the configuration is done without errors, next cvc5 can be build, tested and than installed. For this, navigate into the build directory `cvc5/build`. Then, run the command
  ```make```
  to build the project. This step can be time intensive and take some minutes.
- Next, run the command
  ```make check```
  This will run a default set of tests automatically.
- Next, run the command
  ```make install```
  This will finally install cvc5. A List of all installed files can be found in `cvc5/build/cvc5-installed-files.txt`
- After the successful installation, cvc5 can be tested with further tests. These can be run in `cvc5/build` with the command `ctest`.
  For even more tests, you can build and run API- and unit-tests. For this, see the cvc5 documentation.
Now that cvc5 is installed, you can start to use it. For a quick start, you can look at the examples in `cvc5/examples/api/python/pythonic` and run them. Best start with `quickstart.py` since
it goes through the basic logic of a small project. For more information on how to use the Pythonic API of cvc5, have a look at
the [the Pythonic API documentation](https://cvc5.github.io/docs-ci/docs-main/api/python/pythonic/pythonic.html) or at
the [overview and comparison of all examples in different languages](https://cvc5.github.io/docs-ci/docs-main/examples/examples.html).
