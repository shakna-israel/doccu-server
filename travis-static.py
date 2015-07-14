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
