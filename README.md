# Offline Judge
An offline equivalent of an online judge in Python. Unfortunately, it uses many Unix-exclusive features. This is in theory compatible with Unix-likes, however, it is only tested on Linux 4.12.3.

## Installation
First, clone the repository:
```
$ git clone https://github.com/Ninjaclasher/offline_judge
$ cd offline_judge
```

Install the prerequisites:
```
$ apt update
$ apt install python3 python3-pip
$ pip install -r requirements.txt
```

Allow `judge` to be executable:
```
$ chmod +x judge
```

## Optional Installation
For speed performance reasons, this script comes with a C checker, which is up to 5 times faster than the Python equivalent.

Install the prerequisites:
```
$ apt update
$ apt install gcc
```

To compile the C checker, run:
```
$ gcc -shared -o _checker.so -fPIC _checker.c
```

## Usage
```
$ judge --help
usage: judge [-h] [--no-ansi]
             test_cases time_limit memory_limit executable
             [{standard,floats,identical}]

An quick offline judging tool.

positional arguments:
  test_cases            Directory that contains the test cases, where the
                        input is in a file ending with `.in` and the
                        corresponding output in a file with the same name
                        ending with `.out`.
  time_limit            Time limit in seconds. Decimals are accepted. Note
                        that this limit can be bypassed by catching SIGXCPU.
  memory_limit          Memory limit in one of "B", "K", "M", "G", "T". This
                        must be one continuous string, for example "5M" is
                        valid, however, "5 M" is not. Keep in mind that this
                        has to be a multiple of the architecture's page size.
  executable            The executable to run. It is executed through the
                        execve system call. Therefore, scripts starting with
                        "#!/bin/sh" will work, though it is a questionable
                        language choice. Additional languages can be supported
                        through helper scripts.
  {standard,floats,identical}
                        Checker to be used to compare the correct output and
                        the executable output. (default: standard)

optional arguments:
  -h, --help            show this help message and exit
  --no-ansi             disable ANSI output
```

The judge outputs one line for every case, indicating the test case name/id, verdict and the memory/cpu usage. A final line is then appended, indicating the number of cases passed, the final verdict, the maximum memory usage on any test case, and the total/max time usage.

Note: The memory usage is given in this format: "256p/1M", where 256 is the number of memory pages used.
