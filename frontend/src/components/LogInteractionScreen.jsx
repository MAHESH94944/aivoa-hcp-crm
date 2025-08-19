import React from 'react';
import InteractionForm from './InteractionForm';
import AIAssistant from './AIAssistant';

const LogInteractionScreen = () => {
  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Log HCP Interaction</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Side: Form */}
        <div className="lg:col-span-2">
          <InteractionForm />
        </div>

        {/* Right Side: AI Assistant */}
        <div>
          <AIAssistant />
        </div>

      </div>
    </div>
  );
};

export default LogInteractionScreen;