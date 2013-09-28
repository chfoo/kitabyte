PREFIX ?= /usr/local
PYTHON2=python
BUILD_DIR=./build/
FORMAT_ARGS ?= --format sfd otf woff ttf

.PHONY: build

build:
	mkdir -pv $(BUILD_DIR)
	PYTHONPATH=src $(PYTHON2) -m kitabyte.build $(BUILD_DIR) $(FORMAT_ARGS)

report:
	PYTHONPATH=src $(PYTHON2) -m kitabyte.coverage

sheet:
	PYTHONPATH=src $(PYTHON2) -m kitabyte.image

install:
	mkdir -pv $(DESTDIR)/$(PREFIX)/share/fonts/opentype/kitabyte/
	cp -v $(BUILD_DIR)/*.otf $(DESTDIR)/$(PREFIX)/share/fonts/opentype/kitabyte/

clean:
	rm -fvr $(BUILD_DIR)
