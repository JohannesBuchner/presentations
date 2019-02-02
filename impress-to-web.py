import itertools 
import lxml
from lxml import etree
from lxml.etree import tostring
from itertools import chain
import sys, os

f = sys.argv[1]

def is_new_slide(n):
	return 'page-break-before:always; ' in n.xpath('./@style')

def get_flat_html_text(text):
	if text is None: return ''
	return text.replace('\n',' ').replace('  ', ' ').strip()

def stringify_children(node):
	parts = ([node.text] +
		list(chain(*([c.text, c.tail] for c in node.getchildren()))) +
		[node.tail])
	# filter removes possible Nones in texts and tails
	return '\n'.join(map(str, filter(None, parts)))

print('Parsing presentation text (%s)' % f)
parser = etree.XMLParser(recover=True)
root = etree.parse(f, parser)
body = root.find('body')
title = os.path.basename(f.replace('_text.html', ''))

#slide_titles = [get_flat_html_text(slide_title.text) for slide_title in body.findall('h1')]

slide_titles = []
slide_texts = []
texts = []
for n in body.getchildren():
	#if n.text is None: continue
	if is_new_slide(n):
		slide_texts.append('\n'.join(texts))
		if len(texts) > 0:
			slide_titles.append(get_flat_html_text(get_flat_html_text(texts[0])))
		else:
			slide_titles.append('')
		texts = []
	text = stringify_children(n).strip().replace('\n\n\n','\n').replace('\n\n','\n')
	if len(text) > 0:
		texts.append(text)
		
slide_texts.append('\n'.join(texts))
if len(texts) > 0:
	slide_titles.append(get_flat_html_text(get_flat_html_text(texts[0])))
else:
	slide_titles.append('')

title_node = body.find('h1')
if title_node and title_node.text and title_node.text.strip() != '':
	title = get_flat_html_text(title_node.text)
else:
	title = slide_titles[0]
print('  --> Presentation title is "%s"' % title)

print('  --> got %d slides (%d empty, %d slide titles)' % (len(slide_texts), sum([t.strip() == '' for t in slide_texts]), len(slide_titles)))

assert len(slide_titles) == len(slide_texts), (slide_titles, slide_texts)

print('  inserting slide texts into slide show')

for i, (slide_title, slide_text) in enumerate(zip(slide_titles, slide_texts)):
	slidefile = os.path.join(os.path.dirname(f), 'img%d.html' % i)
	slidehtml = open(slidefile).read()
	slidehtml = slidehtml.replace('<title>Slide %d</title>' % (i+1), '<title>%s</title>' % slide_title)
	slidehtml = slidehtml.replace('alt=""', 'alt="%s"' % slide_text)
	print("------------")
	print(slide_title)
	print("------------")
	print(slide_text)
	print()
	with open(slidefile, 'w') as fout:
		fout.write(slidehtml)
	del slidefile, slidehtml

abstract = ''
try:
	abstract = open(f.replace('_text.html', '_abstract.txt')).read()
	print('  found abstract!')
except IOError: 
	pass

print('  inserting slide texts and title into overview')

overviewf = f.replace('_text.html', '.html')

html = open(overviewf).read()
html = html.replace('<title>Slide 1</title>', '<title>%s</title>' % title)
html = html.replace('Title: &lt;title&gt;; Abstract: &lt;abstract&gt;', '<h1>%s</h1><p><b>Abstract</b>: %s</p>' % (title, abstract))

for i, slide_title in enumerate(slide_titles):
	html = html.replace('alt="Slide %d"' % (i+1), 'alt="%s"' % slide_text)
	html = html.replace('href="img%d.html">' % i, 'href="img%d.html" alt="%s">' % (i, slide_title))
with open(overviewf, 'w') as fout:
	fout.write(html)


