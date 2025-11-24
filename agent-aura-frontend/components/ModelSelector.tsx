import React, { useEffect, useState } from 'react';
import { apiClient } from '../lib/api';

interface Model {
  id: string;
  provider: string;
  name: string;
}

interface ModelSelectorProps {
  selectedModel: string | null;
  onModelSelect: (modelId: string) => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({ selectedModel, onModelSelect }) => {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await apiClient.getAvailableModels();
        setModels(response);
        if (!selectedModel && response.length > 0) {
          // Default to first model if none selected
           // Prefer gemini-3-pro-preview if available
           const defaultModel = response.find(m => m.id === 'gemini-3-pro-preview') || response[0];
           onModelSelect(defaultModel.id);
        }
      } catch (error) {
        console.error('Failed to fetch models:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, []);

  if (loading) {
    return <div className="text-base text-gray-200 font-semibold">Loading models...</div>;
  }

  return (
    <div className="flex items-center gap-3">
      <label htmlFor="model-select" className="text-base font-bold text-gray-100">
        Model:
      </label>
      <select
        id="model-select"
        value={selectedModel || ''}
        onChange={(e) => onModelSelect(e.target.value)}
        className="block w-full rounded-xl border-white/20 bg-white/10 py-3 px-4 text-base leading-5 font-semibold text-white shadow-lg focus:border-purple-400 focus:ring-2 focus:ring-purple-400 transition-all"
      >
        {models.map((model) => (
          <option key={model.id} value={model.id} className="bg-gray-900 text-white font-semibold">
            {model.provider.toUpperCase()} - {model.name}
          </option>
        ))}
      </select>
    </div>
  );
};
