"""
 BBIOServer - v1.2
 Copyright 2012 Alexander Hiam
 A dynamic web interface library for PyBBIO.
"""

"""
Extended by Junaid Malik for use in web interface development
for use in Kovsky Cricket Bowling Machine.
"""

import os, sys, urlparse, traceback
from multiprocessing import Process
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

from bbio import *
from SafeProcess import *

BBIOSERVER_VERSION = "1.2"

THIS_DIR = os.path.dirname(__file__)
PAGES_DIR = "%s/pages" % THIS_DIR
HEADER = "%s/src/header.html" % THIS_DIR
SIDEBAR = "%s/src/sidebar.html" % THIS_DIR
FOOTER = "%s/src/footer.html" % THIS_DIR
IMAGES = "../images/" 
INDEX_TEMPLATE = "%s/src/index.html.template" % THIS_DIR
INDEX = "%s/index.html" % THIS_DIR


# Change working directory to the BBIOServer library directory,
# otherwise the request handler will try to deliver pages from the
# directory where the program using the library is being run from:
os.chdir(THIS_DIR)

# This is where we store the function strings indexed by their
# unique ids:
FUNCTIONS = {}


class BBIORequestHandler(SimpleHTTPRequestHandler):

  def do_GET(self):
    """ Overrides SimpleHTTPRequestHandler.do_GET() to handle
        PyBBIO function calls. """
    url = self.raw_requestline.split(' ')[1]
    if ('?' in url):
      # We've received a request for a PyBBIO function call,
      # parse out parameters:
      url = url.split('?')[1]
      params = urlparse.parse_qs(url)
      function_id = params['function_id'][0]
      
      function = FUNCTIONS.get(function_id)
      if (function):
        if ("entry_text" in params):
          # This is a request from a text entry, so we also need to
          # parse out the text to be passed to the function:
          text = params['entry_text'][0]
          if (text == " "):
            # An empty text box is converted into a space character
            # by the Javascript, because otherwise the parsed url
            # would not have an entry_text param and we'd get errors
            # trying to call the function; convert it back:
            text = "" 

          response = str(function(text))
	
	elif ("bowl" in params):
	  spin = '%s' %  params['spin'][0]
	  speed = '%s' % params['speed'][0]
	  pitchspot = '%s' % params['pitchspot'][0]
          response = str(function(spin,speed,pitchspot))

        else:
          # The function takes no arguments, just call it.
          response = str(function())

      else:
        # The function id is not in the dictionary. This happens if
        # the server has restarted, which generates new function ids, 
        # and the page has not been refreshed.
        response = "*Refresh page*"

      # Send the HTTP headers:
      self.send_response(200)
      self.send_header('Content-Type', 'text/html')
      # Our length is simply the length of our function return value:
      self.send_header("Content-length", len(response))
      self.send_header('Server', 'PyBBIO Server')
      self.end_headers()

      # And finally we write the response:
      self.wfile.write(response)
      return

    # If we get here there's no function id in the request, which
    # means it's a normal page request; let SimpleHTTPRequestHandler
    # handle it the standard way:
    SimpleHTTPRequestHandler.do_GET(self)
    

class BBIOHTTPServer(HTTPServer):

  def handle_error(self, request, client_address):
    """ Overrides HTTPServer.handle_error(). """
    # Sometimes when refreshing or navigating away from pages with
    # monitor divs, a Broken pipe exception is thrown on the socket
    # level. By overriding handle_error() we are able to ignore these:
    error = traceback.format_exc()
    if ("Broken pipe" in error):
      return

    # Otherwise we want to print the error like normal, except that,
    # because BBIOServer redirects stderr by default, we want it to
    # print to stdout:
    traceback.print_exc(file=sys.stdout)
    print '-'*40
    print 'Exception happened during processing of request from',
    print client_address    
    print '-'*40


class RequestFilter():
  # This acts as a file object, but it doesn't print any messages
  # from the server.
  def write(self, err):
    if not (('GET' in err) or ('404' in err)):
      print err
  def flush(self):
    pass

