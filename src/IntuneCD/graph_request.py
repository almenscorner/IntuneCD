import requests
import json
import time

def makeapirequest(endpoint,token,q_param=None):

    headers = {'Content-Type':'application/json', \
    'Authorization':'Bearer {0}'.format(token['accessToken'])}
    
    if q_param != None:
        response = requests.get(endpoint,headers=headers,params=q_param)
        if response.status_code == 504 or response.status_code == 502:
            print('Ran into issues with Graph request, waiting 5 seconds and trying again...')
            time.sleep(5)
            response = requests.get(endpoint,headers=headers)
    else:
        response = requests.get(endpoint,headers=headers)
        if response.status_code == 504 or response.status_code == 502:
            print('Ran into issues with Graph request, waiting 5 seconds and trying again...')
            time.sleep(5)
            response = requests.get(endpoint,headers=headers)
    if response.status_code == 200:
        json_data = json.loads(response.text)

        if '@odata.nextLink' in json_data.keys():
            record = makeapirequest(json_data['@odata.nextLink'],token)
            entries = len(record['value'])
            count = 0
            while count < entries:
                json_data['value'].append(record['value'][count])
                count += 1
        return(json_data)
    elif response.status_code == 404:
        print("Resource not found in Microsoft Graph: " + endpoint)
    elif (("assignmentFilters" in endpoint) and ("FeatureNotEnabled" in response.text)):
        print("Assignment filters not enabled in tenant, skipping")
    else:
        raise Exception('Request failed with ',response.status_code,' - ',
            response.text)

def makeapirequestPatch(patchEndpoint,token,q_param=None,jdata=None,status_code=200):

    headers = {'Content-Type':'application/json', \
    'Authorization':'Bearer {0}'.format(token['accessToken'])}
    
    if q_param != None:
        response = requests.patch(patchEndpoint,headers=headers,params=q_param,data=jdata)
    else:
        response = requests.patch(patchEndpoint,headers=headers,data=jdata)
    if response.status_code == status_code:
        pass
    else:
        raise Exception('Request failed with ',response.status_code,' - ',
            response.text)

def makeapirequestPost(patchEndpoint,token,q_param=None,jdata=None,status_code=200):

    headers = {'Content-Type':'application/json', \
    'Authorization':'Bearer {0}'.format(token['accessToken'])}
    
    if q_param != None:
        response = requests.post(patchEndpoint,headers=headers,params=q_param,data=jdata)
    else:
        response = requests.post(patchEndpoint,headers=headers,data=jdata)
    if response.status_code == status_code:
        if response.text:
            json_data = json.loads(response.text)
            return json_data
        else:
            pass
    else:
        raise Exception('Request failed with ',response.status_code,' - ',
            response.text)

def makeapirequestPut(patchEndpoint,token,q_param=None,jdata=None,status_code=200):

    headers = {'Content-Type':'application/json', \
    'Authorization':'Bearer {0}'.format(token['accessToken'])}
    
    if q_param != None:
        response = requests.put(patchEndpoint,headers=headers,params=q_param,data=jdata)
    else:
        response = requests.put(patchEndpoint,headers=headers,data=jdata)
    if response.status_code == status_code:
        pass
    else:
        raise Exception('Request failed with ',response.status_code,' - ',
            response.text)