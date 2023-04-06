.. _example Python:

Python
======

Since pyAutoMark is written in Python testing students Python code is realtively straightforward. Typically you can reuse 
pytest unit tests which you give the students to get their own feedback as they work with little modification in pyAutoMark.
In these examples I will show the case where you want to test a students script, and a function in a module.

.. highlight:: python

Directory structure
-------------------

Below is the directory structure for these tests. Under the cohort directory we will have a directory for each student which will
contain their submitted code - in this case a script :file:`task1.py` and a module file :file:`cross_product.py` which will contain some
functions. In our tests folder for the cohort we
will need the pytest unittest files e.g. :file:`test_task1.py` and :file:`task_cross_product.py` that contain the tests for these student tasks.

| root
| ├─ cohorts
| │     ├─ cohort1
| │     │   └─ student1
| │     │   │  └─ task1.py
| │     │   │  └─ cross_product.py
| └─ tests
| │     ├─ cohort1
| │     │   └─ test_task1.py
| │     │   └─ test_cross_product.py


Example 1 - Testing a student script
------------------------------------

A typical first program for students is to write a script which takes input from the user and prints our some result.
Below is an example which inputs a day, month and year and does the day of week calculation from a formula given to the
students for the Georgian calendar.

.. code-block:: python
    :caption: task1.py - Day-of-Week Calculation

    month=int(input("Month:"))
    day=int(input("Day:"))
    year=int(input("Year:"))
    days=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    a=(14-month)//12
    y = year - a
    m=month+12*a -2
    d=(day + y + y//4 - y//100 + y//400 +31*m//12) % 7
    print(days[d])


Below is the unit test which generates some random inputs. It takes the :func:`pyam.fixtures.python.run_script` which is
a function that will run a script in the current students directory and pass the provided sequence of arguments to standard
input separated by newlines. It returns as a string the ouput from the script which we can then test as usual and
if it fails give an appropriate answer. This is probably over complicated as a unit test and simnply providing a couple of specific examples
would be better (particularly if giving it as a student unittest).

.. code-block:: python
    :caption: test_task1.py

    def test_task3(run_script):
        days=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
        days_in_month=[31,28,31,30,31,30,31,31,30,31,31,30,31]
        for i in range(10):
            year=random.randint(1900,2022)
            month=random.randint(1,12)
            day=random.randint(1,days_in_month[month])
            output=run_script("task1.py",(month,day,year))
            a=(14-month)//12
            y = year - a
            m=month+12*a - 2
            d=(day + y + y//4 - y//100 + y//400 +31*m//12) % 7
            assert output.endswith(days[d]), f"{output} is an incorrect answer for {day}/{month}/{year} - {days[d]} expected"




Example 2 - Testing student functions
-------------------------------------

As students develop we will want to have them usew write and test functions so for this second example
I will show how we test functions in student modules. THis example has the student write
a function :func:`gen_vec` to generate a vector of length 3 and then a function :func:`cross_product` to calculate
a 3x3 cross product of two vectors.

.. code-block:: python
    :caption: cross_product.py - students 3x3 cross_product and gen_vec functions
    
    import random
    def cross_product(x,y):
        if len(x)!=3 or len(y)!=3:
            raise ValueError
        return [x[1]*y[2]-x[2]*y[1],
                x[2]*y[0]-x[0]*y[2],
                x[0]*y[1]-x[1]*y[0]]

    def gen_vec():
        result=[]
        for i in range(3): result.append(random.randint(-1000,1000)/100)
        return result

A test file for that is given below. In this case we have to define a fixture :func:`module_name` which is the name
of the module/file in the students directory which we are going to test. This module is loaded by pyAutoMark and
made availabe to tests as :mod:`student_module`.

I have then created my own solutions to test the students work against and then the two test functions which
simply use the :mod:`student_module` to sccess the student functions and compare their results
with some expected results.

.. code-block:: python
    :caption: test_cross_product.py - test student gen_vec and cross_product functions

    @pytest.fixture
    def module_name(student):
        """Module name under test"""
        return "cross_product"

    def cross_product(x,y):
        return [x[1]*y[2]-x[2]*y[1],
                x[2]*y[0]-x[0]*y[2],
                x[0]*y[1]-x[1]*y[0]]

    def gen_vec():
        result=[]
        for i in range(3): result.append(random.randint(-1000,1000)/100)
        return result

    def test_cross_product(student_module):
        for test in range(10):
            x=gen_vec()
            y=gen_vec()
            assert student_module.cross_product(x,y) == pytest.approx(cross_product(x,y))

    def test_cross_product_exception(student_module):
        with pytest.raises(ValueError):
            student_module.cross_product([1,2,5,6],[3,4])

    def test_gen_vec_success(student_module):
        x=student_module.gen_vec()
        assert type(x) is list
        assert len(x)==3
        for v in x:
            assert type(v) is float
            assert round(v,2)==v,"Number not rounded to 2 decimal places"
        y=student_module.gen_vec()
        assert x != pytest.approx(y), "Same vector generate twice in a row"


