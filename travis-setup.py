import requests
import json

def download_file(url, fileName):
    """A procedural download, to allow for interruptions and large file sizes."""
    url_request = requests.get(url, stream=True)
    with open(fileName,'wb') as fileOpen:
        for chunk in url_request.iter_content(chunk_size=1024):
            if chunk:
                fileOpen.write(chunk)
                fileOpen.flush()

def download_static():
	download_file('https://raw.githubusercontent.com/bpampuch/pdfmake/master/build/pdfmake.min.js', '.doccu/static/js/pdfmake.min.js')
	download_file('https://raw.githubusercontent.com/bpampuch/pdfmake/master/build/vfs_fonts.js', '.doccu/static/js/vfs_fonts.js')

def generate ids():
	ids = {}
	ids['testing-bot'] = {}
	ids['testing-bot']['key'] = '223344997766551100'
	ids['testing-bot']['group'] = 'superadmin'
	ids['testing-bot']['email'] = 'doccu-testing-bot@shaknaisrael.com'
	json.dump(ids,open('.doccu/ids.dbs','w+'))

def main():
	generate_ids()
	download_static()

if __name__ == '__main__':
	main()