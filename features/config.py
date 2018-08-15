import os
import yaml

from flask import current_app


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

    from markdown.extensions.wikilinks import WikiLinkExtension
    base_url = config('wiki')['base_url']
    extensions.append(
        WikiLinkExtension(base_url='/{}/'.format(base_url)))

    ext_config = config('markdown_extensions')
    if ext_config['nl2br']:
        extensions.append('markdown.extensions.nl2br')
    if ext_config['toc']:
        extensions.append('markdown.extensions.toc')
    if ext_config['footnotes']:
        extensions.append('markdown.extensions.footnotes')
    
    return extensions

