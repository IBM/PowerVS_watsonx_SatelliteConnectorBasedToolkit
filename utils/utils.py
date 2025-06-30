
import re
import configparser
import json

def printinfo(text,debuglvl):
    if debuglvl in (1, 2):
        print(text)
    return

def readllmconfig():
    config = configparser.ConfigParser()
    config.read('config.ini')
    count= config['llminferences']['no_of_inferences']
    url = []
    for i in range(1,int(count)+1,1):
        element = "llmurl"+str(i)
        elementvar = "url"+str(i)
        value = config[element][elementvar]
        url.append(value)
    return url

def readllmparams(filename,user_query):
    body_file = filename
    try:
        with open(body_file, "r") as file:
            body = json.load(file)
    except FileNotFoundError:
        raise Exception(f"Configuration file {body_file} not found.")
    except json.JSONDecodeError as e:
        raise Exception(f"Error decoding JSON in {body_file}: {e}")
    # Replace the {user_query} placeholder in the input
    if isinstance(user_query, list):
        joined_query = "\n".join(str(item) for item in user_query)
        body["input"] = body["input"].replace("{user_query}", joined_query)
    elif isinstance(user_query, str):
        body["input"] = body["input"].replace("{user_query}", user_query)
    else:
        raise TypeError("user_query must be either a string or a list of strings.")    

    return body




def getapikey():
    config = configparser.ConfigParser()
    config.read('config.ini')
    apikey= config['apikey']['api_key']
    return apikey

# Define a function to try and cast values to int or keep as string
def smart_cast(value):
    value = value.strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
        return value  # datetime with time
    elif re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return f"{value}T00:00:00"  # date only
    elif value.isdigit():
        return int(value)
    return value

def parseagentdata(response):
    message = response['choices'][0]['message']['content']

    # Find the table part of the message
    table_match = re.search(r'\|(.+\|)+', message, re.DOTALL)
    if not table_match:
        #XYZ = extract_and_format_transactions(response)
        #XYZ = parse_user_data(response)
        #XYZ = ConvertOPformat(response)
        #raise ValueError("Table not found in the message.")
        return XYZ
    # Extract all lines that look like table rows
    lines = [line.strip() for line in message.splitlines() if line.strip().startswith('|')]

    # Extract headers and rows
    headers = [h.strip().lower() for h in lines[0].strip('|').split('|')]
    rows = [line.strip('|').split('|') for line in lines[2:] if line.count('|') == lines[0].count('|')]

    # Build the list of dicts
    parsed_data = []
    for row in rows:
        entry = dict(zip(headers, map(smart_cast, row)))
        # Optionally, convert all keys to snake_case
        entry = {k.lower().strip().replace(' ', '_'): v for k, v in entry.items()}
        parsed_data.append((entry,))

    # Output
    #for item in parsed_data:
    #    print(item)

    return parsed_data

import json
import re


import re
from datetime import datetime


def to_snake_case(key):
    return key.lower()

def extract_and_format_transactions(response):
    print(response['choices'][0]['message']['content'][:1000])
    response_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    json_blocks = re.findall(r"```json\s*(\[\s*{.*?}\s*])\s*```", response_text, re.DOTALL)
    
    if not json_blocks:
        raise ValueError("JSON array not found in message.")
    
    try:
        data = json.loads(json_blocks[0])
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")
    
    extracted = []
    for item in data:
        # Flatten the nested object (e.g., under "JSON_OBJECT(*)")
        if isinstance(item, dict) and len(item) == 1 and isinstance(next(iter(item.values())), dict):
            flat_item = next(iter(item.values()))
        else:
            flat_item = item
        extracted.append((flat_item,))
    
    return extracted



