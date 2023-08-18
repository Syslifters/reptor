import contextlib
import re
import typing

from django.template import base as django_base
from django.template.base import Token, TokenType
import django.template.loader_tags as django_loader_tags

HTML_PREFIX = "<!--"
HTML_SUFFIX = "-->"
HTML_REGEX = r"(<!--{%.*?%}-->|<!--{{.*?}}-->|<!--{#.*?#}-->)"


@contextlib.contextmanager
def django_tags(format: typing.Optional[str] = None):
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
                    len(django_base.BLOCK_TAG_START) : -len(django_base.BLOCK_TAG_START)
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
                    len(django_base.BLOCK_TAG_START) : -len(django_base.BLOCK_TAG_START)
                ].strip()
                if token_start == django_base.VARIABLE_TAG_START:
                    return Token(TokenType.VAR, content, position, lineno)
                # BLOCK_TAG_START was handled above.
                assert token_start == django_base.COMMENT_TAG_START
                return Token(TokenType.COMMENT, content, position, lineno)
        return Token(TokenType.TEXT, token_string, position, lineno)

    if format == "html":
        # HMTL comment tags
        tag_re = re.compile(HTML_REGEX)
        BLOCK_TAG_START = "<!--{%"
        BLOCK_TAG_END = "%}-->"
        VARIABLE_TAG_START = "<!--{{"
        VARIABLE_TAG_END = "}}-->"
        COMMENT_TAG_START = "<!--{#"
        COMMENT_TAG_END = "#}-->"
    else:
        # Original Django Tags
        tag_re = re.compile(r"({%.*?%}|{{.*?}}|{#.*?#})")
        BLOCK_TAG_START = "{%"
        BLOCK_TAG_END = "%}"
        VARIABLE_TAG_START = "{{"
        VARIABLE_TAG_END = "}}"
        COMMENT_TAG_START = "{#"
        COMMENT_TAG_END = "#}"

    # Save original values
    _tag_re = django_base.tag_re
    _create_token = django_base.Lexer.create_token
    _BLOCK_TAG_START = django_base.BLOCK_TAG_START
    _BLOCK_TAG_END = django_base.BLOCK_TAG_END
    _VARIABLE_TAG_START = django_base.VARIABLE_TAG_START
    _VARIABLE_TAG_END = django_base.VARIABLE_TAG_END
    _COMMENT_TAG_START = django_base.COMMENT_TAG_START
    _COMMENT_TAG_END = django_base.COMMENT_TAG_END

    # Monkey patch
    django_base.tag_re = tag_re
    django_base.Lexer.create_token = create_token
    django_base.BLOCK_TAG_START = BLOCK_TAG_START
    django_base.BLOCK_TAG_END = BLOCK_TAG_END
    django_base.VARIABLE_TAG_START = VARIABLE_TAG_START
    django_base.VARIABLE_TAG_END = VARIABLE_TAG_END
    django_base.COMMENT_TAG_START = COMMENT_TAG_START
    django_base.COMMENT_TAG_END = COMMENT_TAG_END

    yield

    # Restore original values
    django_base.tag_re = _tag_re
    django_base.Lexer.create_token = _create_token
    django_base.BLOCK_TAG_START = _BLOCK_TAG_START
    django_base.BLOCK_TAG_END = _BLOCK_TAG_END
    django_base.VARIABLE_TAG_START = _VARIABLE_TAG_START
    django_base.VARIABLE_TAG_END = _VARIABLE_TAG_END
    django_base.COMMENT_TAG_START = _COMMENT_TAG_START
    django_base.COMMENT_TAG_END = _COMMENT_TAG_END


# do_include should always use the original django tags without HTML prefix and suffix
do_include = django_tags()(django_loader_tags.do_include)
