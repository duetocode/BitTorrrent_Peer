multiple_files_torrent = 'test/resources/multiple-files.torrent'
simple_file_torrent = 'test/resources/debian-9.9.0-amd64-netinst.iso.torrent'
simple_file_torrent_info_hash = '01397ef9739c0fa600ef28b7f4e5564ee7b25388'

def load_file(file):
    with open(file, 'rb') as fd:
        return fd.read()