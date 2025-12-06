SHELL = /bin/bash


#Targets
# download
# tsv2xml
# > 3 elements 
# name it sample.xml
# xml2json
# json2tsv
# check
# report
# all (runs them all)

.PHONY: download tsv2xml xml2json json2tsv check report all

download: data.tsv
data.tsv:
	curl -o data.tsv "https://ufal.mff.cuni.cz/~zabokrtsky/courses/npfl125/data/dependency_trees_from_ud.tsv"; \

tsv2xml: data.tsv convert_to_xml.py
	python3 convert_to_xml.py data.tsv sample.xml

xml2json: sample.xml convert_xml_to_json.py
	python3 convert_xml_to_json.py sample.xml sample.json

json2tsv: sample.json convert_json_to_tsv.py
	python3 convert_json_to_tsv.py sample.json sample.tsv

check: json2tsv
	@if ! cmp -s sample.tsv data.tsv; then \
		echo 'ERROR'; \
	fi

all: download tsv2xml xml2json json2tsv check report

report: 
	@printf '%s\n' \
		"Conversion to XML:" \
		"	Here i chose to structure the xml so that each sentence is separate element and each sentence has some text. Then as a child of sentence there is token element " \
		"	which has all the records about the id, form, lemma, pos and head. Root element is corpus" \
		"	Structure of XML: " \
		"	<corpus> " \
		"	 <sentence> " \
 		"		<text>...</text>"\
		"		<token>"\
		"			<id>1</id>"\
		"			<form>From</form>"\
		"			<lemma>from</lemma>"\
		"			<pos>ADP</pos>"\
		"			<head>3</head>"\
		"		</token>"\
		"		..."\
		"	 </sentence>"\
		"	 ..."\
		"	</corpus>" \
		"	In this task i used xml.etree.ElementTree and minidom from xml.dom"\
		"	I faced a little difficulty about the encodings because iam not sure if conversion to unicode in prettyxml is really needed, but I left it there anyway"\
		""\
		"Conversion XML2JSON:"\
		"	Here I chose to structure the json so that each sentence is in the same block as its tokens which are the words of each sentence with again all data of word respectively (id, form,...) these tokens are "\
		"	    structure of JSON:"\
		"		{"\
		"		"corpus": [ "\
		"			{ "\
		"			"sentence": ..., "\
		"			"tokens": [ "\
		"				{ "\
		"				"id": 1, "\
		"				"form": ..., "\
		"				"lemma": ..., "\
		"				"pos": ..., "\
		"				"head": ... "\
		"				}, "\
		"				... "\
		"				] "\
		"			}, "\
		"				... "\
		"			] "\
		"		} "\
		"	Here i ommitted the unicode and it works fine. The libraries i used were only json pydoc xml.etree.ElementTree"\
		"	Conversion back from JSON to TSV: "\
		"	    # sentence-text: <text> "\
		"		id\tform\tlemma\tpos\thead "\
		"		id\tform\tlemma\tpos\thead "\
		"		... "\
		"		(empty line between sentences) "\
		"	Here i stuggled with the dependencies in the target in Makefile but i think it works properly now. I used only json library here"

