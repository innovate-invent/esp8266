## 
## Copyright (c) dushin.net  All Rights Reserved
## 
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of dushin.net nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
## 
## THIS SOFTWARE IS PROVIDED BY dushin.net ``AS IS'' AND ANY
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL dushin.net BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
## 

LOGGING_MODULES= \
	logging/ulog.py \
	logging/console_sink.py \
	logging/syslog_sink.py

UHTTPD_MODULES=\
	uhttpd/uhttpd/__init__.py \
	uhttpd/uhttpd/file_handler.py \
	uhttpd/uhttpd/api_handler.py \
	uhttpd/demo/stats_api.py \
	uhttpd/demo/my_api.py

TOOL_MODULES=\
	tools/ush.py

TEST_MODULES=\
	uhttpd/test/test_server.py

WEB_CONSOLE_MODULES=\
	web-console/api.py

MODULES=$(LOGGING_MODULES) $(UHTTPD_MODULES) $(TOOL_MODULES) $(TEST_MODULES) $(WEB_CONSOLE_MODULES)
OUTPUTS=$(patsubst %.py, build/mpy/%.mpy, $(MODULES))

all: $(OUTPUTS)

clean:
	rm -rf build

build/mpy/%.mpy: %.py
	@mkdir -p $(@D)
	mpy-cross -o $@ $<
