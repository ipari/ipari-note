import markdown
import re
from markdown.extensions.toc import TocExtension
from markdown.extensions.wikilinks \
    import WikiLinkExtension, WikiLinksInlineProcessor
from app.config.config import get_config


def render_markdown(file_path):
    extensions = md_extensions()
    with open(file_path, 'r') as f:
        raw_md = f.read()
    return markdown.markdown(raw_md, extensions=extensions)


def md_extensions():
    extensions = []
    # https://python-markdown.github.io/extensions/
    base_url = get_config('note')['base_url']
    extensions.append(
        WikiLinkExtensionCustom(base_url='/{}/'.format(base_url)))
    extensions.append('markdown.extensions.fenced_code')
    extensions.append('markdown.extensions.codehilite')
    extensions.append('markdown.extensions.tables')
    extensions.append('markdown.extensions.admonition')
    extensions.append('markdown.extensions.nl2br')
    extensions.append('markdown.extensions.footnotes')
    extensions.append('markdown.extensions.md_in_html')

    ext_config = get_config('markdown_extensions')
    toc_marker = ext_config['toc_marker']
    extensions.append(TocExtension(
        marker=toc_marker, permalink=True, slugify=_slugify))

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
        wikilink_pattern = \
            WikiLinksInlineProcessor(wikilink_re, self.getConfigs())
        wikilink_pattern.md = md
        md.inlinePatterns.register(wikilink_pattern, 'wikilink', 75)


def _slugify(value, _):
    """
    기본 slugify는 한글을 날려먹는 문제가 있어 새로 만든다.
    """
    value = re.sub(r'[^가-힣\w\s-]', '', value.strip().lower())
    return value
