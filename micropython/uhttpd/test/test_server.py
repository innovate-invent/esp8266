#
# Copyright (c) dushin.net  All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of dushin.net nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY dushin.net ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL dushin.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import uos
import uhttpd


def mkdir(path):
    try:
        uos.mkdir(path)
    except OSError as e:
        pass


def write(filename, str):
    f = open(filename, 'w')
    f.write(str)
    f.close()


def init(root_path='/test'):
    print("Initializing from {}...".format(root_path))
    mkdir('{}'.format(root_path))
    write('{}/index.html'.format(root_path), "<html><body>Hello World!</body></html>")
    mkdir('{}/foo'.format(root_path))
    write('{}/foo/test.txt'.format(root_path), "test")
    mkdir('{}/foo/bar'.format(root_path))
    write('{}/foo/bar/test.js'.format(root_path), "{'foo': \"bar\"}")
    write('{}/foo/bar/test.css'.format(root_path), "html")


class TestAPIHandler:
    def __init__(self):
        pass

    def get(self, api_request):
        #print(api_request)
        context = api_request['context']
        if len(context) > 0:
            what_to_return = context[0]
            if what_to_return == 'query_params':
                query_params = api_request['query_params']
                return query_params
            elif what_to_return == "nothing":
                return None
            elif what_to_return == "empty":
                return b''
            elif what_to_return == "something":
                return b'something'
            elif what_to_return == "html":
                return "<html><body><h1>HTML</h1></body></html>"
            elif what_to_return == "json":
                return {'some': [{'j': 1, 's': [], 'o': "str", 'n': {"дружище": "バディ"}}]}
            elif what_to_return == "int":
                return 1342
            elif what_to_return == "float":
                return 3.14159
            elif what_to_return == "bad_request_excetion":
                raise uhttpd.BadRequestException("derp")
            elif what_to_return == "not_found_excetion":
                raise uhttpd.NotFoundException("what you were looking for")
            elif what_to_return == "forbidden_excetion":
                raise uhttpd.ForbiddenException("tsktsk")
        else :
            return {'action': 'get'}

    def put(self, api_request):
        return {'action': 'put'}

    def post(self, api_request):
        return {'action': 'post'}

    def delete(self, api_request):
        return {'action': 'delete'}


server = None

def run(root_path='/test', port=80, backlog=10):
    print("Starting test server ...")
    import uhttpd
    import uhttpd.file_handler
    file_handler = uhttpd.file_handler.Handler(root_path=root_path)
    import uhttpd.api_handler
    api_handler = uhttpd.api_handler.Handler(
        [(['test'], TestAPIHandler())]
    )
    global server
    server = uhttpd.Server([
        ('/api', api_handler),
        ('/test', file_handler)
    ], {
        'port': port,
        'require_auth': True,
        'backlog': backlog
    })
    server.run()


def test(root_path='/test', port=80):
    init(root_path=root_path)
    run(root_path=root_path, port=port)
