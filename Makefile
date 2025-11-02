SHELL=/bin/bash
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

t11: skakalpes-utf8
	sed 's/[[:space:][:punct:]]/\n/g' $< 

t12: skakalpes-utf8
	sed 's/[[:space:][:punct:]]/\n/g' $< | grep -v '^$$'

t13: skakalpes-utf8
	sed 's/[[:space:][:punct:]]/\n/g' $< | grep -v '^$$' | sort 

t14: skakalpes-utf8
	sed 's/[[:space:][:punct:]]/\n/g' $< | grep -v '^$$' | wc -l

