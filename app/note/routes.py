from app.note import bp


@bp.route('/<path:page_path>', methods=['GET', 'POST'])
def note(page_path):
    return f'Note page for "{page_path}".'
