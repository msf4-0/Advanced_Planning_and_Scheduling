// api/services/workorder.js - Workorders endpoints
import { API_CONFIG } from '../config.js';
import { handleApiError } from '../utils/errorHandler.js';

export const workordersApi = {
  /**
   * Fetches all workorders
   * @returns {Promise<Array>} Array of workorder objects
   */
  fetchWorkorders: async () => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/work_orders`);
    
    if (response.ok) {
      const payload = await response.json();
      return payload.data || [];
    }
    throw new Error('Failed to fetch work orders');
  },

  /**
   * Creates a new workorder
   * @param {Object} workorder - Workorder object with required fields
   * @returns {Promise<Object>} Created workorder response
   */
  addWorkorders: async (workorder) => {
    const payload = {
      work_order_id: workorder.work_order_id?.toString() || '',
      target_item_id: workorder.target_item_id?.toString() || '',
      quantity_to_make: workorder.quantity_to_make ? parseInt(workorder.quantity_to_make) : 0,
      due_date: workorder.due_date || null
    };

    const response = await fetch(`${API_CONFIG.BASE_URL}/work_orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    await handleApiError(response, 'Failed to create workorder');
    return await response.json();
  },

  /**
   * Deletes a workorder
   * @param {string} workorderId - ID of the workorder to delete
   * @returns {Promise<Object>} Deletion response
   */
  deleteWorkorder: async (workorderId) => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/workorders?id_value=${encodeURIComponent(workorderId)}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });

    await handleApiError(response, 'Failed to delete workorder');
    return response.json();
  }
};