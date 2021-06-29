import os
import time
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.config.model import CONFIG_PATH
from app.user.model import USER_PATH


MARKDOWN_EXT = '.md'
PAGE_PATH = os.path.join('data', 'pages')


class PageWatcher(object):

    event_order = ['created', 'modified', 'moved', 'deleted']

    def __init__(self):
        self.observer = Observer()
        self.page_handler = EventHandler()
        self.user_handler = EventHandler()
        self.config_handler = EventHandler()

    def watch(self):
        self.observer.schedule(
            self.page_handler,
            os.path.realpath(PAGE_PATH),
            recursive=True,
        )
        self.observer.schedule(self.user_handler, os.path.realpath(USER_PATH))
        self.observer.schedule(self.config_handler, os.path.realpath(CONFIG_PATH))
        self.observer.start()

        try:
            while True:
                time.sleep(1)
                self.handle_page_events()
                self.handle_user_events()
                self.handle_config_events()
        except Exception:
            self.observer.stop()
            traceback.print_exc()
            self.observer.join()

    def handle_page_events(self):
        if not self.page_handler.buffer:
            return
        buffer = self.page_handler.buffer
        buffer = list(set(buffer))
        # 파일 이동 시 새 경로에 생성을 먼저 하고 삭제 처리 하도록 한다.
        buffer = sorted(buffer, key=lambda x: self.event_order.index(x.key[0]))
        for event in buffer:
            _, ext = os.path.splitext(event.src_path)
            if ext != MARKDOWN_EXT:
                continue

            if event.event_type in ('modified', 'deleted'):
                from main import app
                from app.note.note import update_db

                with app.app_context():
                    update_db(event.src_path)

        self.page_handler.clear_buffer()

    def handle_user_events(self):
        if not self.user_handler.buffer:
            return
        from main import app
        from app.user.model import User
        with app.app_context():
            User.update_user()
        self.user_handler.clear_buffer()

    def handle_config_events(self):
        buffer = self.config_handler.buffer
        if not buffer:
            return
        from main import app
        from app.config.model import Config
        with app.app_context():
            Config.update_config()
        self.config_handler.clear_buffer()


class EventHandler(FileSystemEventHandler):

    buffer = []

    def clear_buffer(self):
        self.buffer = []

    def on_any_event(self, event):
        if event.is_directory:
            return
        self.buffer.append(event)


if __name__ == '__main__':
    watcher = PageWatcher()
    watcher.watch()
