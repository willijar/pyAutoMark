Embedded C using the C mock fixtures
====================================


We often want to mark students embedded C designs without having to execute the code on hardware. For this we use mock
headers and C functions.
In this example I show how we can create a C mock to test their code on the host computer rather than 
on the embedded system. I have two examples, using embedded AVR C, which are typical of the kinds
of tasks students are given when they start out on their embedded programming journey.

.. highlight:: c

Directory structure
-------------------

Below is the directory structure for these tests. Under the cohort directory we will have a directory for each student which will
contain their submitted code - in this case :file:`Q1.c` and :file:`Q2.c`. In our tests folder for the cohort we
will need the pytest unittest files e.g. :file:`test1_Q1.py`, helper C test files e.g. :file:`Q1_test.c` and replacement
header files which the student code will include. These need to me in the appropriate directory structure to match the expected_value
system headers so for these simple cases we only have :file:`util/delay.y` and :file:`avr/io.h`.

| root
| ├─ cohorts
| │     ├─ cohort1
| │     │   └─ student1
| │     │   │  └─ Q1.c
| │     │   │  └─ Q2.c
| └─ tests
| │     ├─ cohort1
| │     │   └─ util
| │     │   │  └─ delay.h
| │     │   └─ avr
| │     │   │  └─ io.h
| │     │   └─ Q1_test.c
| │     │   └─ Q2_test.c
| │     │   └─ test_Q1.py
| │     │   └─ test_Q2.py

The cmock fixtures provided by pyAutoMark will set up the compilation include directories to point to the appropriate test folder
and student folder and add in the necessary compilation units.


Example 1 - Replacing function calls
-------------------------------------

Below is a typical example of a "first" embedded program - the students have to include the
correct header files, setup some defines and then have a main program which is an infinite loop that
sets and reads some registers to do stuff (using the defines from the header files). In this case it has a call
to the :code:`_delay_ms` function to slow down operation  so the student cans see the LEDS or whatever flashing.

.. code-block:: c
    :caption: Q1.c - A student AVR Embedded C Program Q1

    // Include relevant libraries
    #include <avr/io.h>
    #include <util/delay.h>

    // Define stuff

    int main(void)
    {
        // Define PortC pins as outputs
        DDRC = LEDs_Out;
        while (1) 
        {
            PORTC = Digits[Count];
            // do stuff
            _delay_ms(400);
            // fo stuff
        }
    }


For testing we will replace the headers with our own mock versions
to define the necessary constants, and we will replace the registers with external variables
of the appropriate type which we can then read or write in our code to test the students
funcitonality.

.. code-block:: c
    :caption: delay.h - mock replacement delay header

    #ifndef __DELAY_H_
    #define __DELAY_H_
    void _delay_ms(double __ms);
    void _delay_us(double __us);
    #endif

.. code-block:: c
    :caption: Mock io.h - replacement io header

    // Constant defines can be copied from real io.header e.g.
    #define PD2 2

    // Replace register defines with external variables
    extern uint8_t DDRC;
    extern uint8_t PORTC;

The next step is to write our C code which will actually test the students work. At the top of this we
we include the file :file:`student.h`. This file is created by the provided fixtures to include the actual students C file
under test. For each test that we want to perform this code will be compiled and and then executed with a different define set
(using the -d argument to the compiler). We therefore use :code:`#ifdef` or :code:`#ifdefined` blocks in the C program
to select which test we want to carry out. In the example below we have two. :code:`TEST_DELAY_HEADER` is used to include the
check that  the students have included the delay header and if not we create a compile time error. 

