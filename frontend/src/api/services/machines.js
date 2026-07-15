// api/services/machines.js - Machines and resources endpoints
import { API_CONFIG } from '../config.js';
import { handleApiError } from '../utils/errorHandler.js';

export const machinesApi = {
  /**
   * Fetches all available machines/resources
   * @returns {Promise<Array>} Array of machine objects
   */
  fetchMachines: async () => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/resources`);
    
    if (response.ok) {
      const payload = await response.json();
      const rawMachines = payload.data || [];

      return rawMachines.map(m => ({
        machine_id: m.id,
        type: m.resource_type || m.name || '',
        capacity: m.capacity || 1
      }));
    }
    throw new Error('Failed to fetch physical factory resources');
  },

  /**
   * Creates a new machine/resource
   * @param {Object} machine - Machine object with machine_id, type, capacity, name
   * @returns {Promise<Object>} Created machine response
   */
  addMachine: async (machine) => {
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