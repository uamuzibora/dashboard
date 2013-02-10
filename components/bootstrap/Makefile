BOOTSTRAP = ./docs/assets/css/bootstrap.css
BOOTSTRAP_LESS = ./less/bootstrap.less
BOOTSTRAP_RESPONSIVE = ./docs/assets/css/bootstrap-responsive.css
BOOTSTRAP_RESPONSIVE_LESS = ./less/responsive.less

OUTPUT_CSS = ../../webroot/css/bootstrap.css
OUTPUT_CSS_RESPONSIVE = ../../webroot/css/bootstrap-responsive.css
OUTPUT_JS = ../../webroot/css/js/bootstrap.js
OUTPUT_CSS_MIN = ../../webroot/css/bootstrap.min.css
OUTPUT_CSS_RESPONSIVE_MIN = ../../webroot/css/bootstrap-responsive.min.css
OUTPUT_JS_MIN = ../../webroot/css/js/bootstrap.min.js
OUTPUT_IMG= ../../webroot/img

DATE=$(shell date +%I:%M%p)
CHECK=\033[32m✔\033[39m
HR=\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#

#
# CLEANS THE ROOT DIRECTORY OF PRIOR BUILDS
#

clean:
	rm -r bootstrap

#
# BUILD SIMPLE BOOTSTRAP DIRECTORY
# recess & uglifyjs are required
#

bootstrap: bootstrap-img bootstrap-css bootstrap-js

#
# JS COMPILE
#
bootstrap-js: bootstrap/js/*.js

bootstrap/js/*.js: js/*.js
	mkdir -p bootstrap/js
	cat js/bootstrap-transition.js js/bootstrap-alert.js js/bootstrap-button.js js/bootstrap-carousel.js js/bootstrap-collapse.js js/bootstrap-dropdown.js js/bootstrap-modal.js js/bootstrap-tooltip.js js/bootstrap-popover.js js/bootstrap-scrollspy.js js/bootstrap-tab.js js/bootstrap-typeahead.js js/bootstrap-affix.js > bootstrap/js/bootstrap.js
	uglifyjs -nc bootstrap/js/bootstrap.js > bootstrap/js/bootstrap.min.tmp.js
	echo "/*!\n* Bootstrap.js by @fat & @mdo\n* Copyright 2012 Twitter, Inc.\n* http://www.apache.org/licenses/LICENSE-2.0.txt\n*/" > bootstrap/js/copyright.js
	cat bootstrap/js/copyright.js bootstrap/js/bootstrap.min.tmp.js > ${OUTPUT_JS_MIN}
	rm bootstrap/js/copyright.js bootstrap/js/bootstrap.min.tmp.js

#
# CSS COMPLILE
#

bootstrap-css: bootstrap/css/*.css

bootstrap/css/*.css: less/*.less
	mkdir -p bootstrap/css
	recess --compile ${BOOTSTRAP_LESS} > ${OUTPUT_CSS}
	recess --compress ${BOOTSTRAP_LESS} > ${OUTPUT_CSS_MIN}
	recess --compile ${BOOTSTRAP_RESPONSIVE_LESS} > ${OUTPUT_CSS_RESPONSIVE}
	recess --compress ${BOOTSTRAP_RESPONSIVE_LESS} > ${OUTPUT_CSS_RESPONSIVE_MIN}

#
# IMAGES
#

bootstrap-img: bootstrap/img/*

bootstrap/img/*: img/*
	cp img/* ${OUTPUT_IMG}

#
# WATCH LESS FILES
#

watch:
	echo "Watching less files..."; \
	watchr -e "watch('less/.*\.less') { system 'make' }"
