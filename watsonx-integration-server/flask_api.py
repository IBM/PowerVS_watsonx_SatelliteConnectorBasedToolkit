import json
import copy
import os
import sys
import configparser

from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response

from gevent.pywsgi import WSGIServer

from watsonx_integration  import watsonx_integrate 

app = Flask(__name__)

# Read the response data format by reading the resp_config.json file
with open('resp_config.json', 'r') as file:
    resp_data = json.load(file)

print(resp_data)

# GET routines
@app.route('/data', methods=['GET'])
def fetchResponse():
    resp_data_local = copy.deepcopy(resp_data);
    query = request.args.get('query')
    data,insights = watsonx_integrate(query)
    if resp_data_local.get("sections") and resp_data_local.get("sections")[0]["type"] == "text":
        insight_text = insights["results"][0]["generated_text"]
        resp_data_local["sections"][0]["data"] += "Here are the insights:\n" + insight_text
    # Add it to the sections list
    for row in data:
        resp_data_local["sections"][1]["data"].append(row);
   

    response = make_response(jsonify(resp_data_local))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

    #return jsonify(resp_data_local)

# GET routines
@app.route('/updatetoken', methods=['GET'])
def updateToken():
    os.system("""echo "WATSONX_ACCESS_TOKEN=`bash generatetoken.sh | cut -d',' -f1 | cut -d'"' -f4`" > .env""")

    import sys
    print("argv was",sys.argv)
    print("sys.executable was", sys.executable)
    print("restart now")

    os.execv(sys.executable, ['python3.11'] + sys.argv)

if __name__ == '__main__':
   os.system("""echo "WATSONX_ACCESS_TOKEN=`bash generatetoken.sh | cut -d',' -f1 | cut -d'"' -f4`" > .env""")
   
   #Read the port number from the config.ini
   config = configparser.ConfigParser()
   config.read('config.ini')

   # Access values
   port = config.getint('apiserver', 'port')   
   print(f'Starting API server on port',port)
   http_server = WSGIServer(('0.0.0.0', port), app)
   
   try:
      http_server.serve_forever()
   except Exception as e:
      print(f"Server stopped due to error: {e}") 
