// src/api/services/materials.js
import { API_CONFIG } from '../config.js';

export const materialsApi = {
  /**
   * Fetches the list of materials from the backend API
   * @returns {Promise<Array>} An array of material records
   */
  fetchMaterials: async () => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/materials`);
    if (!response.ok) throw new Error('Failed to fetch materials inventory');
    const payload = await response.json();
    return payload.data || []; 
  },

  /**
   * Adds a new material record
   * @param {Object} materialData - The data for the new material
   * @returns {Promise<Object>} The created material record
   */
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

  /**
   * Deletes a material record by its ID
   * @param {string} materialId - The ID of the material to delete
   */
  deleteMaterial: async (materialId) => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/materials?id_value=${encodeURIComponent(materialId)}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to delete material');
    return response.json();
  },

  /**
   * Allocates raw materials to a specific operation task
   * @param {Object} allocationData - contains operation_id, material_id, and quantity_required
   */
  allocateMaterial: async (allocationData) => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/operation_materials`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        operation_id: allocationData.operation_id,
        material_id: allocationData.material_id,
        quantity_required: parseFloat(allocationData.quantity_required || 0)
      })
    });

    if (!response.ok) {
      throw new Error('Failed to assign material requirements line item to operation.');
    }
    return response.json();
  },
};