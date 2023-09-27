import re
import xml.etree.ElementTree as etree
from markdown import util
from markdown.extensions import Extension
from markdown.extensions.toc import TocExtension
from markdown.extensions.wikilinks \
    import WikiLinkExtension, WikiLinksInlineProcessor
from markdown.inlinepatterns import InlineProcessor, LinkInlineProcessor
from markdown.preprocessors import Preprocessor
from app.config.model import Config


def md_extensions():
    extensions = []
    # https://python-markdown.github.io/extensions/
    # extensions.append('markdown.extensions.meta')
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
    extensions.append(MetaExtension())

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


##############################################################################
# 메타 데이터에서 yaml list 포맷을 허용하도록
# 기본 메타 익스텐션은 공백 4칸으로 목록을 지정하는데 이것을 - 으로 시작하도록 수정한다.
##############################################################################

META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
META_MORE_RE = re.compile(r'^[ ]{2,}[-]{1}[ ]{1}(?P<value>.*)')
BEGIN_RE = re.compile(r'^-{3}(\s.*)?')
END_RE = re.compile(r'^(-{3}|\.{3})(\s.*)?')


class MetaExtension (Extension):
    """ Meta-Data extension for Python-Markdown. """

    def extendMarkdown(self, md):
        """ Add MetaPreprocessor to Markdown instance. """
        md.registerExtension(self)
        self.md = md
        md.preprocessors.register(MetaPreprocessor(md), 'meta', 27)

    def reset(self):
        self.md.Meta = {}


class MetaPreprocessor(Preprocessor):
    """ Get Meta-Data. """

    def run(self, lines):
        """ Parse Meta-Data and store in Markdown.Meta. """
        meta = {}
        key = None
        if lines and BEGIN_RE.match(lines[0]):
            lines.pop(0)
        while lines:
            line = lines.pop(0)
            m1 = META_RE.match(line)
            if line.strip() == '' or END_RE.match(line):
                break  # blank line or end of YAML header - done
            if m1:
                key = m1.group('key').lower().strip()
                value = m1.group('value').strip()

                # Obsidian 에서 태그가 비어있을 때 `[]` 을 넣는 것을 빈 문자를 넣도록 수정
                if key == 'tags':
                    value = ''

                try:
                    meta[key].append(value)
                except KeyError:
                    meta[key] = [value]
            else:
                m2 = META_MORE_RE.match(line)
                if m2 and key:
                    # Add another line to existing key
                    meta[key].append(m2.group('value').strip())
                else:
                    lines.insert(0, line)
                    break  # no meta data - done
        self.md.Meta = meta
        return lines


def _slugify(value, _):
    """
    기본 slugify는 한글을 날려먹는 문제가 있어 새로 만든다.
    """
    value = re.sub(r'[^가-힣\w\s-]', '', value.strip().lower())
    return value
