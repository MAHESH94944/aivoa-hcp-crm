import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  createInteraction,
  setFormData,
  fetchSuggestions,
} from "../features/interactions/interactionsSlice";
import { Search, Plus } from "lucide-react";

// Helper function to display complex errors from the backend
const formatError = (error) => {
  if (!error) return "An unknown error occurred.";
  if (error.detail && typeof error.detail === "string") return error.detail;
  if (Array.isArray(error.detail)) {
    return error.detail.map((err) => `${err.loc[1]}: ${err.msg}`).join("; ");
  }
  return "Submission failed. Please check the data.";
};

const InteractionForm = () => {
  const dispatch = useDispatch();
  const { formData, status, error, suggestions } = useSelector(
    (state) => state.interactions
  );

  // Automatically fetch suggestions when the HCP name changes
  useEffect(() => {
    if (formData.hcp_name && formData.hcp_name.length > 3) {
      const timer = setTimeout(() => {
        dispatch(fetchSuggestions(formData.hcp_name));
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [formData.hcp_name, dispatch]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    dispatch(setFormData({ [name]: value }));
  };

  // Functions for adding materials/samples dispatch to the central Redux store
  const handleAddMaterial = () => {
    const newMaterial = prompt(
      "Enter material name to add:",
      "OncoBoost Brochure"
    );
    if (newMaterial) {
      const updatedMaterials = [
        ...(formData.materials_shared || []),
        newMaterial,
      ];
      dispatch(setFormData({ materials_shared: updatedMaterials }));
    }
  };

  const handleAddSample = () => {
    const newSample = prompt(
      "Enter sample name to add:",
      "CardioGuard Starter Kit"
    );
    if (newSample) {
      const updatedSamples = [
        ...(formData.samples_distributed || []),
        newSample,
      ];
      dispatch(setFormData({ samples_distributed: updatedSamples }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const dataToSubmit = {
      ...formData,
      attendees:
        typeof formData.attendees === "string"
          ? formData.attendees
              .split(",")
              .map((name) => name.trim())
              .filter(Boolean)
          : [],
      follow_up_actions:
        typeof formData.follow_up_actions === "string"
          ? [formData.follow_up_actions].filter(Boolean)
          : [],
      // materials_shared and samples_distributed are already correct in formData
    };
    dispatch(createInteraction(dataToSubmit));
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 rounded-lg shadow-sm space-y-6"
    >
      <h2 className="text-xl font-semibold text-gray-800">
        Interaction Details
      </h2>

      {/* --- Form fields --- */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            HCP Name
          </label>
          <input
            type="text"
            name="hcp_name"
            value={formData.hcp_name || ""}
            onChange={handleChange}
            placeholder="Search or select HCP..."
            className="w-full p-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Interaction Type
          </label>
          <select
            name="interaction_type"
            value={formData.interaction_type || "Meeting"}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded-md"
          >
            <option>Meeting</option>
            <option>Call</option>
            <option>Virtual</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Date
          </label>
          <input
            type="date"
            name="date"
            value={formData.date || ""}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Time
          </label>
          <input
            type="time"
            name="time"
            value={formData.time || ""}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded-md"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">
          Attendees
        </label>
        <input
          type="text"
          name="attendees"
          value={formData.attendees || ""}
          onChange={handleChange}
          placeholder="Enter names, separated by commas..."
          className="w-full p-2 border border-gray-300 rounded-md"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">
          Topics Discussed
        </label>
        <textarea
          name="topics_discussed"
          value={formData.topics_discussed || ""}
          onChange={handleChange}
          rows="3"
          placeholder="Enter key discussion points..."
          className="w-full p-2 border border-gray-300 rounded-md"
        ></textarea>
      </div>

      {/* --- Materials and Samples Section --- */}
      <div>
        <h3 className="text-md font-semibold text-gray-700 mb-2">
          Materials Shared / Samples Distributed
        </h3>
        <div className="space-y-4">
          <div className="p-4 border border-gray-200 rounded-md">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium text-gray-600">
                Materials Shared
              </h4>
              <button
                type="button"
                onClick={handleAddMaterial}
                className="inline-flex items-center gap-2 px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <Search className="h-4 w-4" /> Search/Add
              </button>
            </div>
            {formData.materials_shared &&
            formData.materials_shared.length > 0 ? (
              <ul className="list-disc list-inside text-sm text-gray-700">
                {formData.materials_shared.map((material, index) => (
                  <li key={index}>{material}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No materials added.</p>
            )}
          </div>
          <div className="p-4 border border-gray-200 rounded-md">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium text-gray-600">
                Samples Distributed
              </h4>
              <button
                type="button"
                onClick={handleAddSample}
                className="inline-flex items-center gap-2 px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <Plus className="h-4 w-4" /> Add Sample
              </button>
            </div>
            {formData.samples_distributed &&
            formData.samples_distributed.length > 0 ? (
              <ul className="list-disc list-inside text-sm text-gray-700">
                {formData.samples_distributed.map((sample, index) => (
                  <li key={index}>{sample}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No samples added.</p>
            )}
          </div>
        </div>
      </div>

      {/* --- Rest of the form fields --- */}
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-2">
          Observed/Inferred HCP Sentiment
        </label>
        <div className="flex items-center gap-6">
          {["Positive", "Neutral", "Negative"].map((sentiment) => (
            <label
              key={sentiment}
              className="flex items-center gap-2 cursor-pointer"
            >
              <input
                type="radio"
                name="sentiment"
                value={sentiment}
                checked={formData.sentiment === sentiment}
                onChange={handleChange}
                className="h-4 w-4"
              />
              <span>{sentiment}</span>
            </label>
          ))}
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">
          Outcomes
        </label>
        <textarea
          name="outcomes"
          value={formData.outcomes || ""}
          onChange={handleChange}
          rows="2"
          placeholder="Key outcomes or agreements..."
          className="w-full p-2 border border-gray-300 rounded-md"
        ></textarea>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">
          Follow-up Actions
        </label>
        <textarea
          name="follow_up_actions"
          value={formData.follow_up_actions || ""}
          onChange={handleChange}
          rows="2"
          placeholder="Enter next steps or tasks..."
          className="w-full p-2 border border-gray-300 rounded-md"
        ></textarea>
      </div>

      {/* --- AI Suggested Follow-ups (Dynamic) --- */}
      <div>
        <h3 className="text-md font-semibold text-gray-700 mb-2">
          AI Suggested Follow-ups
        </h3>
        {suggestions && suggestions.length > 0 ? (
          <ul className="space-y-2">
            {suggestions.map((item, index) => (
              <li key={index} className="text-sm">
                <p className="text-blue-600 font-semibold">
                  - {item.suggestion}
                </p>
                <p className="text-gray-500 pl-4 text-xs">
                  Rationale: {item.rationale}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-400">
            Enter an HCP name to generate suggestions.
          </p>
        )}
      </div>

      {/* --- Submit Button & Error Display --- */}
      <div className="pt-4 border-t border-gray-200 mt-6">
        <button
          type="submit"
          disabled={status === "loading"}
          className="w-full bg-gray-800 text-white font-bold py-3 px-4 rounded-md hover:bg-gray-900 disabled:bg-gray-400"
        >
          {status === "loading" ? "Submitting..." : "Log Interaction"}
        </button>
      </div>
      {status === "failed" && (
        <p className="text-red-500 text-sm mt-2">{formatError(error)}</p>
      )}
    </form>
  );
};

export default InteractionForm;
