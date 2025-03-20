#! /usr/bin/python3
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
        logging.info(f"Received HTML content : {response.text}")

        # Return the HTTP status code and the content of the HTML response
        return response.status_code, response.text

    except requests.RequestException as e:
        # Log any errors that occur
        logging.error(f"An error occurred: {e}")
        raise

def main(url):
    """
    Main function to handle user input and process commands.
    """
    command_history = []
    command_index = 0

    while True:
        try:
            # Display the prompt
            command = input(f"command [{url}]: ")

            # Handle up arrow key for command history
            if command == "":
                if command_index > 0:
                    command_index -= 1
                    command = command_history[command_index]
                    print(f"command [{url}]: {command}")
                else:
                    continue

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
                soup = BeautifulSoup(html_content, 'html.parser')

                if "blue_boy_typing_nothought.gif" in html_content:
                    h2_tag = soup.find('h2')
                    if h2_tag:
                        print(f"{h2_tag.get_text()}")
                    else:
                        print("Success: No h2 tag found.")
                    
                elif "Are you a hacker?" in html_content:
                   print("Command forbidden")
                else:
                    print("Command processed, but no specific condition met.")

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    url = input("Enter the URL: ")
    main(url)

