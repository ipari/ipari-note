import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PageWatcher(object):

    event_order = ['created', 'modified', 'moved', 'deleted']

    def __init__(self):
        self.observer = Observer()
        self.event_handler = PageHandler()
        self.page_path = os.path.join('data', 'pages')

    def watch(self):
        self.observer.schedule(
            self.event_handler,
            os.path.realpath(self.page_path),
            recursive=True,
        )
        self.observer.start()

        try:
            while True:
                time.sleep(1)
                self.handle_events()

        except Exception as e:
            self.observer.stop()
            print(e)
            self.observer.join()

    def handle_events(self):
        if not self.event_handler.buffer:
            return
        buffer = self.event_handler.buffer
        buffer = list(set(buffer))
        # 파일 이동 시 새 경로에 생성을 먼저 하고 삭제 처리 하도록 한다.
        buffer = sorted(buffer, key=lambda x: self.event_order.index(x.key[0]))
        for event in buffer:
            if event.event_type == 'modified':
                from main import app
                from app.note.note import update_db

                with app.app_context():
                    update_db(event.src_path)

        self.event_handler.clear_buffer()
        print('-'*30)


class PageHandler(FileSystemEventHandler):

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
