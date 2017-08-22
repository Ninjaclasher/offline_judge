# offline_judge
An offline equivalent of an online judge(dmoj.ca) in Python. Unfortunately, it uses many Unix-exclusive features. This is in theory compatible with Unix-likes, however, it is only tested on Linux 4.12.3.

## Usage
    ./judge test_case_dir/ cpu_limit mem_limit executable
`test_case_dir/` is a directory that contains the test cases, where the input is in a file ending with `.in`, and the corresponding output in a file with the same name ending with `.out`.

`cpu_limit` is the cpu time limit in seconds(decimals are accepted). Note that this limit can be bypassed by catching SIGXCPU.

`mem_limit` is the memory limit in units specified(valid units are "B","K","M","G"). This must be one continuous string, for example "5M" is valid, however, "5 M" is not. Keep in mind that this has to be a multiple of the architecture's page size.

`executable` is the executable of the submission. It is executed through the execve system call. Therefore, scripts starting with "#!/bin/sh" will work, though it is a questionable language choice. Additional languages can be supported through helper scripts.

The judge outputs one line for every case, indicating the test case name/id, verdict and the memory/cpu usage. A final line is then appended, indicating the number of cases passed, the final verdict, the maximum memory usage on any test case, and the total cpu usage.

Note: The memory usage is given in this format: "256p/1M", where 256 is the number of memory pages used.