const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const api = {
  // Schedule endpoints
  fetchSchedule: async () => {
    const response = await fetch(`${API_BASE_URL}/recent-schedule`);
    if (response.ok) {
      const data = await response.json();
      const jobMap = data.result?.result || {};
      return Object.entries(jobMap).map(([jobId, values]) => ({
        job_id: jobId,
        ...values
      }));
    }
    throw new Error('Failed to fetch schedule');
  },

  triggerOptimization: async () => {
    const response = await fetch(`${API_BASE_URL}/run_scheduler`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    if (!response.ok) throw new Error('Failed to trigger optimization');
    return response.json();
  },

  // Jobs/Tasks endpoints
  fetchBacklog: async () => {
    const response = await fetch(`${API_BASE_URL}/data?table_name=jobs`);
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to fetch backlog');
  },

  addTask: async (task) => {
    const payload = {
      job_id: task.job_id,
      duration: parseInt(task.duration),
      predecessor: task.predecessor || null,
      due_date: parseInt(task.due_date)
    };

    if (task.resources) {
      payload.locked_machine = parseInt(task.resources);
      payload.locked = true;
    }

    const response = await fetch(`${API_BASE_URL}/data?table_name=jobs`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error('Failed to add task');
    return await response.json();
  },

  deleteTask: async (jobId) => {
    const response = await fetch(`${API_BASE_URL}/data?table_name=jobs`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId })
    });
    if (!response.ok) throw new Error('Failed to delete task');
    return response.json();
  },

  // Machines/Resources endpoints
  fetchMachines: async () => {
    const response = await fetch(`${API_BASE_URL}/data?table_name=machines`);
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to fetch machines');
  },

  addMachine: async (machine) => {
    const payload = {
      machine_id: parseInt(machine.machine_id),
      type: machine.type,
      capacity: parseInt(machine.capacity)
    };

    const response = await fetch(`${API_BASE_URL}/data?table_name=machines`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error('Failed to add machine');
    return await response.json();
  }
};