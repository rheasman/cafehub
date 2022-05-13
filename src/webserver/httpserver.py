from functools import partial
import html
import http.server
import logging
import sys
import os
from os.path import (join, exists, abspath, isdir, split, splitdrive)
from os import getcwd, curdir, pardir, fstat
import threading
from urllib.parse import quote, unquote
from posixpath import normpath
from io import BytesIO
import re
import socket
import errno
from typing import BinaryIO, List, Optional

StrPath = str

# This file started its life as: https://gist.github.com/pankajp/280596a5dabaeeceaaaa
# Gist was for python 2.7 code.

DATA_DIR = getcwd()

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """ Handler to handle POST requests for actions.
    """

    def do_HEAD(self):
        """ Override do_HEAD to handle HTTP Range requests. """
        self.range_from, self.range_to = self._get_range_header()
        if self.range_from is None:
            # nothing to do here
            return http.server.SimpleHTTPRequestHandler.do_HEAD(self)
        print('range request', self.range_from, self.range_to)
        f = self.send_range_head()
        if f:
            f.close()

    def do_GET(self):
        """ Overridden to handle HTTP Range requests. """
        print("Handler path: %s" % (self.translate_path(self.path),))
        self.range_from, self.range_to = self._get_range_header()
        if self.range_from is None:
            # nothing to do here
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        print('range request', self.range_from, self.range_to)
        f = self.send_range_head()
        if f:
            self.copy_file_range(f, self.wfile)
            f.close()

    def copy_file_range(self, in_file : BinaryIO, out_file : BinaryIO) -> int:
        """
        Copy only the range in self.range_from/to.

        Returns number of bytes copied
        """
        if in_file is None:
            raise Exception("in_file is None")

        if self.range_from is None:
            raise Exception("range_from is None")

        if self.range_to is None:
            raise Exception("range_to is None")

        in_file.seek(self.range_from)
        # Add 1 because the range is inclusive
        bytes_to_copy = 1 + self.range_to - self.range_from
        buf_length = 64*1024
        bytes_copied = 0
        while bytes_copied < bytes_to_copy:
            read_buf = in_file.read(min(buf_length, bytes_to_copy-bytes_copied))
            if len(read_buf) == 0:
                break
            out_file.write(read_buf)
            bytes_copied += len(read_buf)
        return bytes_copied

    def send_range_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = join(path, index)
                if exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)

        if not exists(path) and path.endswith('/data'):
            # FIXME: Handle grits-like query with /data appended to path
            # stupid grits
            if exists(path[:-5]):
                path = path[:-5]

        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None

        if self.range_from is None:
            self.send_response(200)
        else:
            self.send_response(206)

        self.send_header("Content-type", ctype)
        fs = fstat(f.fileno())
        file_size = fs.st_size
        if self.range_from is not None:
            if self.range_to is None or self.range_to >= file_size:
                self.range_to = file_size-1
            self.send_header("Content-Range",
                             "bytes %d-%d/%d" % (self.range_from,
                                                 self.range_to,
                                                 file_size))
            # Add 1 because ranges are inclusive
            self.send_header("Content-Length", 
                             str(1 + self.range_to - self.range_from))
        else:
            self.send_header("Content-Length", str(file_size))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def _make_literal(self, lit : str) -> bytes:
        return lit.encode()

    def list_directory(self, path : StrPath):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = BytesIO()
        displaypath = html.escape(unquote(self.path))
        f.write(self._make_literal('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'))
        f.write(self._make_literal("<html>\n<title>Directory listing for %s</title>\n" % displaypath))
        f.write(self._make_literal("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath))
        f.write(self._make_literal("<hr>\n<ul>\n"))
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write(self._make_literal('<li><a href="%s">%s</a>\n' % (quote(linkname), html.escape(displayname))))
        f.write(self._make_literal("</ul>\n<hr>\n</body>\n</html>\n"))
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path : str):
        """ Override to handle redirects.
        """
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = normpath(unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = self.directory  # type: ignore
        for word in words:
            drive, word = splitdrive(word)
            head, word = split(word)
            if word in (curdir, pardir): continue
            path = join(path, word)
        return path

    # Private interface ######################################################

    def _get_range_header(self):
        """ Returns request Range start and end if specified.
        If Range header is not specified returns (None, None)
        """
        range_header = self.headers.get("Range")
        if range_header is None:
            return (None, None)
        if not range_header.startswith("bytes="):
            print("Not implemented: parsing header Range: %s" % range_header)
            return (None, None)
        regex = re.compile(r"^bytes=(\d+)\-(\d+)?")
        rangething = regex.search(range_header)
        if rangething:
            from_val = int(rangething.group(1))
            if rangething.group(2) is not None:
                return (from_val, int(rangething.group(2)))
            else:
                return (from_val, None)
        else:
            print('CANNOT PARSE RANGE HEADER:', range_header)
            return (None, None)

def getlocalip():
    """
    It is surprisingly difficult to get a list of network IPs for the current machine. A weird oversight in the python network APIs.

    This hack seems to be the only solution that actually works. It gets one IP, the IP of the default route.
    Without using a hack like this, you get back something epically useful like "127.0.0.1".
    
    See https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib/166589#166589 
    See https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib/28950776#28950776
    The connect on the socket is a no-op. UDP sockets don't have a connect.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError as e:
        logging.info("Exception while trying to determine IP address: %s" % (repr(e)))
        return "localhost"


def get_server(port : int = 8000, attempts : int = 0, serve_path : Optional[StrPath] = None) -> Optional[http.server.ThreadingHTTPServer]:
    Handler = partial(RequestHandler, directory=serve_path)
    while attempts >= 0:
        try:
            httpd = http.server.ThreadingHTTPServer(("", port), Handler)
            logging.info(f"HTTPServer: Local routable IP address is {getlocalip()}")
            logging.info(f"HTTPServer: Listening on {httpd.server_address[0]} : {httpd.server_port}")
            return httpd
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                attempts -= 1
                port += 1
            else:
                raise

class BackgroundThreadedHTTPServer():
    def __init__(self, port : int, attempts : int, path : str):
        self.Server = get_server(port, attempts, path)
        if self.Server:
            self.Thread = threading.Thread(target=self.Server.serve_forever, daemon=True)    

    def start(self):
        if self.Thread:
            self.Thread.start()

    def shutdown(self):
        if self.Server:
            self.Server.shutdown()


def main(args : Optional[List[str]] = None):
    if args is None:
        args = sys.argv[1:]

    serveport = 8000
    servepath = "./"
    if len(args) > 0:
        serveport = int(args[0])
    if len(args) > 1:
        servepath = abspath(args[1])

    httpd = get_server(port=serveport, serve_path=servepath)

    if httpd is not None:
        print("serving at port", serveport)
        httpd.serve_forever()

if __name__ == "__main__" :
    main()            