class BBIOServer():
  def __init__(self, port=8000, verbose=False, blocking=True):
    self._server = BBIOHTTPServer(('',port), BBIORequestHandler)
    self.blocking = blocking
    if not(verbose):
      # A log of every request to the server is written to stderr.
      # This makes for a lot of printing when using the monitors. 
      # We can avoid this by redirecting stderr to a RequestFilter() 
      # instance:
      sys.stderr = RequestFilter()

  def start(self, *pages):
    """ Takes a list of Page instances, creates html files, and starts
        the server. """

    # Make sure at least one page has been given:
    if not(pages):
      print "*Can't start server - no pages provided."
      return

    # Make sure pages/ directory exists:
    if not(os.path.exists(PAGES_DIR)):
      os.system("mkdir %s" % PAGES_DIR)
    # Remove old pages if any:
    if (os.listdir(PAGES_DIR)):
      os.system("rm %s/*" % PAGES_DIR)
    
    # We treat the first page passed in as the home page and create
    # an index.html page in the base directory that redirects to it:
    home = pages[0]
    with open(INDEX, 'w') as index:
      with open(INDEX_TEMPLATE, 'r') as index_template:
        index.write(index_template.read() % home.filename)

    # Generate a list of links for the sidebar:
    links = ''
    for page in pages:
      links += '<li><a href="%s">%s</a></li>\n' % (page.filename, page.title)

    # Add sidebar to each page and write them to files:
    #for page in pages:
      path =  "%s/%s" % (PAGES_DIR, page.filename)
      with open(path, 'w') as f:
        f.write(str(page) % links)

    # The server is started as a subprocess using PyBBIO's SafeProcess. 
    # This way it will be non-blocking and stop automatically during
    # PyBBIO's cleanup routine.
    self._server_process = SafeProcess(target=self._server.serve_forever)
    self._server_process.start()

    if (self.blocking):
      try:
        while(True): delay(10000)
      except KeyboardInterrupt:
        pass
    

  def stop(self):
    self._server_process.terminate()


