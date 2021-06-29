import re
import xml.etree.ElementTree as etree
from markdown import util
from markdown.extensions import Extension
from markdown.extensions.toc import TocExtension
from markdown.extensions.wikilinks \
    import WikiLinkExtension, WikiLinksInlineProcessor
from markdown.inlinepatterns import InlineProcessor, LinkInlineProcessor
from app.config.model import Config


def md_extensions():
    extensions = []
    # https://python-markdown.github.io/extensions/
    extensions.append('markdown.extensions.meta')
    extensions.append('markdown.extensions.fenced_code')
    extensions.append('markdown.extensions.codehilite')
    extensions.append('markdown.extensions.tables')
    extensions.append('markdown.extensions.admonition')
    extensions.append('markdown.extensions.nl2br')
    extensions.append('markdown.extensions.footnotes')
    extensions.append('markdown.extensions.md_in_html')

    # FIXME: 수정해야함
    base_url = 'note'
    extensions.append(
        WikiLinkExtensionCustom(base_url='/{}/'.format(base_url)))

    toc_marker = Config.get('md_toc_marker')
    extensions.append(TocExtension(
        marker=toc_marker, permalink=True, slugify=_slugify))

    extensions.append(AutolinkExtensionCustom())
    extensions.append(LinkInlineExtension())

    return extensions


class WikiLinkExtensionCustom(WikiLinkExtension):
    """
    기본 WikiLinkExtension 은  '/'가 있으면 링크로 인식하지 않는다.
    wikilink_re에 '/' 을 추가하여 문제를 해결한다.
    """

    md = None

    def __init__(self, **kwargs):
        super(WikiLinkExtensionCustom, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        self.md = md

        # append to end of inline patterns
        wikilink_re = r'\[\[([\w0-9_ -/]+)\]\]'
        config = self.getConfigs()
        config['build_url'] = lambda label, base, end:  '{}{}{}'.format(base, label, end)
        wikilink_pattern = \
            WikiLinksInlineProcessor(wikilink_re, config)
        wikilink_pattern.md = md
        md.inlinePatterns.register(wikilink_pattern, 'wikilink', 75)


class AutolinkInlineProcessor(InlineProcessor):
    """ Return a link Element given an autolink (`http://example/com`). """
    def handleMatch(self, m, data):
        el = etree.Element('a')
        el.set('href', self.unescape(m.group(0)))
        el.set('target', '_blank')
        el.text = util.AtomicString(m.group(0))
        return el, m.start(0), m.end(0)


class AutolinkExtensionCustom(Extension):

    def extendMarkdown(self, md):
        html_re = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        md.inlinePatterns.deregister('autolink')
        md.inlinePatterns.register(
            AutolinkInlineProcessor(html_re, md), 'autolink', 120)


class LinkInlineProcessorCustom(LinkInlineProcessor):

    def __init__(self, pattern, md):
        super(LinkInlineProcessorCustom, self).__init__(pattern, md)

    def handleMatch(self, m, data):
        text, index, handled = self.getText(data, m.end(0))

        if not handled:
            return None, None, None

        href, title, index, handled = self.getLink(data, index)
        if not handled:
            return None, None, None

        el = etree.Element('a')
        el.text = text

        el.set('href', href)
        el.set('target', '_blank')

        if title is not None:
            el.set("title", title)

        return el, m.start(0), index


class LinkInlineExtension(Extension):

    def extendMarkdown(self, md):
        link_re = r'(?<!\!)\['
        md.inlinePatterns.deregister('link')
        md.inlinePatterns.register(
            LinkInlineProcessorCustom(link_re, md), 'link', 160)


def _slugify(value, _):
    """
    기본 slugify는 한글을 날려먹는 문제가 있어 새로 만든다.
    """
    value = re.sub(r'[^가-힣\w\s-]', '', value.strip().lower())
    return value
