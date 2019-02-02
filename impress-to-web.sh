
find presentations_prev/ presentations/ -name '*.odp' |while read i; do
#i=$1

OUTDIR=presentations-export
o=${OUTDIR}/$(basename ${i/.odp/})

mkdir -p $o

echo "Converting $i ..."
echo "Creating slide show with unoconv ..."
# "documented" here: https://github.com/LibreOffice/core/blob/31bd7e8c531a9a8e470d96540d730a98da0e81b7/sd/source/filter/html/htmlex.cxx
# https://ask.libreoffice.org/en/question/2641/convert-to-command-line-parameter/
LANG=en unoconv --doctype=presentation --format=html \
	-e PublishMode=0 \
	-e IsExportContentsPage=true \
	-e IsUseDocumentColors=true \
	-e Width=900 \
	-e Format=2 \
	-e Compression='99%' \
	-e Author='Johannes Buchner' \
	-e HomepageURL=http://astrost.at/istics/ \
	-e EnableDownload=true \
	-e UserText='Title: <title>; Abstract: <abstract>' \
	--output=${o}/$(basename ${i/.odp/.html}) $i

echo
echo "Extracting text of slides ..."
LANG=en libreoffice --headless --convert-to html:impress_html_Export --outdir presentations-export/ $i
mv -v ${OUTDIR}/$(basename ${i/.odp/.html}) $o/$(basename ${i/.odp/_text.html})

cp -v ${i/.odp/_abstract.txt} $o/$(basename ${i/.odp/_abstract.txt})

echo "Combining ..."
python3 impress-to-web.py $o/$(basename ${i/.odp/_text.html}) || break
echo

done

