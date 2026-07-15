// api/services/jobs.js
import { API_CONFIG } from '../config.js';
import { mapOperationToUniversalTask, buildDependencyMap } from '../utils/mappers.js';
import { handleApiError } from '../utils/errorHandler.js'; // Ensure this is imported

export const jobsApi = {
  /**
   * Fetches all operations from the backlog (including completed tasks)
   * @returns {Promise<Array>} Array of all operations
   */
  fetchBacklog: async () => {
    const [opsRes, depsRes] = await Promise.all([
      fetch(`${API_CONFIG.BASE_URL}/operations`),
      fetch(`${API_CONFIG.BASE_URL}/operation_dependencies`)
    ]);

    // 1. Trace exactly which endpoint is causing the failure
    await handleApiError(opsRes, 'Failed to fetch raw operations data');
    await handleApiError(depsRes, 'Failed to fetch operation dependencies mapping');

    // 2. Process data only if both explicitly cleared handleApiError checks
    const opsPayload = await opsRes.json();
    const depsPayload = await depsRes.json();
    
    const rawOperations = opsPayload.data || [];
    const rawDependencies = depsPayload.data || [];

    const dependencyMap = buildDependencyMap(rawDependencies);

    return rawOperations.map(op => {
      const upstreamList = dependencyMap[op.id] || [];
      return mapOperationToUniversalTask({
        ...op,
        predecessor: upstreamList.length > 0 ? upstreamList.join(', ') : '-'
      });
    });
  },

  /**
   * Creates a new task/operation with optional dependencies
   * @param {Object} task - Task object with job_id, duration, resources, predecessor, etc.
   * @returns {Promise<Object>} Success response
   */
  addTask: async (task) => {
    const operationPayload = {
      id: task.job_id,
      work_order_id: task.work_order_id || 'MANUAL-WO', 
      sequence_number: parseInt(task.sequence_number) || 10,
      duration_minutes: parseInt(task.duration) * 60,
      assigned_resource_id: (task.resources && task.resources.trim() !== '') ? task.resources.trim().toString() : null,
      status: 'Draft'
    };

    // Step A: Insert task entry into the operations table
    const opResponse = await fetch(`${API_CONFIG.BASE_URL}/operations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(operationPayload)
    });

    await handleApiError(opResponse, 'Failed to create operation');

    // Step B: Link dependencies if provided
    if (task.predecessor && task.predecessor.trim() !== '') {
      const upstreamIds = task.predecessor.split(',').map(id => id.trim()).filter(Boolean);

      for (const upstreamId of upstreamIds) {
        const dependencyPayload = {
          upstream_op_id: upstreamId,
          downstream_op_id: task.job_id
        };

        const depResponse = await fetch(`${API_CONFIG.BASE_URL}/operation_dependencies`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dependencyPayload)
        });

        await handleApiError(depResponse, `Failed to link dependency ${upstreamId}`);
      }
    }

    return { success: true };
  },

  /**
   * Deletes a task/operation and its dependencies
   * @param {string} operationId - ID of the operation to delete
   * @returns {Promise<Object>} Deletion response
   */
  deleteTask: async (operationId) => {
    // Clean up dependent child connections first for relational integrity
    await fetch(`${API_CONFIG.BASE_URL}/operation_dependencies?id_value=${encodeURIComponent(operationId)}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    }).catch(err => console.debug("Cleared task dependency relational map elements", err));

    const response = await fetch(`${API_CONFIG.BASE_URL}/operations?id_value=${encodeURIComponent(operationId)}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });

    await handleApiError(response, 'Failed to delete operation');
    return response.json();
  }
};