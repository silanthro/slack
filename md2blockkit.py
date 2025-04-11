import mistletoe
import mistletoe.block_token as b
import mistletoe.markdown_renderer
import mistletoe.span_token as s


def get_images_from_spans(spans: list[s.SpanToken]):
    images = []
    for span in spans:
        if isinstance(span, s.Image):
            images.append(
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": span.title or spans2text(span.children)[0] or " ",
                        "emoji": True,
                    },
                    "image_url": span.src,
                    "alt_text": span.title or spans2text(span.children)[0] or " ",
                }
            )
            if hasattr(span, "children") and span.children:
                images += get_images_from_spans(span.children)
    return images


def spans2text(spans: list[s.SpanToken]):
    rich_text_content = ""
    for span in spans:
        if isinstance(span, s.Image):
            continue
        else:
            if hasattr(span, "children") and span.children:
                children, _ = spans2text(span.children)
            else:
                children = span.content
            # Handle style
            if isinstance(span, s.Strong):
                children = f"*{children}*"
            elif isinstance(span, s.Emphasis):
                children = f"_{children}_"
            elif isinstance(span, s.InlineCode):
                children = f"`{children}`"
            elif isinstance(span, s.Strikethrough):
                children = f"~{children}~"
            # Handle links
            if isinstance(span, (s.AutoLink, s.Link)):
                children = f"<{span.target}|{children}>"
        rich_text_content += children
    return rich_text_content, get_images_from_spans(spans)


def spans2blocks(spans: list[s.SpanToken]):
    rich_text_blocks = []
    for span in spans:
        if isinstance(span, s.Image):
            continue
        else:
            if hasattr(span, "children") and span.children:
                children, _ = spans2blocks(span.children)
            else:
                children = [
                    {
                        "type": "text",
                        "text": span.content,
                    }
                ]
            # Handle style
            if isinstance(span, s.Strong):
                for c in children:
                    c["style"]["bold"] = True
            elif isinstance(span, s.Emphasis):
                for c in children:
                    c["style"]["italic"] = True
            elif isinstance(span, s.InlineCode):
                for c in children:
                    c["style"]["code"] = True
            elif isinstance(span, s.Strikethrough):
                for c in children:
                    c["style"]["strike"] = True
            # Handle links
            if isinstance(span, (s.AutoLink, s.Link)):
                for c in children:
                    c["type"] = "link"
                    c["url"] = span.target
        rich_text_blocks += children
    return rich_text_blocks, get_images_from_spans(spans)


def heading2blockkit(block: b.Heading):
    images = get_images_from_spans(block.children)
    blocks = []
    if block.level == 1:
        blocks.append(
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": block.content,
                    "emoji": True,
                },
            }
        )
    else:
        blocks.append(
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": block.content,
                                "style": {"bold": True},
                            },
                        ],
                    }
                ],
            }
        )
    return blocks + images


def quote2blockkit(block: b.Quote):
    text, images = spans2text(block.children)
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(f"> {s}" for s in text.split("\n")),
            },
        }
    ] + images


def paragraph2blockkit(block: b.Paragraph):
    text, images = spans2text(block.children)
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text,
            },
        }
    ] + images


def blockcode2blockkit(block: b.BlockCode):
    text, images = spans2text(block.children)
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{text}```",
            },
        }
    ] + images


def codefence2blockkit(block: b.CodeFence):
    text, images = spans2text(block.children)
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{text}```",
            },
        }
    ] + images


def listitem2blockkit(block: b.ListItem, style="bullet", indent=0):
    # First child is usually Paragraph
    # Subsequent child is usually List
    p_text, p_images = spans2blocks(block.children[0].children)
    data = {"rich_text": p_text}
    if len(block.children) > 1 and isinstance(block.children[1], b.List):
        data["children"] = p_images + list2blockkit(block.children[1])
    blocks = [
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_list",
                    "style": style,
                    "indent": indent,
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": p_text,
                        }
                    ],
                }
            ],
        }
    ]
    if len(block.children) > 1 and isinstance(block.children[1], b.List):
        blocks += p_images + list2blockkit(block.children[1], indent=indent + 1)
    return blocks


def list2blockkit(block: b.List, indent=0):
    items = []
    for child in block.children:
        items += listitem2blockkit(
            child,
            style="ordered" if block.start else "bullet",
            indent=indent,
        )
    return items


def table2blockkit(block: b.Table):
    # Block Kit does not support table
    renderer = mistletoe.markdown_renderer.MarkdownRenderer()
    result = ""
    for line in renderer.blocks_to_lines([block], max_line_length=10000):
        result += line + "\n"
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{result}```",
            },
        }
    ]


def break2blockkit(_: b.ThematicBreak):
    return [
        {
            "type": "divider",
        }
    ]


def html2blockkit(block: b.HtmlBlock):
    # Encode in code block
    return blockcode2blockkit(block)


def md2blockkit(md: str):
    doc = mistletoe.Document(md)
    blockkit_blocks = []
    for child in doc.children:
        if isinstance(child, b.Heading):
            blockkit_blocks += heading2blockkit(child)
        elif isinstance(child, b.Quote):
            blockkit_blocks += quote2blockkit(child)
        elif isinstance(child, b.Paragraph):
            blockkit_blocks += paragraph2blockkit(child)
        elif isinstance(child, b.CodeFence):
            blockkit_blocks += codefence2blockkit(child)
        elif isinstance(child, b.BlockCode):
            blockkit_blocks += blockcode2blockkit(child)
        elif isinstance(child, b.List):
            blockkit_blocks += list2blockkit(child)
        elif isinstance(child, b.Table):
            blockkit_blocks += table2blockkit(child)
        elif isinstance(child, b.ThematicBreak):
            blockkit_blocks += break2blockkit(child)
        elif isinstance(child, b.HtmlBlock):
            blockkit_blocks += html2blockkit(child)
    return blockkit_blocks