def parse_user_data(ABC):
    content = ABC['choices'][0]['message']['content']

    # Split content by numbered user sections (e.g., "1. ", "2. ")
    user_sections = re.split(r'\n\d+\.\s+\*\*User Details:\*\*\n', content)
    user_sections = [section.strip() for section in user_sections if section.strip()]

    parsed_users = []

    for section in user_sections:
        user_dict = {}

        # Extract key-value pairs (e.g., "**Username:** manuel")
        matches = re.findall(r'\*\*(.*?)\*\*:\s*(.+)', section)

        for key, value in matches:
            # Normalize key to uppercase with underscores
            norm_key = key.upper().replace(" ", "_").replace("-", "_")

            # Convert dates to ISO format if applicable
            try:
                date_obj = datetime.strptime(value.strip(), "%Y-%m-%d")
                value = date_obj.isoformat()
            except ValueError:
                # Leave other values as-is
                pass

            # Try converting to int if it’s an integer
            if value.isdigit():
                value = int(value)

            user_dict[norm_key] = value.strip()

        parsed_users.append((user_dict,))  # Wrap each dict in a tuple

    XYZ = tuple(parsed_users)
    return XYZ



def remove_pii(data, pii_keys=None):
    if pii_keys is None:
        pii_keys = ['username', 'date_of_birth', 'address', 'email','password', 'first_name', 'last_name']

    cleaned_data = []
    for record in data:
        filtered_record = {k: v for k, v in record.items() if k not in pii_keys}
        cleaned_data.append(filtered_record)

    return cleaned_data


def to_snake_case(text):
    return re.sub(r'\W+', '_', text.strip().lower())


def parse_markdown_table(response_json):
    # Step 1: Extract content
    text = response_json['choices'][0]['message']['content']

    printinfo("parse_markdown_table : text extracted from response: "+text+"\n",2)

    # Extract the first markdown table from the text
    match = re.search(r'((\|.+?\|\n)+)', text)
    if not match:
        return []
    else:
        printinfo("Extract the first markdown table from the text : No Match",2)

    table_text = match.group(1).strip()
    lines = [line.strip() for line in table_text.splitlines() if '|' in line]

    if len(lines) < 2:
        return []

    # Extract headers and convert to snake_case
    headers = [to_snake_case(h) for h in lines[0].strip('|').split('|')]

    # Skip separator line
    data_lines = lines[2:]

    result = []
    for line in data_lines:
        values = [v.strip() for v in line.strip('|').split('|')]
        if len(values) != len(headers):
            continue
        row = dict(zip(headers, values))
        # Convert numeric strings to int or float where appropriate
        for key, val in row.items():
            if re.match(r'^\d+$', val):
                row[key] = int(val)
            elif re.match(r'^\d+\.\d+$', val):
                row[key] = float(val)
        result.append((row,))

    return result

def ConvertOPformat(response_json):
    # Step 1: Extract content
    content = response_json['choices'][0]['message']['content']

    print("ConvertOPformat:content received : "+content)
    # Step 2: Split on double newlines to get individual blocks
    blocks = [block.strip() for block in content.strip().split("\n\n") if block.strip()]

    results = []

    # Step 3: Parse each block
    for block in blocks:
        lines = block.splitlines()
        record = {}
        for line in lines:
            match = re.match(r'- \*\*(.*?):\*\* (.*)', line.strip())
            if match:
                raw_key, raw_value = match.groups()

                # Normalize key: lower, replace spaces with underscores, strip special characters
                key = (
                    raw_key.strip()
                    .lower()
                    .replace(" ", "_")
                    .replace(":", "")
                    .replace("-", "_")
                )
                # Convert numeric types if possible
                if raw_value.isdigit():
                    value = int(raw_value)
                elif re.match(r'^\d+\.\d+$', raw_value):
                    value = float(raw_value)
                else:
                    value = raw_value

                record[key] = value

        if record:
            results.append(record)

    print("RESULTS")
    print(results)
    orows = []
    for row in results:
        r = row
        r = {k.lower(): v for k, v in r.items()}
        tt = ( r,)
        orows.append(tt)

    return orows,results



def remove_pii_data(data, pii_keys=None):
    if pii_keys is None:
        pii_keys = ['username', 'date_of_birth', 'dob', 'address', 'email', 'password', 'passwd', 'first_name', 'last_name','EmailAddress','transaction_id']

    cleaned_data = []
    for record_tuple in data:
        # Unpack the tuple to get the actual dictionary
        record = record_tuple[0]
        filtered_record = {k: v for k, v in record.items() if k not in pii_keys}
        cleaned_data.append(filtered_record)

    return cleaned_data
