def identical(judge_output, process_output):
    return judge_output == process_output

def floats(judge_output, process_output, precision=4):
    # Discount empty lines
    process_lines = process_output.decode('utf-8').strip().split('\n')
    judge_lines = judge_output.decode('utf-8').strip().split('\n')

    if len(process_lines) != len(judge_lines):
        return False

    epsilon = 10 ** -int(precision)

    try:
        for process_line, judge_line in zip(process_lines, judge_lines):

            process_tokens = process_line.strip().split()
            judge_tokens = judge_line.strip().split()

            if len(process_tokens) != len(judge_tokens):
                return False

            for process_token, judge_token in zip(process_tokens, judge_tokens):
                # Allow mixed tokens, for lines like "abc 0.68 def 0.70"
                try:
                    judge_float = float(judge_token)
                except:
                    # If it's not a float the token must match exactly
                    if process_token != judge_token:
                        return False
                else:
                    process_float = float(process_token)
                    # process_float can be nan
                    # in this case, we reject nan as a possible answer, even if judge_float is nan
                    if not abs(process_float - judge_float) <= epsilon and \
                            (not abs(judge_float) >= epsilon or not abs(1.0 - process_float / judge_float) <= epsilon):
                        return False
    except:
        return False
    return True

def iswhite(ch):
    return chr(ch) in [' ', '\t', '\v', '\f', '\n', '\r']

def isline(ch):
    return chr(ch) in ['\n', '\r']

def standard(judge, process):
    try:
        # Use a C subprogram instead python for speed increase
        from ._checker import standard as c_standard
        return c_standard(judge, process)
    except ImportError:
        j = 0
        p = 0
        jlen = len(judge)
        plen = len(process)
        while j < jlen and iswhite(judge[j]):
            j += 1
        while p < plen and iswhite(process[p]):
            p += 1
        while True:
            nj = False
            np = False
            while j < jlen and iswhite(judge[j]):
                nj |= isline(judge[j])
                j += 1
            while p < plen and iswhite(process[p]):
                np |= isline(process[p])
                p += 1
            if j == jlen or p == plen:
                return j == jlen and p == plen
            if nj != np:
                return False
            while j < jlen and not iswhite(judge[j]):
                if p >= plen:
                    return False
                if judge[j] != process[p]:
                    return False
                j += 1
                p += 1