class Page(object):
  def __init__(self, title, stylesheet="style.css"):
    self.title = title
    # Convert the title to a valid .html filename:
    not_allowed = " \"';:,.<>/\|?!@#$%^&*()+="
    self.filename = ''
    for c in title: 
      self.filename += '' if c in not_allowed else c
    self.filename += ".html" 
   
    # The header template has three string formatting operators:
    # the document and page titles, and the sidebar. The sidebar
    # template has one formatting operator where the list of links
    # goes. When we insert the two titles and the sidebar content
    # into the header template, we end up with the one formatting
    # operator from the sidebar template. This way the BBIOServer
    # will be able to insert the links even though the pages are 
    # all created separately:
    self.html = open(HEADER, 'r').read() % \
                (title, stylesheet, title, open(SIDEBAR, 'r').read())
                #(title, stylesheet, title, open(SIDEBAR, 'r').read())

  def add_pitch(self):
    PITCH = "%s/src/pitch.html" % THIS_DIR
    self.html += open(PITCH,'r').read()
  
  def add_feed(self):
    FEED = "%s/src/feed.html" % THIS_DIR
    self.html += open(FEED,'r').read()

  def add_diag(self):
    DIAG = "%s/src/diag.html" % THIS_DIR
    self.html += open(DIAG,'r').read()

  def add_preloader_start(self):
    self.html += '<div id="preloader">'
    self.html += '<div class="alert alert-info" id="status1">'
  
  def add_preloader_end(self):
    self.html += '</div><div id="status"></div>'
    self.html += '</div>'
  
  def add_modal_launch(self):
    self.html += '<button href="#myModal" role="button" class="btn btn-success btn-large btn-block" data-toggle="modal">Launch live feed</button>'
 
  def add_diag_launch(self):
    self.html += '<button href="#diagTool" role="button" class="btn btn-success btn-large btn-block" data-toggle="modal">Woolmer Tool</button>' 
  
  def add_heading(self, text, cls="alert-info"):
    """ Add a heading to the current position in the page. """
    self.html += '<div class="alert %s pagination-centered"><h4>%s</h4></div>\n' % (cls,text)
  
  def add_label(self, text, cls="label-important"):
    """ Add a heading to the current position in the page. """
    self.html += '<span class="label %s pagination-centered">%s</span>\n' % (cls,text)  
    
  def start_div(self, cls): # Added by Junaid Malik
    """ Start a div with the provided class name. """
    self.html += '<div class="%s">' % (cls)

  def end_div(self):
    """ End a div """
    self.html += '</div>'

  def add_text(self, text, newline=False):
    """ Add text to the current position in the page. If newline=True
        the text will be put on a new line, otherwise it will be stacked
        on the current line. """
    style = "clear: left;" if newline else ''
    self.html += '<div class="text" style="%s">%s</div>\n' %\
                 (style, text)

  def add_textfield(self, id, classtext=False, readonly=False, newline=False): # Added by Junaid Malik
    """ Add a textfield to the current position with the given id and optional
	readonly parameter"""
    style = "clear:left;" if newline else ''
    
    self.html += '<div style="%s">\n' % (style)
    self.html += '<input type=text id="%s"' % (id)
    self.html += 'readonly="readonly"' if readonly else ''
    self.html += 'class="%s"' % classtext if classtext else 'class="entry"'
    self.html += ' />'
    self.html += '</div>'


  def add_image(self, filename="",id=str(int(time.time()*1e6) & 0xffff), newline=False, style="", path=""): # Added by Junaid Malik
    """ Add image to the current position in the page. If newline=True
        the text will be put on a new line, otherwise it will be stacked
        on the current line. """
    #style += "display:block; "
    style += "clear: left;" if newline else ''
    if (path == ""): path = "%s/%s" % (IMAGES,filename)
    self.html += '<img id="%s" style="%s" src="%s" />\n' %\
                 (id, style, path)

  def add_button(self, function, label, id=str(int(time.time()*1e6) & 0xffff), type="button", newline=False): # Modified by Junaid Malik
    """ Add a button to the current position in the page with the given
        label, which will execute the given lambda function, e.g.:
        'lambda: digitalWrite(USR3)'. If newline=True the text will be put
        on a new line, otherwise it will be stacked on the current line. """
    # Use system time to create a unique id for the given function.
    # This is used as a lookup value in the FUNCTION_STRINGS dictionary.
    function_id = str(int(time.time()*1e6) & 0xffff)
    FUNCTIONS[function_id] = function

    style = "clear: left;" if newline else ''

    # Add the HTML. Set the button to call the javascript function 
    # which communicates with the request handler, passing it the
    # function id and a string to indicate that it is a button:
    self.html +=\
      '<div class="object-wrapper" style="%s">\n' % (style) +\
      '<div class="button" id="%s" onclick="call_function(%s, \'%s\')">%s\n' %\
        (id, function_id, type, label) +\
     '</div>\n</div>\n'

  def add_custom_button(self, function, label, id=str(int(time.time()*1e6) & 0xffff), cls="", type="button", funcToCall="call_function", newline=False):
    """ Add a button to the current position in the page with the given
        label, which will execute the given lambda function, e.g.:
        'lambda: digitalWrite(USR3)'. If newline=True the text will be put
        on a new line, otherwise it will be stacked on the current line. """
    # Use system time to create a unique id for the given function.
    # This is used as a lookup value in the FUNCTION_STRINGS dictionary.
    function_id = str(int(time.time()*1e6) & 0xffff)
    FUNCTIONS[function_id] = function

    style = "clear: left;" if newline else ''

    # Add the HTML. Set the button to call the javascript function 
    # which communicates with the request handler, passing it the
    # function id and a string to indicate that it is a button:
    self.html +=\
      '<button class="btn %s" id="%s" onclick="%s(%s, \'%s\')">%s\n' %\
        (cls, id, funcToCall, function_id, type, label) +\
     '</button>'

  def add_entry(self, function, submit_label, newline=False):
    """ Add a text entry box and a submit button with the given label to the 
        current position in the page. When submitted, the given function will
        be called, passing it the text currently in the entry. The function 
        must take take a value, e.g.: 'lambda s: print s'. If newline=True 
        the text will be put on a new line, otherwise it will be stacked on
        the current line. """

    # Create the unique id and store the function:
    function_id = str(int(time.time()*1e6) & 0xffff)
    FUNCTIONS[function_id] = function

    style = "clear: left;" if newline else ''

    # Add the HTML. Pass the Javascript function the function id,
    # as well as a string to indicate it's an entry. This way the
    # Javascript function will know to extract the text from the 
    # entry and pass it as part of its request. 
    self.html +=\
      '<div class="object-wrapper" style="%s">\n' % (style) +\
      '<input class="entry" id="%s" type="text" name="entry" />\n' %\
      (function_id) +\
      '<div class="button" onclick="call_function(%s, \'entry\')">%s\n' % \
      (function_id, submit_label) +\
     '</div>\n</div>\n'

  def add_monitor(self, function, label, units='', newline=False):
    """ Add a monitor to the current position in the page. It will be
        displayed in the format: 'label' 'value' 'units', where value is 
        the most recent return value of the given function; will be 
        updated every 200 ms or so. If newline=True the text will be put
        on a new line, otherwise it will be stacked on the current line. """
    
    # Create the unique id and store the function:
    function_id = str(int(time.time()*1e6) & 0xffff)
    FUNCTIONS[function_id] = function

    style = "clear: left;" if newline else ''

    # Add the HTML. Set the monitor id as the function id. When
    # the page loads a Javascript function is called which continually
    # loops throught each monitor, extracts the id, passes it to the
    # server, then sets the text in the monitor div to the return
    # value.
    self.html +=\
      '<div class="object-wrapper" style="%s">\n' % (style) +\
      '<div class="value-field">%s</div>\n' % (label) +\
      '<div class="monitor-field" id="%s"></div>\n' % (function_id) +\
      '<div class="value-field">%s</div>\n' % (units) +\
      '</div>\n'

  def __str__(self):
    # Return the HTML with the content of the footer template
    # appended to it: 
    return self.html + open(FOOTER, 'r').read() % (BBIOSERVER_VERSION)
