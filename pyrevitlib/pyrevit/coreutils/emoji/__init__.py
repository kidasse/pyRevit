import os.path as op
import re

from pyrevit.coreutils import prepare_html_str
from pyrevit.coreutils.emoji.code import emoji_file_dict

HTML_EMOJI_SPAN = prepare_html_str('<span"><img src="{}" style="vertical-align:middle;margin:-4,0,-4,0;"></span>')


def emojize(text):
    pattern = re.compile(':([a-z0-9+-_]+):')

    def emojifier(match):
        emoji_name = match.group(1)
        if emoji_name in emoji_file_dict:
            emoji_name = emoji_file_dict[emoji_name]

        return HTML_EMOJI_SPAN.format(op.join(op.dirname(__file__), 'png', '{}.png'.format(emoji_name)))

    return pattern.sub(emojifier, text)
