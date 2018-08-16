import os
import re
import yaml

from flask import current_app
from markdown.extensions.toc import TocExtension
from markdown.extensions.wikilinks import WikiLinkExtension


def config_path():
    return os.path.join(current_app.root_path, 'config.yml')


def config(key=None):
    try:
        with open(config_path(), 'r') as f:
            data = yaml.load(f)
    except IOError:
        print('no config in {}'.format(config_path))
    else:
        if key is None:
            return data
        return data.get(key, None)


def md_extensions():
    extensions = []

    base_url = config('note')['base_url']
    extensions.append(
        WikiLinkExtension(base_url='/{}/'.format(base_url)))
    extensions.append('markdown.extensions.fenced_code')
    extensions.append('markdown.extensions.codehilite')
    extensions.append('markdown.extensions.tables')
    extensions.append('markdown.extensions.admonition')

    ext_config = config('markdown_extensions')
    if ext_config['nl2br']:
        extensions.append('markdown.extensions.nl2br')
    if ext_config['toc']:
        extensions.append(TocExtension(
            marker='[목차]', permalink=True, slugify=_slugify))
    if ext_config['footnotes']:
        extensions.append('markdown.extensions.footnotes')
    
    return extensions


def _slugify(value, _):
    """
    기본 slugify는 한글을 날려먹는 문제가 있어 새로 만든다.
    """
    value = re.sub(r'[^가-힣\w\s-]', '', value.strip().lower())
    # value = re.sub(r'[\s]', separator, value)
    return value
