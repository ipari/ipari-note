from flask import Blueprint
from app.utils import config

url_prefix = config('note')['base_url']
bp = Blueprint('note', __name__, url_prefix=f'/{url_prefix}')

from app.note import routes
