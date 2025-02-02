import React, { useState, useEffect } from "react";
import { ArrowRight, X, MessageCircle } from "lucide-react";
import axios from "axios";
import "./Chatbot.css";

// Create axios instance with default config
const api = axios.create({
  baseURL: 'http://localhost:5001',  // Default port
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});


export default function Chatbot() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! How can I help you with college events today?", isUser: false }
  ]);
  const [events, setEvents] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  // Modified to handle connection errors
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await api.get("/query?q=upcoming%20events");
        const eventList = response.data.response.split("\n").map((event, index) => ({
          id: index + 1,
          text: event,
          isUser: false
        }));
        setEvents(eventList);
      } catch (error) {
        console.error("Error fetching events:", error);
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          text: "Unable to connect to the server. Please make sure the backend is running.",
          isUser: false
        }]);
      }
    };

    fetchEvents();
  }, []);

  const handleQuery = async () => {
    if (!query.trim()) return;

    // Add user message immediately
    setMessages(prev => [...prev, { 
      id: prev.length + 1, 
      text: query, 
      isUser: true 
    }]);

    try {
      const response = await api.get(`/query?q=${encodeURIComponent(query)}`);
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        text: response.data.response,
        isUser: false
      }]);
    } catch (error) {
      console.error("Error processing query:", error);
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        text: "Error connecting to server. Please check if the backend is running on port 5001.",
        isUser: false
      }]);
    }

    setQuery("");
  };

  const handleAPIError = async (error) => {
    if (error.code === 'ERR_CONNECTION_REFUSED') {
      // Try alternative ports
      const ports = [5001, 5002, 5003, 5004, 5005];
      for (const port of ports) {
        try {
          const response = await axios.get(`http://localhost:${port}/test`);
          if (response.data.status === "Server is running!") {
            api.defaults.baseURL = `http://localhost:${port}`;
            return true;
          }
        } catch (e) {
          continue;
        }
      }
    }
    return false;
  };

  return (
    <div className="fixed bottom-4 right-4">
      {isOpen ? (
        <div className="w-80 bg-white shadow-lg rounded-lg">
          <div className="bg-blue-600 p-4 flex justify-between items-center rounded-t-lg">
            <h2 className="text-white">Event Chatbot</h2>
            <button onClick={() => setIsOpen(false)} className="text-white hover:bg-blue-700">
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="p-4 h-96 overflow-y-auto">
            {messages.map(message => (
              <div key={message.id} className={`mb-2 ${message.isUser ? "text-right" : "text-left"}`}>
                <div className={`inline-block p-3 rounded-lg max-w-xs ${message.isUser ? "bg-blue-500 text-white" : "bg-gray-200"}`}>
                  {message.text}
                </div>
              </div>
            ))}
          </div>
          <div className="p-4 bg-gray-100 border-t">
            <div className="flex">
              <input
                type="text"
                placeholder="Type a message..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1 p-2 border rounded"
                onKeyPress={(e) => e.key === "Enter" && handleQuery()}
              />
              <button onClick={handleQuery} className="bg-blue-600 hover:bg-blue-700 p-2 rounded ml-2">
                <ArrowRight className="h-4 w-4 text-white" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setIsOpen(true)}
          className="p-3 bg-blue-600 hover:bg-blue-700 rounded-full shadow-lg"
        >
          <MessageCircle className="h-6 w-6 text-white" />
        </button>
      )}
    </div>
  );
}