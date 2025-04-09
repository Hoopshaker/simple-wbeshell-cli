# Simple Webshell client
## Overview
This script provides a simple webshell client that interacts with a remote server to execute commands. It is designed to be agnostic of the specific Remote Code Execution (RCE) vulnerability, allowing users to execute commands without needing to upload a specific webshell.

## Features
- **Command Execution** : Execute commands on a remote server via HTTP requests.
- **Template Population**: Dynamically replace placeholders in request templates with command values.
- **Response Parsing**: Extract and process command results from HTML responses using BeautifulSoup and regular expressions.
- **Command History**: Maintain a history of executed commands for easy navigation.

## Requirements & installation
Python 3.x

It is recommanded to use a virtualenv https://virtualenv.pypa.io/en/latest/

Installation 
```
pip install -r requirements.txt
```

## Usage
### Command-Line Arguments
The script accepts several command-line arguments to configure its behavior:

- --url: The URL of the webshell.
- --method: The HTTP method to use (POST or GET).
- --selector: A CSS-like selector to extract the command result from the HTML response.
- --valid_cmd: A string to validate that the command was executed successfully.
- --wrong_cmd: A string indicating that something went wrong with the command execution.
- -H: Add a header to the request (can be specified multiple times).
- -D: Add a body parameter to the request (can be specified multiple times).
- -P: Add a query parameter to the request (can be specified multiple times).
- --regex: A regular expression to apply to the command result.
- --rm: A string to remove from the command result.
- --rm_after: Remove content after this string, including the string itself.
- --rm_before: Remove content before this string, including the string itself.

### Example
```
python webshell_client.py --url http://example.com/webshell --method POST --selector 'div.result' --valid_cmd 'Command executed' --wrong_cmd 'Error' -H "User-Agent=%%cmd%%" -D "command=%%cmd%%" -P "param=%%cmd%%" --regex "some_regex" --rm "remove_this" --rm_after "after_this" --rm_before "before_this"
```

## Disclaimer
This script is intended for educational and ethical hacking purposes only. Unauthorized access to computer systems is illegal and unethical. Always obtain permission before testing or accessing any system.