We then include our mock headers (in case the student hasn't) and define the external variables that we want to read and write to
in our tests - the replacement for the embedded system registers.

Since the student code calls the function :code:`_delay_ms` everytime the go round the :code:`while` loop most of our tests
are in there. I will typically use a global count variable that increases every time our mock function is called to provide state.
On iteration 0 we can put in all of the register intialisation checks we want to assess the studdents against - and we can check, say ,
that a particular register is changing over time, or that it changes when we set anoter variable/register to simulate an input. In the 
example provided we check if :code:`F_CPU` ise set correctly as the :code:`TEST_DELAY_HEADER` test, 
and if :code:`PORTC` is set correctly to soem expected value as the :code:`TEST_DIGITS` test.

.. code-block:: c
    :caption: Q1_test.c -- the C test file

    #include <student.h> // this header file will include actual student C file
    #if defined(TEST_DELAY_HEADER) && !defined(__DELAY_H_)
    #error "delay.h header not included"
    #endif
    #include <avr/io.h>
    #include <util/delay.h>

    // Define variables corresponding to registers
    uint8_t PORTC=0;

    int count=0; // global variable to give state

    // Write replacement function to check state
    void _delay_ms(double delay)
    {
        if (count==0) 
        {
            // Tests that only need checked once e.g.
            #if TEST_F_CPU
            if (F_CPU!= 20E6) {
                printf("F_CPU not set to 20E6");
                exit(1);
            }
            #endif
        }
        // other tests
        #if TEST_DIGITS
        if (PORTC!= expected_value) { 
            printf("Counted 0d%d digit incorrect - expected 0h%x but got 0h%x",count,expected_value,PORTC);
            exit(1);
        }
        #endif
    }

The final component it to provide the pytest file that pulls all this together. I typically will use a single
python file for every student task. In that we have to provide two fixtures. :code:`student_c_file` which returns the path to
the student c file under test, and the :code:`mock_c_file` which is our test C file. I then have a parametrized test
:code:`test_code` which will be run with the provided definitions, and, since we often check style, I have a :code:`test_style`
test function that runs c_lint on the student file with a particular threshold of warning that constitute a failure for this test.
The fixture :code:`c_lint_checks` sets which style checks are carried out - I don't recommend setting them all at this early stage.

.. code-block:: python
    :caption: test_Q1.py - the pytest Python file for this task.

    @pytest.fixture
    def student_c_file(student):
        "Path to students C file under test"
        # TODO: modify to use regex to match and find file rather than fixed filename
        return student.path/"Q1a.c"

    @pytest.fixture
    def mock_c_file(test_path):
        "Path to the Mock test C file to use"
        return test_path/"Q1_test.c"

    @pytest.mark.parametrize("declaration", 
                         ("TEST_F_CPU", "TEST_DELAY_HEADER", "TEST_DDRC",
                          "TEST_TIME_DELAY", "TEST_DIGIT0", "TEST_DIGITS"))
    def test_code(declaration,c_exec):
        assert c_exec([declaration]),declaration

    @pytest.fixture
    def c_lint_checks():
        return "performance-*,readability-*,portability-*"

    def test_style(student_c_file,c_lint):
        c_lint(student_c_file,17)


Example 2 - No function calls - registers only
----------------------------------------------

In the previous example the student submission had function calls for which we could provide a mock
function to carry out our tests. However simple embedded programs may only address registers. 
Typically, however, the will use macros to address those registers (or at least they should) and so we can
exploit that to inject function calls into the student code that we can then use to test and set the register/variable state
for the students work. An example is given below which has one student written function that dets a register bit to start an
ADC conversion and then waits for a conversion finished bit to be set before returning the value in the ADC register.


.. code-block:: c
    :caption: Q2.c - an AVR EMbedded C Program with- no function calls
    
    // Include relevant libraries
    #include <avr/io.h>

    // Define Constants

    // Define Functions
    int ADC_Conversion()
    {
        // Reads value from ADC
        ADCSRA |= 1<<ADSC;
        while(ADCSRA & 1<<ADSC);
        return ADC;
    }

    int main(void)
    {
        int ADC_Result;	
        // Set Registers

        // ADC Initialisation
        ADMUX = 1<<REFS0 | Left_POT;
        ADCSRA = 1<<ADEN | 1<<ADPS2 | 1<<ADPS0;
        while (1)
        {
            
            ADC_Result = ADC_Conversion();
            // Do stuff depending on ADC_Result
        }
    }

As before we provide our own header files. However, we can exploit the "," operator syntax
in C to inject function calls into the students code.
In the example below I have defined the :code:`ADCSRA` macro which is used
to represent a register as a call to
a function which we will use to test/set state be provided followed by the name of our external variable that we will use to
represent that register. Similarly for the :code:`ADC` register.

.. code-block:: c
    :caption: io.h replacing registers with function call and variable

    /// Constant defines can be copied from real io.header

    // Replace register defines with external variables

    // Where appropriate replace a register deine with a function call
    // and variable to inject function calls into student code e.g.

    extern uint8_t _ADCSRA ;
    extern int _ADC;
    void _F_ADCSRA();
    int _F_ADC();
    #define ADCSRA _F_ADCSRA(),  _ADCSRA
    #define ADC _F_ADC()

Then in our mock test :file:`Q2_test.c` file we can implement these function to carry out testing as needed. In this case 
we have :code:`_F_ADCSRA()` which models an ADC converstion, it sets the state variable :code:`state_requested` if the student has correctly
set the correct conversion bit and then after 9 calls sets the conversion finished bit - at which  point the students code will read the
:code:`ADC` register which we have also replaced. This calls the second function :code:`_F_ADC()` which
does the the necessary checks (using compiler defines to select which test as before). It can return different ADC values to the
student program and then on the next call check to see if the student has correctly responded in setting output registers etc.
The pytest test file for this will very similar to the first example, seting the student file and test C file
using fixtures, compiling and executing the code with different defines to run each test and possibly running a style check
on the students submitted code.

.. code-block:: c
    :caption: Q2_test.c our mock C implementation with the two functions

    int conversion_requested=0;
    // FUnction called everytime ADCSRA is referenced
    void _F_ADCSRA()
    {
        static int count=0;
        if (_ADCSRA & 1<<ADSC) {
            conversion_requested=1;
        }
        count++;
        if (count>1000) exit(0);
        if (count%9==1) {
            _ADCSRA &= ~(1<<ADSC);
        }

    }

    // Function called everytime ADC is referenced
    int _F_ADC() {
        static int count=0;
        if (count==0) // Initialisation tests tested on first read of ADC
        {
            #if TEST_DDRB
            assert_int("DDRB incorrect",  1<<PB3 | 1<< PB4, DDRB);
            #endif

            // .....
        }
        // ...
        #if TEST_ADSC_SET
        if (!conversion_requested) {
            printf("Conversion bit ADSC of ADCSRA not set");
            exit(1);
        }
        exit(0);
        #endif
    }



