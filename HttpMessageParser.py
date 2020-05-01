import re


class HttpMessageParser:
    def __init__(self,request):
        # Parse request.
        elements = request.split("\\r\\n")

        methods = elements[0].split()
        # Define method.
        self.method = methods[0].replace("b'","")
        # Define file name.
        p = re.compile('^[\/\w+]+\.\w+')
        self.filename = p.findall(methods[1])[0]
        # Define file type.
        fileparts = self.filename.split(".")
        if fileparts[1] == 'html':
            self.filetype = 'text/html'
            self.filereadmode = 'r'
                #break
        elif fileparts[1] == 'css':
            self.filetype = 'text/css'
            self.filereadmode = 'r'
                #break
        elif fileparts[1] == 'js':
            self.filereadmode = 'r'
            self.filetype = 'application/javascript'
                #break
        elif fileparts[1] == 'png':
            self.filetype = 'image/png'
            self.filereadmode = 'rb'
                #break
        elif fileparts[1] == 'ico':
            self.filetype = 'image/x-icon'
            self.filereadmode = 'rb'
        else:
            self.filetype = "text/html"  # Default filetype
            self.filereadmode = 'r'

        # Default connection is not keep-alive
        self.keepalive = False
        for elementindex in range(1, len(elements)):

            # Parse the element with format elementvalues index 0 is the type of the element.
            elementvalues = elements[elementindex].split()
            if len(elementvalues) > 0:
                if elementvalues[0] == "Connection:":
                    self.connection = elementvalues[1].replace("\r\n","")
                    # Only set the client keep alive if it is requested as keep alive and file type is html.
                    if str.lower(self.connection) == "keep-alive" and self.filetype == "text/html":
                        self.keepalive = True
                    else:
                        self.keepalive = False

    def parse_data(self):
        file_content = b''

        if self.method == 'HEAD':
            ret_message = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body>HEAD</body></html>\n'
        elif self.method == 'GET':
            content = self.get_file(self.filename, self.filereadmode)

            if self.keepalive:
                ret_message = 'HTTP/1.1 200 OK\r\nContent-Type: ' + self.filetype + '\r\nConnection: Keep-Alive\r\nContent-Length: ' + str(len(content)) + '\r\n\r\n'
            else:
                ret_message = 'HTTP/1.1 200 OK\r\nContent-Type: ' + self.filetype + '\r\nContent-Length: ' + str(len(content)) + '\r\n\r\n'

            # Change to bytes if the file content is string.
            if self.filereadmode == 'r':
                file_content = bytes(content, 'utf-8')
            else:
                file_content = content
        else:
            ret_message = 'HTTP/1.1 501 Not Implemented\n'

        return ret_message, file_content, self.keepalive

    def get_file(self, filename, mode):
        with open("html" + filename, mode) as f:
            data = f.read()

        return data





