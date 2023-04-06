.. _example VHDL:

VHDL
====

A set of fixtures are provided which uses `GHDL <http://ghdl.free.fr/>`_ as a free open source simulator for VHDL
and the `Xilinx Vivado <https://www.xilinx.com/products/design-tools/vivado.html>`_ design software for to synthesise
hardware designs written in VHDL  for Xilinx FPGA devices which the students can then test in the laboratory.
For the purpose of automatic marking we can test their designs using simulation testbenches
(which can be the same as those we give the students to get feedback as they work) and the synthesis step o generate A
binary ".bit" file that would the be used to program an FPGA device. I have found this to often be sufficient combined with
having seen the students work in the laboratory without having to program the devices myself for every students design. I have used this
both for intermediate digital desing courses using VHDL bu also for a digital systems hardware course where the students
explore the tradeoffs in a microprocessor design using VHDL.

Directory structure
-------------------

Below is the directory structure for these tests. Under the cohort directory we will have a directory for each student which will
contain their submitted designs in this case a VHDL entity and architecture for a trivial adder design based on a logic circuit in :file:`full_adder.vhd` 
and a constrainst file to map the ports onto hardware signals in file :file:`full_adder.xdc` 
- this is usually a first exercise I given the students to acclimitise them to using the software involved. They also design their
own test bench based on using a truth table for their full adder in file :file:`full_adder_testbench.vhd` which we also want to check.

In the tests folder we have the python unit test script :file:`test_full_adder.py`, our own testbench for the full adder :file:`full_adder_check.vhd` 
and two files to test the students testbench - one which implements a correct full adder :file:`full_adder_success` and one which has errors
:file:`full_adder_fail` to check that they detect a failed design::

    root
    ├─ cohorts
    │     ├─ cohort1
    │     │   └─ student1
    │     │   │  └─ full_adder.vhd
    │     │   │  └─ full_adder_testbench.vhd
    │     │   │  └─ full_adder.xdc
    |
    ├─ tests
    |     ├─ cohort1
    |     │   └─ test_full_adder.py
    |     │   └─ full_adder_check.vhd
    |     │   └─ full_adder_fail.vhd
    |     │   └─ full_adder_success.vhd



Example 1 - Testing simulation and synthesis
--------------------------------------------

In the first case we want to check that the students design pass a simulation and can be synthesised. They provide their implementation
to a given entity specification and an associate constraints (xdc) file. I normally specify that the constraints
file name must match that of the top level vhdl file and that these should match the entity name as a matter of good practice and the students
work will fail if they do not follow this practice. It also makes automated marking easier to have a strict specification.

.. code-block:: vhdl
    :caption: full_adder.vhd - sutdnets full adder implementation

    library ieee;
    use ieee.std_logic_1164.all;

    entity full_adder is
        port (
            x  : in  std_logic;
            y  : in  std_logic;
            cin : in  std_logic;
            s  : out std_logic;
            cout : out std_logic);
    end;

    architecture behavioral of full_adder is
    begin
    -- students implementation goes here
    end;

The constraints file will be a modified version of a template provided that has all of the pins on their 
development board listed but commented out - they just have to comment out the lines for the appropriate switches, buttons, LEDs etc and make sure they connect to the correctly named VHDL ports.

My testbench for  this is from the truth table - exactly the same as I expect the students to produce.

.. code-block:: vhdl
    :caption: full_adder_check.vhd - Turth table based test bench for full adder

    library ieee;
    use ieee.std_logic_1164.all;

    entity full_adder_check is
    end full_adder_check;

    architecture testbench of full_adder_check is
    component full_adder is
        port (
        x  : in  std_logic;
        y  : in  std_logic;
        cin : in  std_logic;
        s  : out std_logic;
        cout : out std_logic);
    end component;
    signal input  : std_logic_vector(2 downto 0);
    signal output : std_logic_vector(1 downto 0);
    begin
    uut: full_adder port map (
        x => input(0),
        y => input(1),
        cin => input(2),
        s => output(0),
        cout => output(1)
        );

    stim_proc: process
    begin
        input <= "000"; wait for 10 ns; assert output = "00" report "0+0+0 failed" ;
        -- Other 7 tests here
        wait;
    end process;
    end;

Below is the unit test file. Since I often want to test many different student entities I paramaterise the tests.
The first test is :func:`test_sim` which takes the students list of vhdl files that we need for the test
(just :file:`fill_adder.vhd` in this case) and our provided testbench entity name (which is also used as the file name) :file:`full_adder_check`. It calls the provided fixture :func:`pyam.fixtures.vhdl.vhdl_simulate` to analyse the student files,
together with our top level testbench, elaborate and run, throwing a :class:`pyam.fixtures.vhdl.VHDLSynthesisError` if the test failed.

