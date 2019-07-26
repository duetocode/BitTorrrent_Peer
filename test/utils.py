multiple_files_torrent = 'test/resources/multiple-files.torrent'
simple_file_torrent = 'test/resources/debian-9.9.0-amd64-netinst.iso.torrent'

def load_file(file):
    with open(file, 'rb') as fd:
        return fd.read()