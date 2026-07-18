// api/services/items.js - Items endpoints
import { API_CONFIG } from '../config.js';
import { handleApiError } from '../utils/errorHandler.js';

export const itemsApi = {
  fetchItems: async () => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/items`);
    if (!response.ok) throw new Error('Failed to fetch item catalog');
    const payload = await response.json();
    return payload.data || []; // Extract data block array
  },
  addItem: async (itemData) => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(itemData)
    });
    if (!response.ok) throw new Error('Failed to create new item master record');
    return response.json();
  },
  deleteItem: async (itemId) => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/items?id_value=${encodeURIComponent(itemId)}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to delete item');
    return response.json();
  }
}