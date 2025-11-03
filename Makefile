SHELL=/bin/bash

skakalpes-il2.txt:
	wget -O skakalpes-il2.txt https://ufal.mff.cuni.cz/~zabokrtsky/courses/npfl125/data/skakalpes-il2.txt
t1:
	echo "Hello world"
t2:
	cat skakalpes-il2.txt

skakalpes-utf8:
	iconv -f iso-8859-2 -t UTF-8 skakalpes-il2.txt > $@ 

t3: skakalpes-utf8
	cat $<

t4: skakalpes-utf8
	 wc -l <  $<	

t5: skakalpes-utf8
	wc -w < $<

t6: skakalpes-utf8
	head -15 < $<

t7: skakalpes-utf8 
	tail -15 < $<

t8: skakalpes-utf8
	sed -n '10,20p' $<

t9: skakalpes-utf8
	cut -d ' ' -f 1,2  $<

t10: skakalpes-utf8
	grep '[0-9]' $<

# Helper targets for saving the actual results into the files
t11.txt: skakalpes-utf8
	sed 's/[[:space:][:punct:]]/\n/g' $< > $@
t11: t11.txt 
	cat t11.txt 

t12.txt: t11.txt
	grep -v '^$$' $< >$@
t12: t12.txt 
	cat t12.txt 

t13.txt: t12.txt
	sort $< > $@
t13: t13.txt 
	cat t13.txt

t14.txt: t12.txt
	wc -l < $< >$@	
t14: t14.txt 
	cat t14.txt 

t15: t12.txt
	sort $< | uniq | wc -l

t16: t12.txt
	sort $< | uniq -c | sort -nr 

t17.txt: skakalpes-utf8 
	fold -w1 $< | grep '[A-Za-z]' | sort | uniq -c > $@

t17: t17.txt 
	cat t17.txt

t18.txt: t12.txt
	# creating shifted version 
	tail -n +2 $< > t12_shifted.txt
	paste t12.txt t12_shifted.txt | head -n -1 | sort | uniq -c | sort -nr >$@
	# cleanup
	rm t12_shifted.txt || true

t18: t18.txt
	 cat t18.txt     


example.html: 
	wget -O example.html https://ufal.mff.cuni.cz

t19: example.html
	 # extracting words (letters only), one per line
	sed 's/[^A-Z]/ /g' $< | tr ' ' '\n' | grep -E '^[A-Z]+$$' > t19_words.txt
	# creating shifted version for bigrams
	tail -n +2 t19_words.txt > t19_words_shifted.txt
	paste t19_words.txt t19_words_shifted.txt | head -n -1 
	# cleanup
	rm t19_words.txt t19_words_shifted.txt

t20: example.html
	grep -o '<[[:alnum:]]\+' example.html | sed 's/^<//' | sort | uniq -c | sort -nr
