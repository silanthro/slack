import re
from typing import Iterable

import mistletoe.block_token as b
import mistletoe.span_token as s
from mistletoe.markdown_renderer import Fragment, MarkdownRenderer


def _escape_text(text: str):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


url_regex = re.compile(
    r"""(?i)\b((?:https?://|www\d{0,3}[.]|ftp://)
    (?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+
    (?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""",
    re.VERBOSE,
)


def _encode_url(text: str):
    return re.sub(url_regex, lambda x: f"<{x.groups()[0]}>", text)


class MrkdwnRenderer(MarkdownRenderer):
    def __init__(self):
        super().__init__()

    def render_raw_text(self, token) -> Iterable[Fragment]:
        yield Fragment(_encode_url(_escape_text(token.content)), wordwrap=True)

    def render_strong(self, token: s.Strong) -> Iterable[Fragment]:
        return self.embed_span(Fragment("*"), token.children)

    def render_emphasis(self, token: s.Emphasis) -> Iterable[Fragment]:
        return self.embed_span(Fragment("_"), token.children)

    def render_strikethrough(self, token: s.Strikethrough) -> Iterable[Fragment]:
        return self.embed_span(Fragment("~"), token.children)

    def render_image(self, token: s.Image) -> Iterable[Fragment]:
        # yield Fragment("!")
        yield from self.render_link_or_image(token, token.src)

    def render_link_or_image(
        self, token: s.SpanToken, target: str
    ) -> Iterable[Fragment]:
        if not target:
            yield from self.embed_span(
                # Fragment("["),
                Fragment(""),
                token.children,
                # Fragment("]"),
                Fragment(""),
            )
            return

        yield Fragment("<")

        if token.dest_type == "uri" or token.dest_type == "angle_uri":
            # "[" description "](" dest_part [" " title] ")"
            # yield Fragment("(")
            dest_part = "<" + target + ">" if token.dest_type == "angle_uri" else target
            yield Fragment(dest_part)
            if token.title:
                yield from (
                    Fragment(" ", wordwrap=True),
                    Fragment(token.title_delimiter),
                    Fragment(token.title, wordwrap=True),
                    Fragment(
                        ")" if token.title_delimiter == "(" else token.title_delimiter,
                    ),
                )
            # yield Fragment(")")
        elif token.dest_type == "full":
            # "[" description "][" label "]"
            yield from (
                Fragment("["),
                Fragment(token.label, wordwrap=True),
                Fragment("]"),
            )
        elif token.dest_type == "collapsed":
            # "[" description "][]"
            yield Fragment("[]")
        else:
            # "[" description "]"
            pass

        yield Fragment("|")

        yield from self.embed_span(
            # Fragment("["),
            Fragment(""),
            token.children,
            # Fragment("]"),
            Fragment(""),
        )

        yield Fragment(">")

    def render_list_item(
        self, token: b.ListItem, max_line_length: int
    ) -> Iterable[str]:
        if self.normalize_whitespace:
            prepend = len(token.leader) + 1
            indentation = 0
        else:
            prepend = token.prepend
            indentation = token.indentation
        max_child_line_length = max_line_length - prepend if max_line_length else None
        lines = self.blocks_to_lines(
            token.children, max_line_length=max_child_line_length
        )
        leader = token.leader
        if leader in ["-", "*"]:
            leader = "•"
        return self.prefix_lines(
            list(lines) or [""],
            " " * indentation + leader + " " * (prepend - len(leader) - indentation),
            " " * prepend,
        )

    def render_heading(self, token: b.Heading, max_line_length: int) -> Iterable[str]:
        # note: no word wrapping, because atx headings always fit on a single line.
        line = "*" * token.level
        text = next(self.span_to_lines(token.children, max_line_length=None), "")
        if text:
            line += text
        if token.closing_sequence:
            line += token.closing_sequence
        line += "*"
        return [line]
