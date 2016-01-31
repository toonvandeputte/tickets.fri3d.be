output = output
version = $(shell git log -1 --format=%ct-%h)
project = fr1ckets

all: populate

output:
	mkdir -p $(output)/src
	mkdir -p $(output)/conf
	mkdir -p $(output)/ssl

populate: output
	cp -R src/* $(output)/src/
	cp -R conf/* $(output)/conf/
	#cp -R ssl/* $(output)/ssl/

serve:
	python src/wsgi.py

deb: all
	./mkdeb.sh $(project) $(version) $(output)

clean:
	rm -rf $(output) *.deb
	find src/ -name '*.pyc' | xargs rm || true

.PHONY: clean serve
