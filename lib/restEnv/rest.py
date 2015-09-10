'''
@copyright: Hewlett Packard
This are simple libraries which will send the following REST calls:
POST
PUT
DELETE
GET
They all have the signature of  "RestCall(url,data,XAuthToken,debug=False,errorList=[])
where url is the url the call will be sent to. dat is the data contained in the request, and xAuthToken is the string
which will be used for the "X-Auth-Token" part of the header.
debug is a boolean which can be used to print to the system console the data which will be sent.
errorList is a string which will be used to return any error found while making the call.

If the call is succesful the return json object will be returned as a dictionary.
If an error occur the return value will be None (null) and the error text will be copied to the errorString variable
'''

import urllib
import httplib
import json

def genericREST(method,ip,url,data,debug=False):
    '''sends a json request using the selected method: method and using X-auth-Token: xAuthToken, and data as the body
    if the post attempt fails "None" (null) will be returned and the text of the error
    will be appended to errorLit[].
    If the post attempt is successful the json response will be returned as a dictionary
    If debug= true, then the url and data will be printed to the system screen.
    '''

    if debug == True:
        debugLabel = "_"+method+"-REST: "
        print ""
        print debugLabel+ "ip:          "  + str(ip)
        print debugLabel+ "url:          " + str(url)
        print debugLabel+ "data:         " + str(data)
        print ""
    server_port = 8091
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    json_data = json.dumps(data)
    try:
        conn = httplib.HTTPConnection(ip, server_port)
    except Exception as e:
        print e
        return {"response":e, "data":None}
    try:
        conn.request(method, url,json_data, headers)
        response = conn.getresponse()
        res_data = response.read()
        conn.close()
        return {"response":response, "data":res_data}
    except Exception as e:
        print e
        conn.close()
        return {"response":e, "data":None}


def post(ip, url, data, debug=False):
    return genericREST("POST", ip, url, data, debug)

def put(ip, url, data, debug=False):
    return genericREST("PUT", ip, url, data, debug)

def delete(ip, url, data, debug=False):
    return genericREST("DELETE", ip, url, data, debug)

def get(ip, url, debug=False):
    return genericREST("GET", ip, url, None, debug)

def head(ip, url, debug=False):
    return genericREST("HEAD", ip, url,None, debug)
