.PHONY: clean clean

all: check

clean:
	find . -name '*~' | xargs rm -f
	find . -name '*pyc' | xargs rm -f
	cd tests ; make clean

check:
	codecheck *.py
	pychecker2 *.py
