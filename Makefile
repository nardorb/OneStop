PYTHON          = python2.7
APPENGINE       = /usr/local/google_appengine
APP_ID          = transapptool
SERVE_PORT      = 9098
SERVE_ADDRESS   = 0.0.0.0
DATASTORE_PATH  = ./datastore

test:
	@export PYTHONPATH="$(APPENGINE)" && ./run_unit_tests.py

pep8:
	@./run_pep8_check.py --exclude="environment" .

pyflakes:
	@pyflakes .

serve:
	@$(PYTHON) $(APPENGINE)/dev_appserver.py \
		--host=$(SERVE_ADDRESS) \
		--port=$(SERVE_PORT) \
		--datastore_path=$(DATASTORE_PATH) \
		.

deploy:
	@make -s css js
	@make -s update-indexes
	@./wait_for_indexes.py
	@make -s update
	@make -s vacuum-indexes

console:
	@$(PYTHON) $(APPENGINE)/remote_api_shell.py $(APP_ID)

update:
	@$(PYTHON) $(APPENGINE)/appcfg.py \
		--noauth_local_webserver \
		--oauth2 \
		--version=autodeployed \
		update .
	@$(PYTHON) $(APPENGINE)/appcfg.py \
		--noauth_local_webserver \
		--oauth2 \
		--version=autodeployed \
		backends update .

update-indexes:
	@$(PYTHON) $(APPENGINE)/appcfg.py \
		--noauth_local_webserver \
		--oauth2 \
		update_indexes .

vacuum-indexes:
	@$(PYTHON) $(APPENGINE)/appcfg.py \
		--noauth_local_webserver \
		--oauth2 \
		--force \
		vacuum_indexes .

css:
	@echo -n "Compiling CSS..."
	@lessc media/less/project.less media/project.css
	@yui-compressor media/project.css -o media/project.min.css
	@echo " done."

js:
	@echo -n "Compiling Javascript..."
	@cat \
		media/date.js \
		media/time.js \
		media/jquery.js \
		media/bootstrap.js \
		media/bootstrap-datepicker.js \
		media/bootstrap-daterangepicker.js \
		media/bootstrap-timepicker.js \
		media/application.js \
		> media/project.js
	@jsmin < media/project.js > media/project.min.js
	@echo " done."

remove-trailing-whitespace:
	@find -type f | egrep '\.(py|css|less|js|html|haml)$$' | \
		xargs sed -i 's/[ \t]*$$//g'
