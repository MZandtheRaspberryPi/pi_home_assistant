import datetime
import requests

IP_ADDRESS = "10.0.0.110"
PORT = 8080

# URL of the mjpg-streamer snapshot endpoint
ENDPOINT = f"http://{IP_ADDRESS}:{PORT}/?action=snapshot"

def take_snapshot(output_filename='snapshot.jpg'):
    try:
        # Send GET request to capture image
        response = requests.get(ENDPOINT, timeout=5)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Write the binary image content to file
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print(f"Snapshot saved to {output_filename}")
        else:
            print(f"Failed to get snapshot, status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    take_snapshot()