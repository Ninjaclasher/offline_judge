import argparse
import math
import mmap
import os
import re
import resource
import signal
import sys
from enum import Enum
from operator import attrgetter

from .checkers import identical, floats, standard
from .ansi import ansi_style


class Verdict(Enum):
    AC = 0
    RTE = 1 << 0
    MLE = 1 << 1
    OLE = 1 << 2
    TLE = 1 << 3
    RE = 1 << 4
    WA = 1 << 5


VERDICT_COLOUR = {
    Verdict.AC: 'green',
    Verdict.RTE: 'yellow',
    Verdict.MLE: 'yellow',
    Verdict.OLE: 'yellow',
    Verdict.TLE: 'white',
    Verdict.RE: 'yellow',
    Verdict.WA: 'red',
}


MEMORY_UNIT = {
    'B': 2**0,
    'K': 2**10,
    'M': 2**20,
    'G': 2**30,
    'T': 2**40,
}


try:
    import ctypes
    import ctypes.util

    libc = ctypes.CDLL(ctypes.util.find_library('c'))
    strsignal_c = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_int)(('strsignal', libc), ((1,),))
    NSIG = signal.NSIG

    def strsignal(signo):
        if 0 <= signo < NSIG:
            s = strsignal_c(signo)
            if s:
                return s.decode('utf-8')
        return 'Unknown signal {}'.format(signo)
except:
    RTE_MSG = {
        4: 'Illegal instruction',
        6: 'Aborted',
        8: 'Floating point exception',
        11: 'Segmentation fault'
    }
    def strsignal(signo):
        if signo in RTE_MSG:
            return RTE_MSG[signo]
        return 'signal {}'.format(signo)


class Case:
    def __init__(self, case, verdict, time, memory, return_status):
        self.case = case
        self.verdict = verdict
        self.time = time
        self.memory = memory
        self.return_status = return_status


class OfflineJudge:
    def __init__(self, case_path, time_limit, memory_limit, executable, checker, *args, **kwargs):
        self.case_path = case_path
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.executable = executable
        self.check = checker

        self.args = args
        self.kwargs = {
            'no_ansi': False,
            'full_paths': False,
            'no_summary': False,
            'no_resource_usage': False,
            'include_verdicts': [],
            'exclude_verdicts': [],
        }
        self.kwargs.update(kwargs)

        self.cases = []

    def echo(self, text):
        print(text)

    def format_ansi(self, text):
        return ansi_style(text, self.kwargs['no_ansi'])

    def format_verdict(self, verdict):
        return self.format_ansi('#ansi[{}]({}|bold)'.format(verdict.name, VERDICT_COLOUR[verdict]))

    def format_memory(self, mem):
        return '{}p/{}M'.format(mem * 1024 // resource.getpagesize(), round(mem / 1024, 2))

    def format_resources(self, time, mem):
        return '{memory} {time}s'.format(memory=self.format_memory(mem), time=round(time, 4))

    def get_padding(self, depth):
        return '' if self.kwargs['full_paths'] else (' ' * 4 * depth) + ' '

    def get_filename(self, filename):
        return filename if self.kwargs['full_paths'] else os.path.basename(filename)

    def print_case(self, case, depth):
        verdict_name = case.verdict.name
        if verdict_name not in self.kwargs['include_verdicts'] or \
                verdict_name in self.kwargs['exclude_verdicts']:
            return

        usage_str = self.format_resources(case.time, case.memory)
        case_name_verdict = '{padding}{filename}: {verdict}'.format(padding=self.get_padding(depth),
                                                                    filename=self.get_filename(case.case),
                                                                    verdict=self.format_verdict(case.verdict))
        if self.kwargs['no_resource_usage']:
            self.echo(case_name_verdict)
        elif case.verdict in (Verdict.WA, Verdict.AC, Verdict.OLE):
            self.echo('{} {}'.format(case_name_verdict, usage_str))
        elif case.verdict == Verdict.TLE:
            self.echo('{} (>{}s) {}'.format(case_name_verdict, self.time_limit, self.format_memory(case.memory)))
        elif case.verdict == Verdict.RTE:
            signal = os.WTERMSIG(case.return_status)
            self.echo('{} ({}) {}'.format(case_name_verdict, strsignal(signal), usage_str))
        elif case.verdict == Verdict.RE:
            self.echo('{} ({}) {}'.format(case_name_verdict, os.WEXITSTATUS(case.return_status), usage_str))

    def judge_case(self, case, out_limit=None):
        file_i = case + '.in'
        file_o = case + '.out'
        if not os.path.isfile(file_i) or not os.path.isfile(file_o):
            return

        r, w = os.pipe()
        os.set_inheritable(w, True)
        os.set_inheritable(2, True)
        pid = os.fork()
        if pid == 0:
            stdin = os.open(file_i, os.O_RDONLY)
            if stdin != 0:
                os.dup2(stdin, 0)
                os.close(stdin)
            os.dup2(w, 1)
            resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit,)*2)
            resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(self.time_limit),)*2)
            os.execv(self.executable, [self.executable])
        submission = pid
        os.close(w)
        if out_limit is None:
            out_limit = os.stat(file_o).st_size * 4

        result = os.read(r, mmap.PAGESIZE)
        while len(result) < out_limit:
            buf = os.read(r, mmap.PAGESIZE)
            if len(buf) == 0:
                break
            result += buf

        os.kill(submission, signal.SIGKILL)
        os.close(r)
        _, return_status, rusage = os.wait4(submission, 0)
        # TODO: Other processes randomly sending signals can break this
        if len(result) > out_limit:
            verdict = Verdict.OLE
        elif (os.WIFSIGNALED(return_status) and
              os.WTERMSIG(return_status) == signal.SIGKILL or rusage.ru_utime > self.time_limit):
            verdict = Verdict.TLE
        elif os.WIFSIGNALED(return_status):
            verdict = Verdict.RTE
        elif os.WEXITSTATUS(return_status) != 0:
            verdict = Verdict.RE
        else:
            with open(file_o, 'rb') as out:
                answer = out.read()
            verdict = Verdict.AC if self.check(answer, result) else Verdict.WA
        return Case(case, verdict, rusage.ru_utime, rusage.ru_maxrss, return_status)

    def file_sort(self, text):
        convert = (lambda c: int(c) if c.isdigit() else c)
        return list(map(convert, re.split(r'(\d+)', text)))

    def recursive_judge(self, case, depth=-1):
        if os.path.isdir(case):
            if depth != -1:
                if not self.kwargs['full_paths']:
                    self.echo(self.format_ansi('#ansi[{padding}- {basename}](yellow|bold)'
                                                    .format(padding=self.get_padding(depth), basename=os.path.basename(case))))
            for filename in sorted(os.listdir(case), key=self.file_sort):
                self.recursive_judge(os.path.join(case, filename), depth+1)
        elif case.endswith('.in'):
            ret = self.judge_case(case.rstrip('.in'))
            self.print_case(ret, depth)
            self.cases.append(ret)

    def run(self):
        self.recursive_judge(self.case_path)

        num_ac = len(list(filter(lambda case: case.verdict == Verdict.AC, self.cases)))
        num_cases = len(self.cases)
        time_sum = sum(map(attrgetter('time'), self.cases))
        time_max = max(map(attrgetter('time'), self.cases))
        memory = max(map(attrgetter('memory'), self.cases))

        status_mask = 0
        for case in self.cases:
            status_mask |= case.verdict.value

        if not self.kwargs['no_summary']:
            self.echo('{ac}/{total} {verdict} {usage}/{max_time}s'
                            .format(ac=num_ac, total=num_cases,
                                    verdict=self.format_verdict(Verdict(status_mask & -status_mask)),
                                    usage=self.format_resources(time_sum, memory),
                                    max_time=round(time_max, 4)))

