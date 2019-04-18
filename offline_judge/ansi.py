import re

from termcolor import colored

def ansi_style(text, no_ansi):
    def format_inline(text, attrs):
        data = attrs.split('|')
        colors = data[0].split(',')
        if not colors[0]:
            colors[0] = None
        attrs = data[1].split(',') if len(data) > 1 else []
        return colored(text, *colors, attrs=attrs)

    return re.sub(r'#ansi\[(.*?)\]\((.*?)\)',
                  lambda x: format_inline(x.group(1), x.group(2)) if not no_ansi else x.group(1), text)
