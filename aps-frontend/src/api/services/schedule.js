// api/services/schedule.js - Schedule and optimization endpoints
import { API_CONFIG } from '../config.js';
import { mapOperationToUniversalTask } from '../utils/mappers.js';
import { handleApiError } from '../utils/errorHandler.js';

export const scheduleApi = {
  /**
   * Fetches the current optimized schedule and enriches it with operation details
   * 
   * The /recent-schedule endpoint provides timing (start/end minutes)
   * But we need to fetch /operations to get task details (status, resources, work_order_id)
   * 
   * @returns {Promise<Array>} Array of UI-ready universal tasks
   */
  fetchSchedule: async () => {
    try {
      // Step 1: Get the optimized schedule with timing data
      const scheduleResponse = await fetch(API_CONFIG.RECENT_SCHEDULE);
      await handleApiError(scheduleResponse, 'Failed to fetch optimized operations schedule');
      const schedulePayload = await scheduleResponse.json();
      const scheduledTasks = schedulePayload.tasks || [];

      // Step 2: Get all operations with their details (status, resources, work_order_id, etc.)
      const opsResponse = await fetch(`${API_CONFIG.BASE_URL}/operations`);
      await handleApiError(opsResponse, 'Failed to fetch operations details');
      const opsPayload = await opsResponse.json();
      const allOperations = opsPayload.data || [];

      // Step 3: Create a lookup map for quick access to operation details by operation_id
      const operationDetailsMap = {};
      allOperations.forEach(op => {
        operationDetailsMap[op.id] = op; // op.id is the operation_id like "op_wo1_10"
      });

      // Step 4: Merge schedule timing data with operation details
      const enrichedTasks = scheduledTasks.map(scheduledTask => {
        // Find the matching operation details
        const operationDetails = operationDetailsMap[scheduledTask.operation_id] || {};

        // Combine the two data sources
        const combinedTask = {
          ...scheduledTask,                    // Timing: optimized_start_minute, optimized_end_minute, etc.
          ...operationDetails,                 // Details: status, assigned_resource_id, work_order_id, etc.
          // Keep operation_id as the primary ID (structured like "op_wo1_10")
          operation_id: scheduledTask.operation_id
        };

        // Transform to UI-ready format
        return mapOperationToUniversalTask(combinedTask);
      });

      return enrichedTasks;
    } catch (error) {
      console.error('Schedule fetch error:', error);
      throw error;
    }
  },

  /**
   * Triggers the optimization solver engine
   * Computes optimal job scheduling based on constraints
   * 
   * @returns {Promise<Object>} Optimization result containing run_info
   */
  triggerOptimization: async () => {
    const response = await fetch(API_CONFIG.SCHEDULER_RUNNER, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    
    await handleApiError(response, 'Failed to execute optimization solver engine');
    return response.json();
  }
};