The second test we have :func:`test_full_adder_bit_file_present` simply tests to see if the students have synthesised their own design
- a reminder to check notes from observations in the laboratory. The third test :func:`test_synthesis` is also paramaterised as I may want to fdo this for several designs in a submission. It again takes the name of the top level entity (which also forms the name of the constraints file) and a full list of VHDL files needed. It calls the provided fixture :func:`pyam.fixtures.vhdl.vhdl_synthesise` which will return if the synthesis has completed and a bit file produced, otherwise raising an error.

.. code-block:: python
    :caption: test_full_adder.py  fragment

    @pytest.mark.parametrize(
        "student_files,check",
        ((["full_adder.vhd"], "full_adder_check")))
    def test_sim(check, student_files, vhdl_simulate):
        vhdl_simulate(check, student_files)

    def test_full_adder_bit_file_present(student):
        assert (student.path/"full_adder.bit").exists()

    @pytest.mark.slow
    @pytest.mark.parametrize("top, files",
                            (("full_adder", ("full_adder.vhd")),))
    def test_synthesis(top, files, vhdl_synthesise):
        vhdl_synthesise(top, files)

Example 2 - Testing student test benches
----------------------------------------

Testing student test benches is a little more complex as we usually want to check if they detect both success (correct)
designs and failure (incorrect) designs. To accomplish this we provide a correct and incorrect design in our tests folder -  :file:`full_adder_success.vhd` and :file:`full_adder_fail.vhd`. Below is the test function :func:`test_full_adder_testbench` for this case.
It makes use of the :func:`pyam.fixtures.vhdl.vhdl_simulate` fixture as before to test success. 

To detect test bench failure we use the lower level :func:`pyam.fixtures.vhdl.ghdl` fixture provided to analyse our files and then run them, expecting a :class:`pyam.fixtures.vhdl.VHDLRunError` indicating that the testbench has successfully produced an error. It is necessary to reanalyse the fles at this point as we are using a different file with the incorrect version of the top level entity in the test. In tis case we disable standard output capture (capsys) for the duration of the simulation as we don't need it's error output for the student (it is expected).

.. code-block:: python
    :caption: test_full_adder.py fragment for testing testbenches
  
    def test_full_adder_testbench(vhdl_simulate,capsys,ghdl, test_path, student):
        #Expect student testbench to succeed for full_adder_successs provided
        vhdl_simulate("full_adder_testbench", ["full_adder_testbench.vhd"],
                    ["full_adder_success.vhd"])
        #Expect student testbench to fail for full_adder_fail provided
        with capsys.disabled():
            ghdl("-a", test_path / "full_adder_fail.vhd")
            ghdl("-a", student.path / "full_adder_testbench.vhd")
            with pytest.raises(VHDLRunError):
                ghdl("--elab-run", "full_adder_testbench", run_options=["--assert-level=error"])


Example 3 - Testing simulation and synthesis with VHDL only (without Python fixtures)
-------------------------------------------------------------------------------------

Directory structure
...................

Below is the directory structure for these tests. Under the cohort directory we will have a directory for each student which will
contain their submitted code - in this case :file:`entity1.vhd` and :file:`entity2.vhd`. In our tests folder for the cohort we have the VHDL test bench files :file:`test_entity1.vhd`, :file:`test_entity2.vhd` etc. The
test  files must start with "test\_" and must contain some comments to be recognised as test files::

    root
    ├─ cohorts
    │     ├─ cohort1
    │     │   └─ student1
    │     │   │  └─ entity1.vhd
    │     │   │  └─ entity2.vhd
    |
    ├─ tests
    │     └─ test_entity1.vhd
    │     └─ test_entity2.vhd

The VHDL fixtures provided by pyAutoMark will set up the analysis to point to the appropriate test folder and student folder. It is assumed that the entity specification and architecture under test are both defined in the same students file.

To be collected the VHDL test filenames must start with "test\_" and contain
the following definition

:PYAM_TEST: A unix glob string used to find the students file (by name) under test.

Additional parameters may be specified

:PYAM_TIMEOUT: (Optional) A floating point value spcifying the timeout for these tests.

:PYAM_TEST_VALUE: (Optional) This may be specified multiple times to enable multiple test
  using the same testbench file. For each value given the simulaition will be called
  with a generic parameter "PYAM_TEST_VALUE" set to the corresponding value.

e.g.

.. code-block:: VHDL

    -- PYAM_TEST "UUT.vhdl"
    -- PYAM_TIMEOUT TIMEOUT
    -- PYAM_TEST_VALUE VALUE1
    -- PYAM_TEST_VALUE VALUE2

.. option:: UUT.vhdl

    The filename glob to the entity and architecture definition file under test in the students directory 

.. option:: TIMEOUT

    The maximum run time for a test in seconds.

.. option:: VALUE1, VALUE2

    This is the list of test values which will be passed as "PYAM_TEST_VALUE generic values to the simulation in turn


