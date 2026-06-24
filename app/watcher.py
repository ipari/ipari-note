import os
import time
import traceback
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from app.config.model import CONFIG_PATH
from app.user.model import USER_PATH


MARKDOWN_EXT = '.md'
PAGE_PATH = os.path.join('data', 'pages')
DEFAULT_WATCHDOG_OBSERVER = 'native'
WATCHDOG_OBSERVER_MODES = ('native', 'polling')


class PageWatcher(object):

    event_order = ['created', 'modified', 'moved', 'deleted']

    def __init__(self):
        self.page_path = os.path.realpath(PAGE_PATH)
        self.user_path = os.path.realpath(USER_PATH)
        self.config_path = os.path.realpath(CONFIG_PATH)
        self.observer = create_observer()
        self.page_handler = EventHandler()
        self.user_handler = EventHandler()
        self.config_handler = EventHandler()

    def watch(self):
        self.observer.schedule(
            self.page_handler,
            self.page_path,
            recursive=True,
        )
        self.observer.schedule(self.user_handler, self.user_path)
        self.observer.schedule(self.config_handler, self.config_path)
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
        buffer = sorted(buffer, key=self.event_sort_key)
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

    def event_sort_key(self, event):
        try:
            return self.event_order.index(event.event_type)
        except ValueError:
            return len(self.event_order)

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

    def __init__(self):
        self.buffer = []

    def clear_buffer(self):
        self.buffer = []

    def on_any_event(self, event):
        if event.is_directory:
            return
        self.buffer.append(event)


def create_observer():
    mode = get_observer_mode()
    if mode == 'polling':
        return PollingObserver()
    return Observer()


def get_observer_mode():
    try:
        from config import WATCHDOG_OBSERVER
        mode = WATCHDOG_OBSERVER
    except ImportError:
        mode = DEFAULT_WATCHDOG_OBSERVER

    mode = str(mode).lower()
    if mode not in WATCHDOG_OBSERVER_MODES:
        return DEFAULT_WATCHDOG_OBSERVER
    return mode


if __name__ == '__main__':
    watcher = PageWatcher()
    watcher.watch()
