// api/services/machines.js - Machines and resources endpoints
import { API_CONFIG } from '../config.js';
import { handleApiError } from '../utils/errorHandler.js';

export const workorderApi = {
  /**
   * Fetches all available Workorders
   * @returns {Promise<Array>} Array of machine objects
   */
  fetchWorkorders: async () => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/work_orders`);
    
    if (response.ok) {
      const payload = await response.json();
      const rawWorkorders = payload.data || [];

      return rawWorkorders.map(wo => ({
        workorder_id: wo.id,
        target_item_id: wo.target_item_id,
        quantity: wo.quantity_to_make,
        due_date: wo.due_date,
        status: wo.status
      }));
    }
    throw new Error('Failed to fetch work orders');
  },

  /**
   * Creates a new machine/resource
   * @param {Object} machine - Machine object with machine_id, type, capacity, name
   * @returns {Promise<Object>} Created machine response
   */
  addWorkorders: async (machine) => {
    const payload = {
      id: machine.machine_id.toString(),
      name: machine.name || `${machine.type} Unit ${machine.machine_id}`,
      resource_type: machine.type || 'Machine',
      capacity: machine.capacity ? parseInt(machine.capacity) : 1,
      is_active: true
    };

    const response = await fetch(`${API_CONFIG.BASE_URL}/resources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    await handleApiError(response, 'Failed to create resource');
    return await response.json();
  }
};