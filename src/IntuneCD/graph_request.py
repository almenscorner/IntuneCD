import requests
import json

def makeapirequest(endpoint,token,q_param=None):

    headers = {'Content-Type':'application/json', \
    'Authorization':'Bearer {0}'.format(token['accessToken'])}
    
    if q_param != None:
        response = requests.get(endpoint,headers=headers,params=q_param)
    else:
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