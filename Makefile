.PHONY: clean check

all: check

clean:
	find . -name "*~" -or -name "*.pyc" -print0 | xargs -0 rm -f
	cd tests ; make clean

check:
	codecheck *.py
	pychecker2 *.py
