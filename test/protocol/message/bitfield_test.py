from bittorrent.context import PieceInfo, PieceState
from bittorrent.protocol.message import Bitfield

def test_init_from_piece_list():
    mockList = [PieceInfo(state=PieceState.Have if i % 3 == 0 else PieceState.NotHave) for i in range(20)]
    mockList = list(mockList)

    bitfield = Bitfield(pieces=mockList)

    assert bitfield is not None
    assert bitfield.serialize() == b'\x92\x49\x20'

def test_parse_from_raw_data():
    bitfield = Bitfield.parse(b'\x92\x49\x20')
    assert bitfield is not None
    assert bitfield.array[0:4] == [True, False, False, True]
    assert bitfield.array[-6:] == [True, False, False, False, False, False]