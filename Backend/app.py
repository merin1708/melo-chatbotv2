import os
import logging
from flask import Flask, jsonify, request
import google.generativeai as genai
from flask_cors import CORS
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('flask_app.log')
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Get API key with better error handling
try:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=GOOGLE_API_KEY)
    logger.info("Successfully configured Gemini API")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


# Event data
event_data = [
    {"Event Name": "Tedx event", "Event Date": "Feb 22, 2025", "Venue": "", "Club Name": "TEDX", "Google Form Link": "https://bit.ly/TedxAtMace", "Deadline": "05-02-25"},
    {"Event Name": "Hackify", "Event Date": "28,1,2 March", "Venue": "", "Club Name": "IEDC", "Google Form Link": "https://hackify.iedcmace.in", "Deadline": "15-02-25"},
    {"Event Name": "Magazine Release", "Event Date": "Feb 5", "Venue": "", "Club Name": "Union", "Google Form Link": "", "Deadline": ""}
]

# Test endpoint to verify server is running
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "Server is running!", "message": "If you see this, the server is working correctly"})

# Error handling for all routes
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"An error occurred: {str(error)}")
    return jsonify({"error": str(error)}), 500

# API Endpoint to get event details with error handling
@app.route('/event_info', methods=['GET'])
def fetch_event_info():
    try:
        event_name = request.args.get('event', '').strip()
        if not event_name:
            return jsonify({"response": "Please provide an event name."})

        for event in event_data:
            if event_name.lower() in event["Event Name"].lower():
                event_details = (f"Event: {event['Event Name']}\n"
                               f"Date: {event['Event Date']}\n"
                               f"Club: {event['Club Name']}\n"
                               f"Google Form: {event.get('Google Form Link', 'N/A')}\n"
                               f"Deadline: {event.get('Deadline', 'N/A')}")
                return jsonify({"response": event_details})

        return jsonify({"response": "Sorry, I couldn't find any event matching your request."})
    except Exception as e:
        logger.error(f"Error in fetch_event_info: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# API Endpoint for chatbot queries with error handling
@app.route('/query', methods=['GET'])
def query_chatbot():
    try:
        user_query = request.args.get("q", "").lower()
        if not user_query:
            return jsonify({"response": "Please provide a query."})

        if "upcoming events" in user_query:
            upcoming_events = "\n".join([f"{event['Event Name']} on {event['Event Date']} (Club: {event['Club Name']})"
                                       for event in event_data])
            return jsonify({"response": upcoming_events})

        # For other queries, use Gemini if available
        if 'genai' in globals():
            response = query_gemini(user_query)
            return jsonify({"response": response})
        else:
            return jsonify({"response": "AI service is currently unavailable. Please try asking about events instead."})
            
    except Exception as e:
        logger.error(f"Error in query_chatbot: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def query_gemini(query):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat = model.start_chat(history=[])
        response = chat.send_message(query, stream=False)
        return response.text
    except Exception as e:
        logger.error(f"Error while calling Gemini API: {str(e)}")
        return "Sorry, I encountered an issue processing your request."
    
def find_free_port(start_port, max_attempts=10):
    """Find a free port starting from start_port"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            continue
    return None


if __name__ == "__main__":
    try:
        # Try to find a free port starting from 5001
        port = find_free_port(5001)
        if port is None:
            logger.error("Could not find a free port. Please free up some ports and try again.")
            sys.exit(1)
            
        logger.info(f"Starting Flask server on http://localhost:{port}")
        
        # Disable reloader to prevent port conflicts
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)