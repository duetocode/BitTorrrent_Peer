from bittorrent.storage import Storage
from test.utils import *

def test_start(multipleFilesContext):
    storage = Storage(multipleFilesContext, None)
    storage.start()