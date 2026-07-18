// src/api/services/materials.js
import { API_CONFIG } from '../config.js';

export const materialsApi = {
  fetchMaterials: async () => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/materials`);
    if (!response.ok) throw new Error('Failed to fetch materials inventory');
    const payload = await response.json();
    return payload.data || []; 
  },
  addMaterial: async (materialData) => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/materials`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...materialData,
        // Ensure proper numeric casting before sending to database
        quantity_available: parseFloat(materialData.quantity_available || 0),
        available_date_minutes: parseInt(materialData.available_date_minutes || 0, 10)
      })
    });
    if (!response.ok) throw new Error('Failed to create material record');
    return response.json();
  },
  deleteMaterial: async (materialId) => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/materials?id_value=${encodeURIComponent(materialId)}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to delete material');
    return response.json();
  }
};