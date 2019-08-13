# Offline Judge
An offline equivalent of an online judge in Python. Unfortunately, it uses many Unix-exclusive features. This is in theory compatible with Unix-likes, however, it is only tested on Linux 4.12.3.

## Installation
```
$ pip install offline-judge
```

## Usage
```
$ judge --help
usage: judge [-h] [--no-ansi] [--full-paths] [--no-summary]
             [--no-resource-usage]
             [--only-verdicts {AC,RTE,MLE,OLE,TLE,RE,WA} [{AC,RTE,MLE,OLE,TLE,RE,WA} ...]]
             [--exclude-verdicts {AC,RTE,MLE,OLE,TLE,RE,WA} [{AC,RTE,MLE,OLE,TLE,RE,WA} ...]]
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
  --no-ansi             Disable ANSI output.
  --full-paths          Use full case paths instead of batch headings and
                        padding.
  --no-summary          Do not output the final summary.
  --no-resource-usage   Do not output time and memory usage.
  --only-verdicts {AC,RTE,MLE,OLE,TLE,RE,WA} [{AC,RTE,MLE,OLE,TLE,RE,WA} ...]
                        Only display cases with the verdicts specified.
  --exclude-verdicts {AC,RTE,MLE,OLE,TLE,RE,WA} [{AC,RTE,MLE,OLE,TLE,RE,WA} ...]
                        Do not display cases with the verdicts specified.
```
