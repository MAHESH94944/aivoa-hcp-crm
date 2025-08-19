import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  sendChatMessage,
  addMessage,
  fetchHistory,
  fetchSummary,
  fetchSuggestions,
} from '../features/interactions/interactionsSlice';
import { Bot, Send, User } from 'lucide-react';

const AIAssistant = () => {
  const dispatch = useDispatch();
  // --- THIS IS THE FIX ---
  // We now also select 'formData' from the Redux state
  const { status, messages, formData } = useSelector((state) => state.interactions);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;

    // Now 'formData' is defined and can be used to get the hcp_name
    const hcpName = formData.hcp_name;
    const lowerInput = input.toLowerCase();

    dispatch(addMessage({ sender: 'user', text: input }));

    // The command routing logic
    if (lowerInput.includes('history') || lowerInput.includes('records')) {
      if (!hcpName) {
        dispatch(addMessage({ sender: 'ai', text: "Please enter an HCP name in the form first to get their history." }));
      } else {
        dispatch(fetchHistory(hcpName));
      }
    } else if (lowerInput.includes('summary') || lowerInput.includes('summarize')) {
      if (!hcpName) {
        dispatch(addMessage({ sender: 'ai', text: "Please enter an HCP name in the form first to get a summary." }));
      } else {
        dispatch(fetchSummary(hcpName));
      }
    } else if (lowerInput.includes('suggestion') || lowerInput.includes('next step')) {
      if (!hcpName) {
        dispatch(addMessage({ sender: 'ai', text: "Please enter an HCP name in the form first to get suggestions." }));
      } else {
        dispatch(fetchSuggestions(hcpName));
      }
    } else {
      // Default to conversational form filling
      dispatch(sendChatMessage(input));
    }

    setInput('');
  };

  return (
    <div className="bg-gray-50 p-6 rounded-lg shadow-sm flex flex-col h-full">
      <div className="flex items-center gap-3 mb-4">
        <Bot className="h-6 w-6 text-blue-600" />
        <div>
          <h2 className="text-xl font-semibold text-gray-800">AI Assistant</h2>
          <p className="text-sm text-gray-500">Log interaction via chat</p>
        </div>
      </div>

      <div className="flex-grow mb-4 p-4 bg-white border border-gray-200 rounded-md overflow-y-auto h-96">
        {messages.length === 0 ? (
          <p className="text-sm text-gray-500">
            Describe an interaction or ask for help.
          </p>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex items-start gap-3 ${
                  msg.sender === 'user' ? 'justify-end' : ''
                }`}
              >
                {msg.sender === 'ai' && (
                  <Bot className="h-6 w-6 text-blue-500 flex-shrink-0" />
                )}
                <div
                  className={`p-3 rounded-lg max-w-xs ${
                    msg.sender === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  <p className="text-sm">{msg.text}</p>
                </div>
                {msg.sender === 'user' && (
                  <User className="h-6 w-6 text-gray-500 flex-shrink-0" />
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Describe or correct interaction..."
          disabled={status === 'loading'}
          className="w-full p-3 pr-28 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button
          onClick={handleSend}
          disabled={status === 'loading'}
          className="absolute right-2 top-1/2 -translate-y-1/2 bg-gray-800 text-white px-4 py-2 rounded-md flex items-center gap-2 hover:bg-gray-900 disabled:bg-gray-400"
        >
          <span className="font-semibold">
            {status === 'loading' ? '...' : 'Send'}
          </span>
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default AIAssistant;