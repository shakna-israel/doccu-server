import requests

def download_file(url, fileName):
    """A procedural download, to allow for interruptions and large file sizes."""
    url_request = requests.get(url, stream=True)
    with open(fileName,'wb') as fileOpen:
        for chunk in url_request.iter_content(chunk_size=1024):
            if chunk:
                fileOpen.write(chunk)
                fileOpen.flush()

download_file('https://raw.githubusercontent.com/bpampuch/pdfmake/master/build/pdfmake.min.js', '.doccu/static/js/pdfmake.min.js')
download_file('https://raw.githubusercontent.com/bpampuch/pdfmake/master/build/vfs_fonts.js', '.doccu/static/js/vfs_fonts.js')

import os

for dirname, dirnames, filenames in os.walk('.'):
    # print path to all subdirectories first.
    for subdirname in dirnames:
        print(os.path.join(dirname, subdirname))

    # print path to all filenames.
    for filename in filenames:
        print(os.path.join(dirname, filename))

    # Advanced usage:
    # editing the 'dirnames' list will stop os.walk() from recursing into there.
    if '.git' in dirnames:
        # don't go into any .git directories.
        dirnames.remove('.git')
