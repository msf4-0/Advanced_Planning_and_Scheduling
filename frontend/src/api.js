const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Helper function to map a database row to a universally compatible frontend object
const mapOperationToUniversalTask = (op) => ({
  // Shared properties
  job_id: op.id,
  work_order_id: op.work_order_id,
  status: op.status,
  
  // BacklogView specific requirements
  duration: op.duration_minutes,
  predecessor: op.predecessor || '-',
  allowed_resources: op.assigned_resource_id ? [op.assigned_resource_id] : [],
  
  // ScheduleView specific requirements
  resources: op.assigned_resource_id || 'Any Machine',
  start: op.scheduled_start_time || `${op.optimized_start_minute || 0} mins`,
  end: op.scheduled_end_time || `${op.optimized_end_minute || 0} mins`,
  
  // Keep original numeric offsets for timeline calculations if needed by charts
  start_minute: op.optimized_start_minute,
  end_minute: op.optimized_end_minute
});

export const api = {
  // 1. SCHEDULE ENDPOINTS
  fetchSchedule: async () => {
    const response = await fetch(`${API_BASE_URL}/operations`);
    if (response.ok) {
      const payload = await response.json();
      const rawOperations = payload.data || [];
      
      // Filter out completed, only map active schedules using the universal structure
      return rawOperations
        .filter(op => op.status !== 'Done')
        .map(mapOperationToUniversalTask);
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

  // 2. JOBS / TASKS ENDPOINTS
  fetchBacklog: async () => {
    const response = await fetch(`${API_BASE_URL}/operations`);
    if (response.ok) {
      const payload = await response.json();
      const rawOperations = payload.data || [];

      // Maps the backlog using the exact same universal properties structure
      return rawOperations.map(mapOperationToUniversalTask);
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

  // 3. MACHINES / RESOURCES ENDPOINTS
  fetchMachines: async () => {
    const response = await fetch(`${API_BASE_URL}/resources`);
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