sdist:
	python setup.py sdist

rpm: sdist
	rpmbuild -ba smugapi.spec --define "_sourcedir `pwd`/dist"

srpm: sdist
	rpmbuild -bs smugapi.spec --define "_sourcedir `pwd`/dist"

clean:
	rm -rf MANIFEST build dist usr *~ smugapi.spec *.pyc
