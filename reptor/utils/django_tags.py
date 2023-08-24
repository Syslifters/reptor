import re

from django.template import base as django_base
from django.template.base import Token, TokenType

# HMTL comment tags
HTML_REGEX = re.compile(r"(<!--{%.*?%}-->|<!--{{.*?}}-->|<!--{#.*?#}-->)")
BLOCK_TAG_START = "<!--{%"
BLOCK_TAG_END = "%}-->"
VARIABLE_TAG_START = "<!--{{"
VARIABLE_TAG_END = "}}-->"
COMMENT_TAG_START = "<!--{#"
COMMENT_TAG_END = "#}-->"


def setup_django_tags():
    def create_token(self, token_string, position, lineno, in_tag):
        """
        Convert the given token string into a new Token object and return it.
        If in_tag is True, we are processing something that matched a tag,
        otherwise it should be treated as a literal string.
        """
        if in_tag:
            # The [0:2] and [2:-2] ranges below strip off *_TAG_START and
            # *_TAG_END. The 2's are hard-coded for performance. Using
            # len(BLOCK_TAG_START) would permit BLOCK_TAG_START to be
            # different, but it's not likely that the TAG_START values will
            # change anytime soon.
            token_start = token_string[0 : len(django_base.BLOCK_TAG_START)]
            if token_start == django_base.BLOCK_TAG_START:
                content = token_string[
                    len(django_base.BLOCK_TAG_START) : -len(django_base.BLOCK_TAG_END)
                ].strip()
                if self.verbatim:
                    # Then a verbatim block is being processed.
                    if content != self.verbatim:
                        return Token(TokenType.TEXT, token_string, position, lineno)
                    # Otherwise, the current verbatim block is ending.
                    self.verbatim = False
                elif content[:9] in ("verbatim", "verbatim "):
                    # Then a verbatim block is starting.
                    self.verbatim = "end%s" % content
                return Token(TokenType.BLOCK, content, position, lineno)
            if not self.verbatim:
                content = token_string[
                    len(django_base.BLOCK_TAG_START) : -len(django_base.BLOCK_TAG_END)
                ].strip()
                if token_start == django_base.VARIABLE_TAG_START:
                    return Token(TokenType.VAR, content, position, lineno)
                # BLOCK_TAG_START was handled above.
                assert token_start == django_base.COMMENT_TAG_START
                return Token(TokenType.COMMENT, content, position, lineno)
        return Token(TokenType.TEXT, token_string, position, lineno)

    # Monkey patch
    django_base.tag_re = HTML_REGEX
    django_base.Lexer.create_token = create_token
    django_base.BLOCK_TAG_START = BLOCK_TAG_START
    django_base.BLOCK_TAG_END = BLOCK_TAG_END
    django_base.VARIABLE_TAG_START = VARIABLE_TAG_START
    django_base.VARIABLE_TAG_END = VARIABLE_TAG_END
    django_base.COMMENT_TAG_START = COMMENT_TAG_START
    django_base.COMMENT_TAG_END = COMMENT_TAG_END
