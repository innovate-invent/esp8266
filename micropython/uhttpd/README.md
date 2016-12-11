# Micropython HTTP daemon

This set of modules provides a simple HTTP framework and server, providing an HTTP interface into your ESP8266.  Having an HTTP server allows developers to create management consoles for their ESP8266 devices, which can be very useful for configuration and troubleshooting devices, or even for bootstrapping them from an initial state.

Features include:

* Support for a strict subset of the HTTP/1.1 protocol (RFC 2616)
* Asynchronous handling of requests, so that the server can run while the ESP8266 runs other tasks
* Support for HTTP/Basic authentication
* Handler for servicing files on the Micropython file system
* Extensible API for adding REST-ful JSON-based APIs


By itself, the `uhttpd` module is just a TCP server and framework for adding handlers to process HTTP requests.  The actual servicing of HTTP requests is done by installing handlers, which are passed to the `uhttpd` server at creation time.  It's the handlers that actually do the heavy lifting when it comes to servicing HTTP requests.  

This package includes handlers for servicing files on the micropython file system (e.g., HTML, Javascript, CSS, etc), as well as handlers for managing REST-ful API calls, essential components in any modern web-based application.

Once started, the `uhttpd` server runs in the background, so that the ESP8266 can do other tasks.  When the server accepts a request, however, the ESP8266 will block for the period of time it takes to accept the request.

TCP/IP connections between clients and the `uhttpd` server endure for the duration of a single request.  Once the client opens a connection to the server, the server will dispatch the request to an appropriate handler and wait for the response from the handler.  It will then send the response back to the client on the open connection, and then close the connection from the client.
 
A driving design goal of this package is to have minimal impact on the ESP8266 device, itself, and to provide the tools that allow developers to implement rich client-side applications.  By design, web applications built with this framework should do as little work as possible on the server side, but should instead make use of modern web technologies to allow the web client or browser to perform significant parts of business logic.  In most cases, the web clients will have far more memory and compute resources than the ESP8266 device, itself, so it is wise to keep as much logic as possible on the client side.

> Warning: This software currently provides no transport-layer protection for your applications.  When this software is running, requests are sent in clear text, including not only the HTTP headers you may use for authentication, but also the contents of the HTTP requests and responses.  Malicious users on your network using off-the-shelf packet sniffers can read your HTTP traffic with no difficulty.  AS WRITTEN, THIS SOFTWARE IS NOT INTENDED FOR USE IN AN UNTRUSTED NETWORK!

The following work is planned for the future:

* Support for HTTP/S

## Modules and Dependencies

The `uhttpd` framework and server is comprised the following python modules:

* `uhttpd.py` -- provides HTTP server and framework
* `http_file_handler.py` -- a file handler for the `uhttpd` server
* `http_api_handler.py` -- a handler for servicing REST-ful APIs
* `stats_api_handler` -- an API handler used to service run-time statistics about the device

This module relies on the `ulog` facility, defined in the [logging](/micropython/logging) area of this repository.

There is currently no `upip` support for this package.

## Loading Modules

