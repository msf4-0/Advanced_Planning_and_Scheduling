const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Helper function to map a database row to a universally compatible frontend object
const mapOperationToUniversalTask = (op) => ({
  // Shared properties
  job_id: op.id,
  work_order_id: op.work_order_id,
  status: op.status,
  
  // BacklogView specific requirements
  duration: op.duration_minutes,
  // CHANGED: Removed default fallback string so our stitcher can control it cleanly
  predecessor: op.predecessor,
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
    const [opsRes, depsRes] = await Promise.all([
      fetch(`${API_BASE_URL}/operations`),
      fetch(`${API_BASE_URL}/operation_dependencies`)
    ]);

    if (opsRes.ok && depsRes.ok) {
      const opsPayload = await opsRes.json();
      const depsPayload = await depsRes.json();
      
      const rawOperations = opsPayload.data || [];
      const rawDependencies = depsPayload.data || [];

      // Group dependencies by downstream task identifier
      const dependencyMap = {};
      rawDependencies.forEach(edge => {
        if (!dependencyMap[edge.downstream_op_id]) {
          dependencyMap[edge.downstream_op_id] = [];
        }
        dependencyMap[edge.downstream_op_id].push(edge.upstream_op_id);
      });

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
    const [opsRes, depsRes] = await Promise.all([
      fetch(`${API_BASE_URL}/operations`),
      fetch(`${API_BASE_URL}/operation_dependencies`)
    ]);

    if (opsRes.ok && depsRes.ok) {
      const opsPayload = await opsRes.json();
      const depsPayload = await depsRes.json();
      
      const rawOperations = opsPayload.data || [];
      const rawDependencies = depsPayload.data || [];

      // Group dependencies by downstream task identifier
      const dependencyMap = {};
      rawDependencies.forEach(edge => {
        if (!dependencyMap[edge.downstream_op_id]) {
          dependencyMap[edge.downstream_op_id] = [];
        }
        dependencyMap[edge.downstream_op_id].push(edge.upstream_op_id);
      });

      return rawOperations.map(op => {
        const upstreamList = dependencyMap[op.id] || [];
        return mapOperationToUniversalTask({
          ...op,
          predecessor: upstreamList.length > 0 ? upstreamList.join(', ') : '-'
        });
      });
    }
    throw new Error('Failed to fetch operations backlog');
  },

  addTask: async (task) => {
    const operationPayload = {
      id: task.job_id,
      work_order_id: task.work_order_id || 'MANUAL-WO', 
      sequence_number: parseInt(task.sequence_number) || 10,
      duration_minutes: parseInt(task.duration) * 60,
      // Safely check for empty string inputs from your form state baseline
      due_date: (task.due_date !== '' && task.due_date !== null) ? parseInt(task.due_date) : null,
      assigned_resource_id: (task.resources && task.resources.trim() !== '') ? task.resources.trim().toString() : null,
      status: 'Draft'
    };

    // Step A: Insert task entry into the operations table
    const opResponse = await fetch(`${API_BASE_URL}/operations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(operationPayload)
    });

    if (!opResponse.ok) {
      const error = await opResponse.text();
      throw new Error(`Failed to create operation: ${error}`);
    }

    // Step B: Loop insert links into operation_dependencies relation matrix
    if (task.predecessor && task.predecessor.trim() !== '') {
      const upstreamIds = task.predecessor.split(',').map(id => id.trim()).filter(Boolean);

      for (const upstreamId of upstreamIds) {
        const dependencyPayload = {
          upstream_op_id: upstreamId,
          downstream_op_id: task.job_id
        };

        const depResponse = await fetch(`${API_BASE_URL}/operation_dependencies`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dependencyPayload)
        });

        if (!depResponse.ok) {
          const error = await depResponse.text();
          throw new Error(`Failed to link dependency ${upstreamId}: ${error}`);
        }
      }
    }

    // Return a guaranteed success payload back to App.jsx
    return { success: true };
  },

  deleteTask: async (operationId) => {
    // Clean up dependent child connections first to ensure relational integrity
    await fetch(`${API_BASE_URL}/operation_dependencies?id_value=${encodeURIComponent(operationId)}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    }).catch(err => console.debug("Cleared task dependency relational map elements", err));

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