const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const api = {
  // Schedule endpoints
  fetchSchedule: async () => {
    const response = await fetch(`${API_BASE_URL}/operations`);
    if (response.ok) {
      const payload = await response.json();
      const rawOperations = payload.data || []; // Extracts from generic {"data": [...]} wrapper
      
      // Filter out completed tasks so the Gantt chart reflects active runtime states
      return rawOperations
        .filter(op => op.status !== 'Done')
        .map(op => ({
          job_id: op.id, // Maps operations.id back to chart task component views
          work_order_id: op.work_order_id,
          duration: op.duration_minutes,
          resource_id: op.assigned_resource_id,
          start_minute: op.optimized_start_minute,
          end_minute: op.optimized_end_minute,
          start_time: op.scheduled_start_time,
          end_time: op.scheduled_end_time,
          status: op.status
        }));
    }
    throw new Error('Failed to fetch optimized operations schedule');
  },

  triggerOptimization: async () => {
    // Triggers the background creator engine pipeline routing
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/run_scheduler`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    if (!response.ok) throw new Error('Failed to execute optimization solver engine');
    return response.json();
  },

  // Jobs/Tasks endpoints
  fetchBacklog: async () => {
    const response = await fetch(`${API_BASE_URL}/operations`);
    if (response.ok) {
      const payload = await response.json();
      return payload.data; // Strips out the generic route count envelope wrappers
    }
    throw new Error('Failed to fetch operations backlog matrix');
  },

  addTask: async (task) => {
    // Structure payload properties to exactly align with the PostgreSQL operations schema
    const payload = {
      id: task.job_id, // Unique primary key identifier hash tracking string
      work_order_id: task.work_order_id || 'MANUAL-WO', 
      sequence_number: parseInt(task.sequence_number) || 10,
      duration_minutes: parseInt(task.duration),
      assigned_resource_id: task.resources || null,
      status: 'Draft'
    };

    const response = await fetch(`${API_BASE_URL}/operations`, {
      method: 'POST', // Swapped out legacy PUT with correct semantic standard POST creator route
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error('Failed to create factory operation record entry');
    return await response.json();
  },

  deleteTask: async (operationId) => {
    // Passes identification keys via query strings (?id_value=X) to align with python controllers
    const response = await fetch(`${API_BASE_URL}/operations?id_value=${encodeURIComponent(operationId)}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to drop targeted operation record from canvas');
    return response.json();
  },

  // Machines/Resources endpoints
  fetchMachines: async () => {
    const response = await fetch(`${API_BASE_URL}/resources`);
    if (response.ok) {
      const payload = await response.json();
      return payload.data;
    }
    throw new Error('Failed to fetch physical factory resources catalog');
  },

  addMachine: async (machine) => {
    // Map object structures precisely matching the PostgreSQL resources table
    const payload = {
      id: machine.machine_id.toString(),
      name: machine.name || `${machine.type} Studio Unit`,
      resource_type: machine.type || 'Machine',
      is_active: true
    };

    const response = await fetch(`${API_BASE_URL}/resources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error('Failed to save asset work center capacity resource');
    return await response.json();
  }
};
