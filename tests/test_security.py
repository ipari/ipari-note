import os
import sys
import tempfile
import unittest

for module_name in list(sys.modules):
    if module_name == 'app' or module_name.startswith('app.'):
        del sys.modules[module_name]

from app.note import note as note_module
from app.note.permission import Permission


class SecurityTest(unittest.TestCase):

    def setUp(self):
        self.original_root_path = note_module.ROOT_PATH
        self.original_user = note_module.User
        self.original_find_parent_note_for_file = (
            note_module.find_parent_note_for_file
        )
        self.tempdir = tempfile.TemporaryDirectory()
        note_module.ROOT_PATH = os.path.realpath(self.tempdir.name)

    def tearDown(self):
        note_module.ROOT_PATH = self.original_root_path
        note_module.User = self.original_user
        note_module.find_parent_note_for_file = (
            self.original_find_parent_note_for_file
        )
        self.tempdir.cleanup()

    def test_safe_page_path_allows_descendant(self):
        path = note_module.get_safe_page_path('folder', 'image.png')

        self.assertEqual(
            path,
            os.path.join(note_module.ROOT_PATH, 'folder', 'image.png'),
        )

    def test_safe_page_path_rejects_parent_traversal(self):
        path = note_module.get_safe_page_path('..', 'secret.yml')

        self.assertIsNone(path)

    def test_get_filepath_rejects_page_root(self):
        path = note_module.get_filepath('.', '.md')

        self.assertIsNone(path)

    def test_anonymous_file_without_parent_note_is_denied(self):
        note_module.User = type(
            'UserStub',
            (),
            {'is_logged_in': staticmethod(lambda: False)},
        )
        note_module.find_parent_note_for_file = lambda _: None

        self.assertFalse(note_module.can_serve_file('private/image.png'))

    def test_anonymous_file_uses_parent_note_permission(self):
        note_module.User = type(
            'UserStub',
            (),
            {'is_logged_in': staticmethod(lambda: False)},
        )
        parent_note = type('NoteStub', (), {'permission': Permission.PUBLIC})()
        note_module.find_parent_note_for_file = lambda _: parent_note

        self.assertTrue(note_module.can_serve_file('public/image.png'))

        parent_note.permission = Permission.PRIVATE

        self.assertFalse(note_module.can_serve_file('private/image.png'))


if __name__ == '__main__':
    unittest.main()
