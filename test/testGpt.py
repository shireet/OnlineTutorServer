import requests

while True:
    # Get user input
    user_message = input("Enter your message (or type 'exit' to quit): ")

    # Exit the loop if the user types 'exit'
    if user_message.lower() == "exit":
        print("Exiting the program.")
        break

    # Prepare the payload
    payload = {
        "message": user_message
    }

    # Make the POST request
    try:
        result = requests.post("http://172.17.112.1:5001/message", json=payload)

        # Check the response
        if result.status_code == 200:
            print("Response from server:", result.json())
        else:
            print(f"Error: {result.status_code}, {result.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
