import RestService
import pprint
import json
import argparse


def resttest():
    ip = args.ip
    url = args.url
    method = args.method
    inputData = args.inputData
    expectedData = args.expectedData
#    restResult = dict()
    rest_handle = RestService.RestService(switch_ip=ip)
    if method == "POST" or method == "PUT":
        with open('/root/restEnv/restdata', 'rb') as f:
            inputData = json.load(f)

#            inputData = f.read()
# print inputData
    if (method == "GET"):
        result = rest_handle.getResponse(url)
    elif (method == "POST"):
        result = rest_handle.postResponse(url, inputData)
    elif (method == "PUT"):
        result = rest_handle.putResponse(url, inputData)
    elif (method == "DELETE"):
        result = rest_handle.deleteResponse(url, inputData)
#    restResult['http_status'] = result[0]
#    restResult['data'] = result[1]
#    print(str(restResult))
    print(str(result[0]))
    print "\n"
    print(str(result[1]))
    # Command line argument parser
parser = argparse.ArgumentParser(description='OpenHalon environment test shell')
parser.add_argument('--ip', help="ip", required=True, dest='ip')
parser.add_argument('--url', help="url", required=True, dest='url', default=None)
parser.add_argument('--method',help="method GET/POST", required=True, dest='method', default=None)
parser.add_argument('--inputData',help="JSON input data", required=False, dest='inputData', default=None)
parser.add_argument('--expectedData',help="JSON output data", required=False, dest='expectedData', default=None)
args = parser.parse_args()
resttest()
