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
    if str_valid_command_return in html_content:
        selector_tags = soup.select(bs4_selector)
        if selector_tags and len(selector_tags)>0:
            print(f"{selector_tags[0].get_text().strip()}")
            if len(selector_tags)>1:
                print(f"->Selector {bs4_selector} returned multiple lines, concider choosing a more discriminating selector to retuen only one result.")
        else:
            print("Success: No valid tag found.")
        
    elif str_wrong_command_return in html_content:
       print("Command forbidden")

def main(url, str_valid_command_return, str_wrong_command_return,bs4_selector="html"):
    """
    Main function to handle user input and process commands.
    """
    command_history = []
    command_index = 0
    
    # Parameters to process cmd returns
    str_valid_command_return=str_valid_command_return
    str_wrong_command_return=str_wrong_command_return
    bs4_selector=bs4_selector




    while True:
        try:
            # Display the prompt
            command = input(f"command [{url}]: ")


            # Exit condition
            if command.lower() == "exit":
                break

            # Add command to history
            if command_index < len(command_history):
                command_history = command_history[:command_index]
                command_history.append(command)
                command_index = len(command_history)

            # Execute the command
            http_response, html_content = execute_command(url, data={"command": command})

            if html_content:
                
                extract_result_from_command_return(html_content, str_valid_command_return, str_wrong_command_return,bs4_selector)
                soup = BeautifulSoup(html_content, 'html.parser')
            else:
                print("Command processed, but no specific condition met.")

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    str_valid_command_return="blue_boy_typing_nothought.gif"
    str_wrong_command_return="Are you a hacker?"
    bs4_selector='h2'

    url = input("Enter the URL:")
    main(url, str_valid_command_return, str_wrong_command_return, bs4_selector)
