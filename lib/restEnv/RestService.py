import json
import rest
import urllib2

class RestService(object):
    '''
    This is the main class for Halon FW REST API library.
    Usage:
    1. Import RestService
    2. Create object of the RestLib class (Optionall one can pass ip, user and password).
    3. Import relevant classes (datapath, aprs, stats...) from features.
    4. Make relevant calls:
        A>
            (code, val) = <class_name>.<method_name>(hpclib_object,...OTHER_PARAMS...)
            code: It is the HTTP response code.
            val : It has json object representing response or error message if req. fails
        B>
            call custom functions // These are found towards end of the file
            count = <class_name>.<method_name>(hpclib_object)
    '''

    def __init__(self, switch_ip='localhost', user='sdn', password='skyline'):
        self.switch_ip = switch_ip
        self.user = user
        self.password=password
        self.url = 'https://'+switch_ip+':8091/system'
        self.token = None
        self.verbose = False


    def setVerbose(self):
        '''
        setVerbose:
        API to set verbosity level for the session.
        No Arguments, sets self.verbose.
        '''
        self.verbose = True

    def clearVerbose(self):
        '''
        clearVerbose:
        API to clear verbosity level for the session.
        No Arguments, clears self.verbose.
        '''
        self.verbose = False

    def setURL(self, url):
        '''
        setURL:
        API to set base URL for the controller.
        No Arguments, sets self.url.
        '''
        self.url = url

##########################
# Generic GET
##########################
    def getResponse(self, reqURL):
        '''
        getResponse:
        API to make REST GET request.
        Takes URL, returns (code, value) pair.
            code: HTTP response core or 555 (for other errors)
            value: JSON response object of error string.
        '''
        if self.verbose:
            print 'Req URL: ', reqURL
        res = rest.get(self.switch_ip, reqURL, self.verbose)
        if isinstance(res["response"], urllib2.URLError):
            return (555, res.reason)
        else:
            try:
                return (res["response"].status, res["data"])
            except:
                return (res["response"].status, res["response"].reason)


##########################
# Generic POST
##########################
    def postResponse(self, reqURL, data):
        '''
        postResponse:
        API to make REST POST request.
        Takes URL, and data (generally a json string).
        Returns (code, value) pair.
            code: HTTP response core or 555 (for other errors)
            value: JSON response object of error string.
        '''
        if self.verbose:
            print 'Req URL: ', reqURL
        res = rest.post(self.switch_ip, reqURL, data, self.verbose)
        if isinstance(res, urllib2.URLError):
            return (555, res.reason)
        else:
            try:
                return (res["response"].status, res["data"])
            except:
                return (res["response"].status, res["response"].reason)

##########################
# Generic PUT
##########################
    def putResponse(self, reqURL, data):
        '''
        putResponse:
        API to make REST PUT request.
        Takes URL, and data (generally a json string).
        Returns (code, value) pair.
            code: HTTP response core or 555 (for other errors)
            value: JSON response object of error string.
        '''
        if self.verbose:
            print 'Req URL: ', reqURL
        res = rest.put(self.switch_ip, reqURL, data, self.verbose)
        if isinstance(res, urllib2.URLError):
            return (555, res.reason)
        else:
            try:
                return (res["response"].status, res["data"])
            except:
                return (res["response"].status, res["response"].reason)

##########################
# Generic DELETE
##########################
    def deleteResponse(self, reqURL, data):
        '''
        daleteResponse:
        API to make REST DELETE request.
        Takes URL, and data (generally a json string on None).
        Returns (code, value) pair.
            code: HTTP response core or 555 (for other errors)
            value: JSON response object of error string.
        '''
        if self.verbose:
            print 'Req URL: ', reqURL
        res = rest.delete(self.switch_ip,reqURL, data,self.verbose)
        if isinstance(res, urllib2.URLError):
            return (555, res.reason)
        else:
            try:
                return (res["response"].status, res["data"])
            except:
                return (res["response"].status, res["response"].reason)
