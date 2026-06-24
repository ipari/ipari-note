import importlib.util
import pathlib
import sys
import types
import unittest

import markdown


class ConfigStub:

    @classmethod
    def get(cls, column=None):
        return '[TOC]'


app_module = types.ModuleType('app')
config_module = types.ModuleType('app.config')
config_model_module = types.ModuleType('app.config.model')
config_model_module.Config = ConfigStub

sys.modules.setdefault('app', app_module)
sys.modules.setdefault('app.config', config_module)
sys.modules.setdefault('app.config.model', config_model_module)

ROOT_PATH = pathlib.Path(__file__).resolve().parents[1]
MARKDOWN_PATH = ROOT_PATH / 'app' / 'note' / 'markdown.py'
spec = importlib.util.spec_from_file_location('ipari_note_markdown', MARKDOWN_PATH)
markdown_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(markdown_module)


def render(markdown):
    md = markdown_lib.Markdown(extensions=markdown_module.md_extensions())
    return md.convert(markdown)


markdown_lib = markdown


class ObsidianMarkdownTest(unittest.TestCase):

    def test_wikilink_renders_note_link(self):
        html = render('[[folder/My Note]]')

        self.assertIn('href="/note/folder/My%20Note/"', html)
        self.assertIn('class="wikilink"', html)
        self.assertIn('>folder/My Note</a>', html)

    def test_wikilink_alias_renders_label(self):
        html = render('[[folder/My Note|read this]]')

        self.assertIn('href="/note/folder/My%20Note/"', html)
        self.assertIn('>read this</a>', html)

    def test_wikilink_heading_renders_fragment(self):
        html = render('[[folder/My Note#Section One|section]]')

        self.assertIn('href="/note/folder/My%20Note/#section one"', html)
        self.assertIn('>section</a>', html)

    def test_same_page_heading_renders_fragment_only(self):
        html = render('[[#Section One]]')

        self.assertIn('href="#section one"', html)
        self.assertIn('>Section One</a>', html)

    def test_image_embed_renders_image(self):
        html = render('![[attachments/photo 1.png]]')

        self.assertIn('<img', html)
        self.assertIn('src="attachments/photo%201.png"', html)
        self.assertIn('alt="attachments/photo 1.png"', html)


if __name__ == '__main__':
    unittest.main()
