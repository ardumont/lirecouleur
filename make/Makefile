all : lirecouleur.oxt tests web

clean :
	rm -r images locale pythonpath template lirecouleur.dic lirecouleurooo.py AddonUI.xcu description.xml lirecouleur.oxt
	rm -r Factories.xcu lirecouleur.xcu WriterWindowState.xcu lirecouleur.xcs lcfactory.py icon.png
	rm ../tests/lirecouleur.* 
	rm -r ../src/firefox-plugin/data/lirecouleur.js

core : ../src/opendocument-plugin
	cp -r ../src/opendocument-plugin/* .

lirecouleur.oxt : core
	zip -r $@ locale template pythonpath Legal META-INF Descriptions images
	zip $@ lcfactory.py
	zip $@ lirecouleurooo.py
	zip $@ description.xml
	zip $@ lirecouleur.xcs
	zip $@ lirecouleur.xcu
	zip $@ lirecouleur.dic
	zip $@ AddonUI.xcu
	zip $@ WriterWindowState.xcu
	zip $@ Factories.xcu
	zip $@ icon.png

tests : ../src/opendocument-plugin/pythonpath/lirecouleur/lirecouleur.py ../src/opendocument-plugin/lirecouleur.dic ../tests/tests_lirecouleur.py
	cp ../src/opendocument-plugin/pythonpath/lirecouleur/lirecouleur.py ../tests/
	cp ../src/opendocument-plugin/lirecouleur.dic ../tests/
	python ../tests/tests_lirecouleur.py

web :
	cp ../src/ckeditor-plugin/lirecouleur.js ../src/firefox-plugin/data/