def main():
    verdicts = list(Verdict.__members__.keys())
    checkers = {
        'standard' : standard,
        'floats'   : floats,
        'identical': identical,
    }
    parser = argparse.ArgumentParser(description='An quick offline judging tool.')
    parser.add_argument('test_cases', help='Directory that contains the test cases, where the input is '
                                           'in a file ending with `.in` and the corresponding output in '
                                           'a file with the same name ending with `.out`.')
    parser.add_argument('time_limit', type=float, help='Time limit in seconds. Decimals are accepted. '
                                                       'Note that this limit can be bypassed by catching SIGXCPU.')
    parser.add_argument('memory_limit', help='Memory limit in one of "B", "K", "M", "G", "T". '
                                             'This must be one continuous string, for example "5M" is '
                                             'valid, however, "5 M" is not. Keep in mind that this has to '
                                             "be a multiple of the architecture's page size.")
    parser.add_argument('executable', help='The executable to run. It is executed through the execve system call. '
                                           'Therefore, scripts starting with "#!/bin/sh" will work, though it is '
                                           'a questionable language choice. Additional languages can be supported '
                                           'through helper scripts.')
    parser.add_argument('checker', default='standard', nargs='?', choices=checkers.keys(),
                            help='Checker to be used to compare the correct output '
                                 'and the executable output. (default: standard)')
    parser.add_argument('--no-ansi', action='store_const', default=0, const=1, help='Disable ANSI output.')
    parser.add_argument('--full-paths', action='store_const', default=0, const=1,
                            help='Use full case paths instead of batch headings and padding.')
    parser.add_argument('--no-summary', action='store_const', default=0, const=1,
                            help='Do not output the final summary.')
    parser.add_argument('--no-resource-usage', action='store_const', default=0, const=1,
                            help='Do not output time and memory usage.')
    parser.add_argument('--only-verdicts', nargs='+', help='Only display cases with the verdicts specified.',
                            default=verdicts, choices=verdicts)
    parser.add_argument('--exclude-verdicts', nargs='+', help='Do not display cases with the verdicts specified.',
                            default=[], choices=verdicts)
    args = parser.parse_args()

    case_path = args.test_cases
    time_limit = args.time_limit
    memory_limit = (int(args.memory_limit[:-1]) * MEMORY_UNIT[args.memory_limit[-1:]]) & -mmap.PAGESIZE
    executable = args.executable
    checker = checkers[args.checker]
    no_ansi = args.no_ansi
    full_paths = args.full_paths
    no_summary = args.no_summary
    no_resource_usage = args.no_resource_usage

    include_verdicts = args.only_verdicts
    exclude_verdicts = args.exclude_verdicts

    OfflineJudge(case_path, time_limit, memory_limit, executable, checker,
                 no_ansi=no_ansi, full_paths=full_paths, no_summary=no_summary, no_resource_usage=no_resource_usage,
                 include_verdicts=include_verdicts, exclude_verdicts=exclude_verdicts).run()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
