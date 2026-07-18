// src/api/services/routing.js
import { API_CONFIG } from '../config.js';

export const routingApi = {
  fetchTemplates: async () => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/routing-templates`);
    if (!response.ok) throw new Error('Failed to fetch routing blueprints');
    const payload = await response.json();
    return payload.data || [];
  },

  createTemplate: async (templateData) => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/routing-templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(templateData),
    });
    if (!response.ok) throw new Error('Failed to save routing blueprint');
    const payload = await response.json();
    return payload.data;
  }
};