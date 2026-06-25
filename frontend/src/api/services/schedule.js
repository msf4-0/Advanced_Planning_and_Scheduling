// api/services/schedule.js - Schedule and optimization endpoints
import { API_CONFIG } from '../config.js';
import { mapOperationToUniversalTask, buildDependencyMap } from '../utils/mappers.js';
import { handleApiError } from '../utils/errorHandler.js';

export const scheduleApi = {
  /**
   * Fetches the current optimized schedule (excludes completed tasks)
   * @returns {Promise<Array>} Array of scheduled operations
   */
  fetchSchedule: async () => {
    const [opsRes, depsRes] = await Promise.all([
      fetch(`${API_CONFIG.BASE_URL}/operations`),
      fetch(`${API_CONFIG.BASE_URL}/operation_dependencies`)
    ]);

    if (opsRes.ok && depsRes.ok) {
      const opsPayload = await opsRes.json();
      const depsPayload = await depsRes.json();
      
      const rawOperations = opsPayload.data || [];
      const rawDependencies = depsPayload.data || [];

      const dependencyMap = buildDependencyMap(rawDependencies);

      return rawOperations
        .filter(op => op.status !== 'Done')
        .map(op => {
          const upstreamList = dependencyMap[op.id] || [];
          return mapOperationToUniversalTask({
            ...op,
            predecessor: upstreamList.length > 0 ? upstreamList.join(', ') : '-'
          });
        });
    }
    throw new Error('Failed to fetch optimized operations schedule');
  },

  /**
   * Triggers the optimization solver engine
   * @returns {Promise<Object>} Optimization result
   */
  triggerOptimization: async () => {
    const response = await fetch(API_CONFIG.SCHEDULER_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    
    await handleApiError(response, 'Failed to execute optimization solver engine');
    return response.json();
  }
};