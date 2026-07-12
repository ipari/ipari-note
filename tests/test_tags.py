import importlib.util
import pathlib
import sys
import types
import unittest

from flask import Flask, url_for


def load_main_view_module():
    note_module = types.ModuleType('app.note.note')
    note_module.get_base_meta = lambda: {}
    note_module.get_menu_list = lambda: []
    note_module.get_posted_page = lambda page=1: ([], None, None)
    note_module.get_tag_page = lambda tag, page=1: ([], None, None)
    note_module.get_tag_list = lambda: []
    note_module.error_page = lambda page_path, message=None: ('', 404)
    note_module.update_all = lambda: None

    user_model_module = types.ModuleType('app.user.model')
    user_model_module.User = type(
        'User',
        (),
        {'is_logged_in': classmethod(lambda cls: False)},
    )

    sys.modules.setdefault('app', types.ModuleType('app'))
    sys.modules.setdefault('app.note', types.ModuleType('app.note'))
    sys.modules.setdefault('app.note.note', note_module)
    sys.modules.setdefault('app.user', types.ModuleType('app.user'))
    sys.modules.setdefault('app.user.model', user_model_module)

    root_path = pathlib.Path(__file__).resolve().parents[1]
    view_path = root_path / 'app' / 'main' / 'view.py'
    spec = importlib.util.spec_from_file_location('ipari_main_view', view_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TagRouteTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        main_view = load_main_view_module()
        cls.app = Flask(__name__)
        cls.app.register_blueprint(main_view.bp)

    def test_nested_tag_path_matches_as_single_tag(self):
        adapter = self.app.url_map.bind('example.test')

        endpoint, values = adapter.match('/tags/인물/가족')

        self.assertEqual(endpoint, 'main.view_tag')
        self.assertEqual(values, {'tag': '인물/가족'})

    def test_nested_tag_pagination_matches_tag_and_page(self):
        adapter = self.app.url_map.bind('example.test')

        endpoint, values = adapter.match('/tags/인물/가족/2')

        self.assertEqual(endpoint, 'main.view_tag_posts')
        self.assertEqual(values, {'tag': '인물/가족', 'page': 2})

    def test_nested_tag_url_generation(self):
        with self.app.test_request_context():
            url = url_for('main.view_tag', tag='인물/가족')

        self.assertEqual(url, '/tags/%EC%9D%B8%EB%AC%BC/%EA%B0%80%EC%A1%B1')


if __name__ == '__main__':
    unittest.main()
