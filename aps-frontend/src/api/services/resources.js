// api/services/resources.js - Resources endpoints
import { API_CONFIG } from '../config.js';
import { handleApiError } from '../utils/errorHandler.js';

export const resourcesApi = {
  /**
   * Fetches all available generic resources
   * @returns {Promise<Array>} Array of resource objects
   */
  fetchResources: async () => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/resources`);
    
    if (response.ok) {
      const payload = await response.json();
      const rawResources = payload.data || [];

      // Mapped straight to the exact DB columns
      return rawResources.map(r => ({
        id: r.id,
        name: r.name || '',
        resource_type: r.resource_type || '',
        is_active: r.is_active ?? true
      }));
    }
    throw new Error('Failed to fetch factory resources');
  },

  /**
   * Creates a new resource matching DB columns perfectly
   * @param {Object} resource - Resource object with id, name, resource_type
   * @returns {Promise<Object>} Created resource response
   */
  addResource: async (resource) => {
    const payload = {
      id: resource.id.toString(),
      name: resource.name || `${resource.resource_type} Unit ${resource.id}`,
      resource_type: resource.resource_type || 'Generic',
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