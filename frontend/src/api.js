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
    // Call /run_scheduler endpoint directly
    const response = await fetch(`/run_scheduler`, {
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
      const rawOperations = payload.data || []; // Strip out the generic route count wrappers

      return rawOperations.map(op => ({
        job_id: op.id,
        duration: op.duration_minutes,
        predecessor: op.predecessor || '-',
        allowed_resources: op.assigned_resource_id ? [op.assigned_resource_id] : [],
        status: op.status
      }));
    }
    throw new Error('Failed to fetch operations backlog');
  },

  addTask: async (task) => {
    // Structure payload to match PostgreSQL operations schema
    const payload = {
      id: task.job_id, // Unique primary key identifier hash tracking string
      work_order_id: task.work_order_id || 'MANUAL-WO', 
      sequence_number: parseInt(task.sequence_number) || 10,
      duration_minutes: parseInt(task.duration) * 60,

      predecessor: task.predecessor || null,
      due_date: task.due_date ? parseInt(task.due_date) : null,
      
      assigned_resource_id: task.resources ? task.resources.toString() : null,
      status: 'Draft'
    };

    const response = await fetch(`${API_BASE_URL}/operations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to create operation: ${error}`);
    }
    return await response.json();
  },

  deleteTask: async (operationId) => {
    // Pass ID via query string to match backend DELETE handler
    const response = await fetch(`${API_BASE_URL}/operations?id_value=${encodeURIComponent(operationId)}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to delete operation: ${error}`);
    }
    return response.json();
  },

  // Machines/Resources endpoints
  fetchMachines: async () => {
    const response = await fetch(`${API_BASE_URL}/resources`);
    if (response.ok) {
      const payload = await response.json();
      const rawMachines = payload.data || [];

      return rawMachines.map(m => ({
        machine_id: m.id,
        type: m.resource_type || m.name || '',
        capacity: m.capacity || Uint16Array
      }));
    }
    throw new Error('Failed to fetch physical factory resources');
  },

  addMachine: async (machine) => {
    // Map to match PostgreSQL resources table schema
    const payload = {
      id: machine.machine_id.toString(),
      name: machine.name || `${machine.type} Unit ${machine.machine_id}`,
      resource_type: machine.type || 'Machine',
      capacity: machine.capacity ? parseInt(machine.capacity) : 1,
      is_active: true
    };

    const response = await fetch(`${API_BASE_URL}/resources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to create resource: ${error}`);
    }
    return await response.json();
  }
};