Some of the modules in this package require significant amounts of RAM to load and run.  While you can run these modules by loading them on the Micropython file system and allowing the runtime to compile the source modules for you, it is recommended to either freeze the modules in your firmware (a rather involved process, and recommended for production), or to compile to bytcode and load the generated `.mpy` files (recommended for development), which will decrease the memory footprint of your application using these modules.  You can acquire the `mpy-cross` tool which will compile micro python source modules to bytecode, by installing and building the micro python source project, as described [here](https://github.com/micropython/micropython/tree/master/esp8266)

Once you have the `mpy-cross` tool built, you can use the supplied `Makefile` to generate `.mpy` files.  Loading the generated bytecode files, instead of the python files, will reduce memory overhead during the development process of your application.

> Note.  The Makefile assumes the presence of `mpy-cross` in your executable path.

For example, to build the bytecode, 

    prompt$ export PATH=/Volumes/case-sensitive/micropython/mpy-cross:$PATH
    prompt$ pwd
    /work/src/github/fadushin/esp8266/micropython
    prompt$ make
    mpy-cross logging/ulog.py
    mpy-cross logging/console_sink.py
    mpy-cross logging/syslog_sink.py
    mpy-cross uhttpd/uhttpd.py
    mpy-cross uhttpd/http_file_handler.py
    mpy-cross uhttpd/http_api_handler.py
    mpy-cross uhttpd/stats_api.py
    mpy-cross tools/ush.py

If you have `webrepl` running and `webrepl_cli.py` in your `PATH`, then you can upload the files you need to your device (adjusted of course for the IP address of your ESP8266), as follows:

    prompt$ export PATH=/Volumes/case-sensitive/webrepl:$PATH
    prompt$ bin/upload.sh 192.168.1.180 logging/*.mpy uhttpd/*.mpy

The above command will use the `webrepl_cli.py` tool to upload the needed files to your ESP8266, using the `webrepl` server.

## Basic Usage

Start by creating a directory (e.g., `www`) on your file system in which you can place HTML (or other) files:

    >>> import os
    >>> os.mkdir('www')
    >>> os.chdir('www')
    >>> f = open('index.html', 'w')
    >>> f.write('<html><body>Hello World!</body></html>')
    38
    >>> f.close()
    >>> os.listdir()
    ['index.html']

To run the `uhttpd` server, initialize an instance of the `uhttpd.Server` class with an ordered list of tuples, which map URL prefixes to handlers, and start the server.  When creating a HTTP file handler, you can optionally specify the "root" of the file system from which to serve files. 

For example, to start the server with the file handler rooted off the `/www` path, use the following: 

    >>> import uhttpd
    >>> import http_file_handler
    >>> server = uhttpd.Server([('/', http_file_handler.Handler('/www'))])
    >>> server.start()

You should then see some logs printed to the console, indicating that the server is listening for connections:

    2000-01-01T08:09:15.005 [info] esp8266: TCP server started on 192.168.4.1:80
    2000-01-01T08:09:15.005 [info] esp8266: TCP server started on 0.0.0.0:80

By default, the `uhttpd` server requires authentication, using the username `admin` and the password `uhttpD`.  These credentials are configurable.  (See reference section, below)

You may now connect to your ESP8266 via a web browser or curl and browse your file system, e.g.,

    prompt$ curl -i 'http://192.168.1.180/' 
    HTTP/1.1 200 OK
    Content-Length: 38
    Content-Type: text/html
    
    <html><body>Hello World!</body></html>

## HTTP Authentication

The `uhttpd.Server` supports HTTP Basic authentication.  By default, HTTP authentication is not required, but you can configure the `uhttpd.Server` to require authentication by setting the `require_auth` configuration property to `True` in the `uhttpd.Server` constructor.  (For more information about the `uhttpd.Server` constructor, see the _Configuration_ section below.)

    >>> import uhttpd
    >>> import http_file_handler
    >>> server = uhttpd.Server(
        [('/', http_file_handler.Handler('/www'))],
        {'require_auth': True}
    )
    >>> server.start()

The default HTTP user name is `admin`, and the default password is `uhttpD`, but these values are configurable, as described in the _Configuration_ section, below.  This server only supports one username and password for each server instance.

Warning: This software currently provides no transport-layer protection for your applications.  HTTP credentials, while obfuscated with BASE-64 encoding, per the HTTP 1.1 spec, are sent in plaintext, and are therefore accessible to malicious parties on your network.  AS WRITTEN, THIS SOFTWARE IS NOT INTENDED FOR USE IN AN UNTRUSTED NETWORK!

For example, if you try to make a request without supplying HTTP Basic authentiction credentials (i.e., a username and password), your request will be rejected with an HTTP 401 error:

    curl -i 'http://192.168.1.180' 
    HTTP/1.1 401 Unauthorized
    Server: uhttpd/pre-0.1 (running in your devices)
    Content-Type: text/html
    www-authenticate: Basic realm=esp8266
    
    <html><body><header>uhttpd/pre-0.1<hr></header>Unauthorized</body></html>

If you use a web browser to access this page, you should get a popup window prompting you for a username and password.

When you supply the correct credentials (e.g., via `curl`), you should be granted access to the requested URL:

    curl -i -u admin:uhttpD 'http://192.168.1.180' 
    HTTP/1.1 200 OK
    Server: uhttpd/pre-0.1 (running in your devices)
    Content-Length: 40
    Content-Type: text/html
    
    <html><body>Hello World!</body></html>

## Reference

The following sections describe the components that form the `uhttpd` package in more detail.

### `uhttpd.Server`

The `uhttpd.Server` is simply a container for helper instances.  Its only job is to accept connections from clients, to read and parse HTTP headers, and to read the body of the request, if present.  The server will the dispatch the request to the first handler that matches the path indicated in the HTTP request, and wait for a response.  Once received, the response will be sent back to the caller.

An instance of a `uhttpd.Server` is created using an ordered list of pairs, where the first element of the pair is a path prefix, and the second is a handler index.  When an HTTP request is processed, the server will select the handler that corresponds with the first path prefix which is a prefix of the path in the HTTP request.

For example, given the following construction:

    >>> import uhttpd
    >>> handler1 = ...
    >>> handler2 = ...
    >>> handler3 = ...
    >>> server = uhttpd.Server([
            ('/foo/', handler1),
            ('/gnu', handler2),
            ('/', handler3)
        ])
    >>> server.start()

a request of the form `http://host/foo/bar/` will be handled by `handler1`, whereas a request of the form `http://host/gnat/` will be handled by `handler3`.

Once started, the `uhttpd.Server` will listen asynchronously for connections.  While a connection is not being serviced, the application may proceed to do work (e.g., via the REPL).  Once a request is accepted, the entire request processing, including the time spent in the handlers, is synchronous.

A `uhttpd.Server` may be stopped via the `stop` method.

#### Configuration

The `uhttpd.Server` can be configured using the `config` parameter at construction time, which is dictionary of name-value pairs.  E.g.,

    server = uhttpd.Server([...], config={'port': 8080})

The valid entries for this configuration parameter are described in detail below.

##### `port`

This parameter denotes the TCP/IP port on which the `uhttpd` should listen.  The type of this paramter is `int`, and the default value is 80.

##### `require_auth`

This parameter indicates whether HTTP authentication is required.  The type of this parameter is boolean, and the default value is `False`.  If this parameter is set to `True`, all requests into this server instance require HTTP authentication headers, per RFC 7231.

##### `realm`

This parameter denotes the HTTP authorization realm in which users should be authenticated.  This realm is returned back to the HTTP client when authorization is required but not credentials are supported.  The type of this parameter is `string`.  The default realm is `esp8266`.

##### `user`

This parameter denotes the HTTP user name, which needs to be supplied by the user in an HTTP Basic authentication header, per RFC 7231.  The default user name is `admin`.

##### `password`

This parameter denotes the HTTP password, which needs to be supplied by the user in an HTTP Basic authentication header, per RFC 7231.  The default password is `uhttpD`.


### `http_file_handler.Handler`

The `http_file_handler.Handler` request handler is designed to service files on the ESP8266 file system, relative to a specified file system root path (e.g., `/www`).

This handler will display the contents of the path specified in the HTTP GET URL, relative to the specified root path.  If path refers to a file on the file system, the file contents are returned.  If the path refers to a directory, and the directory does not contain an `index.html` file, the directory contents are provided as a list of hyperlinks.  Otherwise, the request will result in a 404/Not Found HTTP error.

The default root path for the `http_file_handler.Handler` is `/www`.  For example, the following constructor will result in a file handler that expects HTTP artifacts to reside in the `/www` directory of the micropython file system:

    >>> import http_file_handler
    >>> file_handler = http_file_handler.Handler()

Once your handler is created, you can then provide it to the `uhttpd.Server` constructor, providing the path prefix used to locate the handler at request time:

    >>> import uhttpd
    >>> server = uhttpd.Server([
            ('/', file_handler)
        ])

> Important: The path prefix provided to the `uhttpd.Server` constructor is distinct from the root path provided to the `http_file_handler.Handler` constructor.  The former relates to the path specified in a given HTTP GET request and is used to pick out the handler to process the handler.  The latter is used to locate where, on the file system, to start looking for files and directories to serve.  If the root path is `/www` and the path in the HTTP request is `/foo/bar`, then the `http_file_handler.Handler` will look for `/www/foo/bar` on the micropython file system.

You may of course specify a root path other than `/www` through the `http_file_handler.Handler` constructor, but the directory must exist, or an error will occur at the time of construction. 

> Warning: If you specify the micropython file system root path (`/`) in the HTTP file handler constructor, you may expose sensitive security information, such as the Webrepl password, through the HTTP interface.  This behavior is strongly discouraged.

You may optionally specify the `block_size` as a parameter to the `http_file_handler.Handler` constructor.  This integer value (default: 1024) determines the size of the buffer to use when streaming a file back to the client.  Larger chunk sizes require more memory and may run into issues with memory.  Smaller chunk sizes may result in degradation in performance.

This handler only supports HTTP GET requests.  Any other HTTP request verb will be rejected.

This handler recognizes HTML (`text/html`), CSS (`text/css`), and Javascript (`text/javascript`) file endings, and will set the `content-type` header in the response, accordingly.  The `content-length` header will contain the length of the body.  Any file other than the above list of types is treated as `text/plain`

### `http_api_handler.Handler`

The `http_api_handler.Handler` request handler is designed to handle REST-ful API calls into the `uhttpd` server.  Currently, JSON is the only supported message binding for REST-ful API calls through this handler.

This handler should be initialized with an ordered list of tuples, mapping a list of API "components" to an API handler instance, which will be used to actually service the API request.  A component, in this sense, is a sequence of path elements

    >>> import http_api_handler
    >>> api1 = ...
    >>> api2 = ...
    >>> api3 = ...
    >>> api_handler = http_api_handler.Handler([
            (['foo'], api1),
            (['gnu'], api2),
            ([], api3),
       ])

You can then add the API handler to the `uhttpd.Server`, as we did above with the HTTP File Handler:

    >>> import uhttpd
    >>> server = uhttpd.Server([
            ('/api', api_handler),
            ('/', file_handler)
        ])

This way, any HTTP requests under `http://host/api` get directed to the HTTP API Handler, and everything else gets directed to the HTTP File Handler.

The HTTP API Handler, like the `uhttp.Server`, does not do much processing on the request, but instead uses the HTTP path to locate the first API Handler that matches the sequence of components provided in the constructor.  In the above example, a request to `http://host/api/foo/` would get processed by the `api1` handler (as would requests to `http://host/api/foo/bar`), whereas requests simply to `http://host/api/` would get procecced by the `api3` handler.

### `stats_api.Handler`

This package includes one HTTP API Handler instance, which can be used to retrieve runtime statistics from the ESP8266 device.  This API is largely for demonstration purposes, but it can also be used as part of an effort to build a Web UI to manage an ESP8266 device.

Here is a complete example of construction of a server using this handler:

    >>> import http_file_handler
    >>> file_handler = http_file_handler.Handler()
    >>> import stats_api
    >>> stats = stats_api.Handler()
    >>> import http_api_handler
    >>> api_handler = http_api_handler.Handler([
            (['stats'], stats)
        ])
    >>> import uhttpd
    >>> server = uhttpd.Server([
            ('/api', file_handler)
            ('/', file_handler)
        ])

Here is some sample output from curl:

    prompt$ curl -s 'http://192.168.1.180/api/stats' | python -m json.tool
    {
        "esp": {
            "flash_id": 1327328,
            "flash_size": 1048576,
            "free_mem": 8288
        },
        "gc": {
            "mem_alloc": 29952,
            "mem_free": 6336
        },
        "machine": {
            "freq": 80000000,
            "unique_id": "0xBBB81500"
        },
        "network": {
            "ap": {
                "config": {
                    "authmode": "AUTH_WPA_WPA2_PSK",
                    "channel": 11,
                    "essid": "MicroPython-80d271",
                    "hidden": false,
                    "mac": "0x5ecf7f15b8bb"
                },
                "ifconfig": {
                    "dns": "192.168.1.1",
                    "gateway": "192.168.4.1",
                    "ip": "192.168.4.1",
                    "subnet": "255.255.255.0"
                },
                "status": "Unknown wlan status: -1"
            },
            "phy_mode": "MODE_11N",
            "sta": {
                "ifconfig": {
                    "dns": "192.168.1.1",
                    "gateway": "192.168.1.1",
                    "ip": "192.168.1.180",
                    "subnet": "255.255.255.0"
                },
                "status": "STAT_GOT_IP"
            }
        },
        "sys": {
            "byteorder": "little",
            "implementation": {
                "name": "micropython",
                "version": [
                    1,
                    8,
                    6
                ]
            },
            "maxsize": 2147483647,
            "modules": [
                "stats_api",
                "flashbdev",
                "console_sink",
                "webrepl_cfg",
                "uhttpd",
                "webrepl",
                "http_api_handler",
                "ulog",
                "websocket_helper"
            ],
            "path": [
                "",
                "/lib",
                "/"
            ],
            "platform": "esp8266",
            "version": "3.4.0",
            "vfs": {
                "bavail": 78,
                "blocks": 101,
                "frsize": 4096
            }
        }
    }
