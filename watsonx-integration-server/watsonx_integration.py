import oracledb
import json
import requests
import sys
import os
import re
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from utils import *


from dotenv import load_dotenv
import configparser

def watsonx_integrate(user_query):
    #Debug ON and OFF 
    DEBUG =1 
    os.chdir('../watsonx-integration-server')
    url=readllmconfig()
    API_KEY=getapikey()
    if DEBUG==1:
        print(f'User query: \n {user_query}')
    load_dotenv()
    AUTHENTICATION_TOKEN = os.getenv("WATSONX_ACCESS_TOKEN")
    

    body_file = "llm_params_config.json"
    try:
        with open(body_file, "r") as file:
            body = json.load(file)
    except FileNotFoundError:
        raise Exception(f"Configuration file {body_file} not found.")
    except json.JSONDecodeError as e:
        raise Exception(f"Error decoding JSON in {body_file}: {e}")
    # Replace the {user_query} placeholder in the input
    body["input"] = body["input"].replace("{user_query}", user_query)

    #NLP2SQL 
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTHENTICATION_TOKEN}"
    }
    response = requests.post(url[0],headers=headers,json=body)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))
    
    data = response.json()
    if DEBUG==1: 
        print(f'Response from WatsonX::\n {data}')
    sql_resp = data['results']


    QUERY = sql_resp[0]['generated_text'].split(';')[0]
    SQL_QUERY = QUERY +" "
    if DEBUG==1:
        print(f"\nWatsonX generated SQL:: {SQL_QUERY}")
    JSON_SQL_QUERY = "select JSON_OBJECT(*) from (" + SQL_QUERY + ")"
    if DEBUG==1:
        print(f'Updated SQL : {JSON_SQL_QUERY}')
    
    ############ 2 Execute DB - by calling agent 
    # NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account (https://eu-de.dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/ml-authentication.html?context=wx)
    #API_KEY = "DBJXI9hqQJ9YVCrY4oZXt0AQt3uAy2-2RfeciTHB_Dkc"
    print("2 Execute DB - by calling agent")
    token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
    mltoken = token_response.json()["access_token"]

    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

    # NOTE:  manually define and pass the array(s) of values to be scored in the next line
    payload_scoring = {"messages":[{"content":SQL_QUERY,"role":"user"}]}
    
    start_time = time.perf_counter()
    response_scoring = requests.post(url[1], json=payload_scoring,headers={'Authorization': 'Bearer ' + mltoken}, stream=False)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print("Elapsed time :",elapsed_time)

    if DEBUG==1:
        print("Scoring response:")
    try:
        result=response_scoring.json()
    except ValueError:
        print(response_scoring.text)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    if DEBUG==1:
        print("Original result :\n")
        print(result)
    data = parseagentdata(result)
    if DEBUG==1:
        print("\n finished parsing data: \n\n")
        print(data)

    #Remove PII
    #clean_data=remove_pii_data(data, pii_keys=None)
    #if DEBUG==1:
    #    print("Clean Data:\n\n",clean_data) 

    
    #############
    # 3 PRovide Insights
    body = readllmparams('llm_params_config_2.json',data)
    headers = {"Accept": "application/json","Content-Type": "application/json","Authorization": f"Bearer {AUTHENTICATION_TOKEN}"}

    response = requests.post(url[2],headers=headers,json=body)
    if response.status_code != 200:
        print("Error in response")
        raise Exception("Non-200 response: " + str(response.text))

    insights = response.json()
    if DEBUG==1:
        print("INSIGHTS")
        print(insights)
    
    return data,insights 
