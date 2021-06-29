import threading

from app import create_app
from app.watcher import PageWatcher


app = create_app()
watcher = PageWatcher()

thread = threading.Thread(target=watcher.watch, args=())
thread.daemon = True
thread.start()

if __name__ == '__main__':
    app.run(threaded=True)
