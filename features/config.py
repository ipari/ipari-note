import os
import re
import yaml
from flask import current_app

from markdown.extensions.toc import TocExtension
from markdown.extensions.wikilinks import WikiLinkExtension, WikiLinks


def config(key=None):
    path = os.path.join(current_app.root_path, 'config.yml')
    try:
        with open(path, 'r') as f:
            data = yaml.load(f)
    except IOError:
        print('no config')
    else:
        if key is None:
            return data
        return data.get(key, None)


def md_extensions():
    extensions = []

    base_url = config('note')['base_url']
    extensions.append(
        WikiLinkExtensionCustom(base_url='/{}/'.format(base_url)))
    extensions.append('markdown.extensions.fenced_code')
    extensions.append('markdown.extensions.codehilite')
    extensions.append('markdown.extensions.tables')
    extensions.append('markdown.extensions.admonition')
    extensions.append('markdown.extensions.nl2br')
    extensions.append('markdown.extensions.footnotes')

    ext_config = config('markdown_extensions')
    toc_marker = ext_config['toc_marker']
    extensions.append(TocExtension(
        marker=toc_marker, permalink=True, slugify=_slugify))
    
    return extensions


def _slugify(value, _):
    """
    기본 slugify는 한글을 날려먹는 문제가 있어 새로 만든다.
    """
    value = re.sub(r'[^가-힣\w\s-]', '', value.strip().lower())
    # value = re.sub(r'[\s]', separator, value)
    return value


class WikiLinkExtensionCustom(WikiLinkExtension):
    """
    기본 WikiLinkExtension이 '/'가 있으면 링크로 인식하지 않는 문제를 해결.
    wikilink_re에 '/' 을 추가한다.
    """

    md = None

    def __init__(self, *args, **kwargs):
        super(WikiLinkExtensionCustom, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        self.md = md

        # append to end of inline patterns
        wikilink_re = r'\[\[([\w0-9_ -/]+)\]\]'
        wikilink_pattern = WikiLinks(wikilink_re, self.getConfigs())
        wikilink_pattern.md = md
        md.inlinePatterns.add('wikilink', wikilink_pattern, "<not_strong")
