import os
import re
import markdown
import requests

def send_email(email_address,name_to,body_text):
    api_key = 'https://api.mailgun.net/v2/shaknaisrael.com/messages'
    try:
        my_api = os.environ['MAILGUN_KEY']
    except KeyError:
    	return False
    body_text = '# Doccu Alert\n\n---\n\n' + str(body_text) + '\n\n' + '---\n\nThis has been an automated email, from your friendly Doccu server.\n\nSupport: Call on [0459 528 387](tel:0061459528387), or reply to [this email](mailto:doccu@shaknaisrael.com).'
    markdown_text = markdown.markdown(str(body_text))
    plain_text = re.sub('<[^<]+?>', '', markdown_text)
    return requests.post(
        api_key,
        auth=("api", str(my_api)),
        data={"from": 'doccu@shaknaisrael.com',
              "to": str(email_address),
              "subject": 'Doccu Alert for ' + str(name_to),
              "text": str(plain_text),
              "html": str(markdown_text),
              "o:tracking": True})