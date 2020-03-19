from app.utils import config
from app.note.note import *
from app.note.permission import delete_permission


def save_page(page_path, raw_md):
    file_path = get_file_path(page_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(raw_md)


def delete_page(page_path):
    # 퍼미션 제거
    delete_permission(page_path)

    # 파일 제거
    file_path = get_file_path(page_path)
    os.remove(file_path)

    # 빈 디렉터리 제거 (첫 2개는 data/pages)
    page_dir_length = len(PAGE_DIR.split('/'))
    dirs = os.path.dirname(file_path).split('/')[page_dir_length:]
    for x in range(len(dirs), 0, -1):
        subdir = os.path.join(PAGE_DIR, *dirs[:x])
        try:
            if len(os.listdir(subdir)) == 0:
                os.rmdir(subdir)
        except OSError:
            continue


def edit_page(page_path):
    file_path = get_file_path(page_path)
    base_url = config('note.base_url')
    raw_md = get_raw_page(file_path)
    # ` 문자는 ES6에서 템플릿 문자로 사용되므로 escape 해줘야 한다.
    raw_md = raw_md.replace('`', '\`')
    return render_template('edit.html',
                           pagename=page_path,
                           meta=get_note_meta(),
                           menu=get_menu_list(),
                           base_url=base_url,
                           raw_md=raw_md)
