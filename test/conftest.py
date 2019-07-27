import pytest
from types import SimpleNamespace
from bittorrent.bencoding import decode, ByteStringBuffer
from test.utils import *

#@pytest.fixture(autouse=True)
#def multipleFilesContext(tmpdir):
