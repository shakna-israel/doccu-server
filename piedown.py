"""
Piedown is a small python script that converts Markdown text
to HTML using only regular expressions.

Usage:
  cat page.md | piedown.py > page.html

Where:
 - 'page.md' is the Markdown source file; and
 - 'page.html' is the generated file containing the produced HTML.

LEGAL:
This work is inspired by the work of Johnny Broadway <johnny@johnnybroadway.com>
on Slimdown <https://gist.github.com/jbroadway/2836900> which is licensed under
the MIT license <http://opensource.org/licenses/MIT>.

This work is licensed under the MIT LICENSE <http://opensource.org/licenses/MIT>
with copyright attribution to: Lucas Possatti (2015).
"""

import re
import sys
import collections


########################
### Helper Functions ###
########################

def paragraph(match_obj):
	line = match_obj.group(1)
	trimmed = line.strip()
	if re.search(r'^<\/?(ul|ol|li|h|p|bl)', trimmed):
		return "\n" + line + "\n"
	return "\n<p>{}</p>\n".format(trimmed);

def ul_list(match_obj):
	item = match_obj.group(1);
	return "\n<ul>\n\t<li>{}</li>\n</ul>".format(item.strip());

def ol_list(match_obj):
	item = match_obj.group(1);
	return "\n<ol>\n\t<li>{}</li>\n</ol>".format(item.strip());

def blockquote(match_obj):
	item = match_obj.group(2);
	return "\n<blockquote>{}</blockquote>".format(item.strip());

def header(match_obj):
	level = len(match_obj.group(1))
	title = match_obj.group(2).strip()
	return '<h{0}>{1}</h{0}>'.format(level, title)


########################
### Rules Definition ###
########################

rules = collections.OrderedDict()
rules[r'(#+)(.*)'] = header # headers
rules[r'\[([^\[]+)\]\(([^\)]+)\)'] = r'<a href="\2">\1</a>' # links
rules[r'(\*\*|__)(.*?)\1'] = r'<strong>\2</strong>' # bold
rules[r'(\*|_)(.*?)\1'] = r'<em>\2</em>' # emphasis
rules[r'\~\~(.*?)\~\~'] = r'<del>\1</del>' # del
rules[r'\:\"(.*?)\"\:'] = r'<q>\1</q>' # quote
rules[r'`(.*?)`'] = r'<code>\1</code>' # inline code
rules[r'\n\*(.*)'] = ul_list # ul lists
rules[r'\n[0-9]+\.(.*)'] = ol_list # ol lists
rules[r'\n(&gt;|\>)(.*)'] = blockquote # blockquotes
rules[r'\n-{5,}'] = r"\n<hr />" # horizontal rule
rules[r'\n([^\n]+)\n'] = paragraph # add paragraphs
rules[r'<\/ul>\s?<ul>'] = r'' # fix extra ul
rules[r'<\/ol>\s?<ol>'] = r'' # fix extra ol
rules[r'<\/blockquote><blockquote>'] = r"\n" # fix extra blockquote


#######################
### Render Function ###
#######################

def render(text):
	text = '\n' + text + '\n'
	for regex, replacement in rules.items():
		text = re.sub(regex, replacement, text)
	return text.strip()


############
### Main ###
############

if __name__ == '__main__':
	input_text = sys.stdin.read()
	rendered_text = render(input_text)
	print(rendered_text)
