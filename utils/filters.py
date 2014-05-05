# coding=utf8
"""
jinja2的过滤器
"""
import markdown


def md2html(md):
    """
    @param {unicode} md
    @return {unicode html}
    """
    return markdown.markdown(md, ['extra', 'codehilite', 'toc', 'nl2br'], safe_mode="escape")


JINJA2_FILTERS = {
    'md2html': md2html,
}
