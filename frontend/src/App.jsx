import React, { useState, useEffect } from 'react';

// Dynamically use the injected environment variable or fallback to the nginx proxy '/api' prefix
// When running in Docker with the provided nginx config, API routes are served under '/api'
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export default function App() {
  const [view, setView] = useState('schedule');
  const [schedule, setSchedule] = useState([]);
  const [backlog, setBacklog] = useState([]);
  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [metrics, setMetrics] = useState({ makespan: 0, tardiness: 0 });
  const [showForm, setShowForm] = useState(false);
  const [newTask, setNewTask] = useState({
    job_id: '',
    duration: 1,
    allowed_resources: '1',
    predecessor: '',
    due_date: 0,
    resources: ''
  });
  const [machines, setMachines] = useState([]);
  const [showMachineForm, setShowMachineForm] = useState(false);
  const [newMachine, setNewMachine] = useState({
    machine_id: '',
    type: '',
    capacity: 1
  });

  // Fetch unscheduled tasks from backend
  const fetchBacklog = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/data?table_name=jobs`);
      if (response.ok) {
        const data = await response.json();
        setBacklog(data || []);
      }
    } catch (error) {
      console.error("Error fetching backlog:", error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch machines/resources from backend
  const fetchMachines = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/data?table_name=machines`);
      if (response.ok) {
        const data = await response.json();
        setMachines(data || []);
      }
    } catch (error) {
      console.error("Error fetching machines:", error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch current schedule from FastAPI backend
  const fetchSchedule = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/recent-schedule`);
      if (response.ok) {
        const data = await response.json();
        // The backend returns { "success": true, "result": { "result": { ...jobs... } } }
        const jobMap = data.result?.result || {};
        const scheduleArray = Object.entries(jobMap).map(([jobId, values]) => ({
          job_id: jobId,
          ...values
        }));
        setSchedule(scheduleArray);

        // Dynamically calculate makespan (max end time) from results
        const maxEnd = scheduleArray.reduce((max, job) => Math.max(max, job.end || 0), 0);
        setMetrics({ makespan: maxEnd, tardiness: 0 });
      }
    } catch (error) {
      console.error("Error fetching schedule execution data:", error);
    } finally {
      setLoading(false);
    }
  };

  // Trigger OR-Tools / Scheduler optimization routine
  const triggerOptimization = async () => {
    setOptimizing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/run_scheduler`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      if (response.ok) {
        await fetchSchedule();
        await fetchBacklog();
        setView('schedule');
      }
    } catch (error) {
      console.error("Failed to trigger optimization pipeline:", error);
    } finally {
      setOptimizing(false);
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        job_id: newTask.job_id,
        duration: parseInt(newTask.duration),
        predecessor: newTask.predecessor || null,
        due_date: parseInt(newTask.due_date)
      };

      if (newTask.resources) {
        // Map fixed assigned resource to the jobs table's locked_machine field.
        payload.locked_machine = parseInt(newTask.resources);
        payload.locked = true;
      }

      const response = await fetch(`${API_BASE_URL}/data?table_name=jobs`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      if (response.ok && Array.isArray(result) && result.length > 0) {
        setShowForm(false);
        setNewTask({ job_id: '', duration: 1, allowed_resources: '1', predecessor: '', due_date: 0, resources: '' });
        fetchBacklog();
      } else {
        console.error('Failed to add task, backend response:', result);
      }
    } catch (error) {
      console.error("Failed to add task:", error);
    }
  };

  const handleAddMachine = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        machine_id: parseInt(newMachine.machine_id),
        type: newMachine.type,
        capacity: parseInt(newMachine.capacity)
      };

      const response = await fetch(`${API_BASE_URL}/data?table_name=machines`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setShowMachineForm(false);
        setNewMachine({ machine_id: '', type: '', capacity: 1 });
        fetchMachines();
      } else {
        console.error("Failed to add machine. Response status:", response.status);
      }
    } catch (error) {
      console.error("Failed to add machine:", error);
    }
  };

  const handleDeleteTask = async (jobId) => {
    if (!window.confirm(`Are you sure you want to delete job ${jobId}?`)) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/data?table_name=jobs`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId })
      });

      if (response.ok) {
        fetchBacklog();
      } else {
        console.error("Failed to delete task");
      }
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  useEffect(() => {
    fetchSchedule();
    fetchBacklog();
    fetchMachines();
  }, []);

  console.log("APS Engine UI Loaded. Current View:", view);

  return (
    <div style={styles.container}>
      {/* Add Task Modal */}
      {showForm && (
        <div style={styles.formModal}>
          <form style={styles.formContent} onSubmit={handleAddTask}>
            <h2 style={{marginBottom: '20px'}}>Add New Scheduling Task</h2>
            
            <label style={styles.label}>Job ID (Unique Name)</label>
            <input style={styles.input} required value={newTask.job_id} onChange={e => setNewTask({...newTask, job_id: e.target.value})} placeholder="e.g. BATCH_101" />
            
            <div style={{display: 'flex', gap: '16px'}}>
              <div style={{flex: 1}}>
                <label style={styles.label}>Duration (hrs)</label>
                <input style={styles.input} type="number" required value={newTask.duration} onChange={e => setNewTask({...newTask, duration: e.target.value})} />
              </div>
              <div style={{flex: 1}}>
                <label style={styles.label}>Due Date (hrs)</label>
                <input style={styles.input} type="number" value={newTask.due_date} onChange={e => setNewTask({...newTask, due_date: e.target.value})} />
              </div>
            </div>

            <label style={styles.label}>Allowed Resources (IDs, comma separated)</label>
            <input style={styles.input} value={newTask.allowed_resources} onChange={e => setNewTask({...newTask, allowed_resources: e.target.value})} placeholder="e.g. 1, 2, 3" />

            <label style={styles.label}>Predecessor Job ID (Optional)</label>
            <input style={styles.input} value={newTask.predecessor} onChange={e => setNewTask({...newTask, predecessor: e.target.value})} placeholder="e.g. BATCH_100" />

            <label style={styles.label}>Fixed Resource Assignment (Optional)</label>
            <input style={styles.input} value={newTask.resources} onChange={e => setNewTask({...newTask, resources: e.target.value})} placeholder="e.g. 1" />

            <div style={styles.formActions}>
              <button type="button" onClick={() => setShowForm(false)} style={styles.cancelButton}>Cancel</button>
              <button type="submit" style={styles.submitButton}>Create Task</button>
            </div>
          </form>
        </div>
      )}

      {/* Add Machine Modal */}
      {showMachineForm && (
        <div style={styles.formModal}>
          <form style={styles.formContent} onSubmit={handleAddMachine}>
            <h2 style={{marginBottom: '20px'}}>Add New Machine/Resource</h2>
            
            <label style={styles.label}>Machine ID (Numeric)</label>
            <input style={styles.input} type="number" required value={newMachine.machine_id} onChange={e => setNewMachine({...newMachine, machine_id: e.target.value})} placeholder="e.g. 1" />
            
            <label style={styles.label}>Machine Type</label>
            <input style={styles.input} required value={newMachine.type} onChange={e => setNewMachine({...newMachine, type: e.target.value})} placeholder="e.g. CNC, Lathe, Milling" />
            
            <label style={styles.label}>Capacity (parallel jobs)</label>
            <input style={styles.input} type="number" required value={newMachine.capacity} onChange={e => setNewMachine({...newMachine, capacity: e.target.value})} min="1" />

            <div style={styles.formActions}>
              <button type="button" onClick={() => setShowMachineForm(false)} style={styles.cancelButton}>Cancel</button>
              <button type="submit" style={styles.submitButton}>Create Machine</button>
            </div>
          </form>
        </div>
      )}

      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Advanced Planning & Scheduling (APS) Engine v2.1</h1>
          <nav style={styles.nav}>
            <button 
              onClick={() => setView('schedule')} 
              style={{...styles.navButton, ...(view === 'schedule' ? styles.activeNav : {})}}
            >
              Operational Schedule
            </button>
            <button 
              onClick={() => setView('backlog')} 
              style={{...styles.navButton, ...(view === 'backlog' ? styles.activeNav : {})}}
            >
              Task Backlog
            </button>
            <button 
              onClick={() => setView('machines')} 
              style={{...styles.navButton, ...(view === 'machines' ? styles.activeNav : {})}}
            >
              Machines/Resources
            </button>
          </nav>
        </div>
        <button 
          onClick={triggerOptimization} 
          disabled={optimizing} 
          style={{...styles.button, backgroundColor: optimizing ? '#9ca3af' : '#2563eb'}}
        >
          {optimizing ? 'Optimizing Schedule...' : 'Run Optimization'}
        </button>
      </header>

    {/* KPI Cards */}
    <section style={styles.kpiGrid}>
        <div style={styles.card}>
            <h3 style={styles.cardTitle}>Makespan (C_max)</h3>
            <p style={styles.cardValue}>{metrics.makespan} hrs</p>
        </div>
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Total Tardiness</h3>
          <p style={styles.cardValue}>{metrics.tardiness} jobs</p>
        </div>
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>System Status</h3>
          <p style={{...styles.cardValue, color: optimizing ? '#d97706' : '#16a34a'}}>
            {optimizing ? 'Re-calculating' : 'Idle / Optimized'}
          </p>
        </div>
      </section>

      {/* Schedule Table View */}
      <main style={styles.mainContent}>
        {view === 'schedule' ? (
          <div style={styles.tableCard}>
            <div style={styles.tableHeader}>
              <h2>Operational Schedule Outputs</h2>
              <button onClick={fetchSchedule} style={styles.refreshButton}>Refresh Data</button>
            </div>
            
            {loading ? (
              <p style={styles.message}>Loading execution plans...</p>
            ) : schedule.length === 0 ? (
              <p style={styles.message}>No active schedule found. Run optimization to generate allocations.</p>
            ) : (
              <table style={styles.table}>
                <thead>
                  <tr style={styles.thRow}>
                    <th style={styles.th}>Job ID</th>
                    <th style={styles.th}>Resource / Machine</th>
                    <th style={styles.th}>Start Time</th>
                    <th style={styles.th}>End Time</th>
                    <th style={styles.th}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {schedule.map((task, index) => (
                    <tr key={index} style={styles.tr}>
                      <td style={styles.td}><strong>{task.job_id}</strong></td>
                      <td style={styles.td}>{task.resources}</td>
                      <td style={styles.td}>{task.start}</td>
                      <td style={styles.td}>{task.end}</td>
                      <td style={styles.td}>
                        <span style={styles.badge}>Scheduled</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        ) : view === 'backlog' ? (
          <div style={styles.tableCard}>
            <div style={styles.tableHeader}>
              <h2>Unscheduled Task Backlog</h2>
              <div style={{display: 'flex', gap: '12px'}}>
                <button onClick={() => setShowForm(true)} style={{...styles.button, backgroundColor: '#16a34a'}}>+ Add New Task</button>
                <button onClick={fetchBacklog} style={styles.refreshButton}>Refresh</button>
              </div>
            </div>
            
            {loading ? (
              <p style={styles.message}>Loading backlog...</p>
            ) : backlog.length === 0 ? (
              <p style={styles.message}>No unscheduled tasks found. Add a task to get started.</p>
            ) : (
              <table style={styles.table}>
                <thead>
                  <tr style={styles.thRow}>
                    <th style={styles.th}>Job ID</th>
                    <th style={styles.th}>Duration</th>
                    <th style={styles.th}>Predecessor</th>
                    <th style={styles.th}>Allowed Resources</th>
                    <th style={styles.th}>Status</th>
                    <th style={styles.th}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {backlog.map((task, index) => (
                    <tr key={index} style={styles.tr}>
                      <td style={styles.td}><strong>{task.job_id}</strong></td>
                      <td style={styles.td}>{task.duration || task.properties?.duration} hrs</td>
                      <td style={styles.td}>{task.predecessor || task.properties?.predecessor || '-'}</td>
                      <td style={styles.td}>{(task.allowed_resources || task.properties?.allowed_resources || []).join(', ')}</td>
                      <td style={styles.td}>
                        <span style={{...styles.badge, backgroundColor: '#fef3c7', color: '#92400e'}}>Unscheduled</span>
                      </td>
                      <td style={styles.td}>
                        <button 
                          onClick={() => handleDeleteTask(task.job_id)}
                          style={{...styles.button, backgroundColor: '#dc2626', padding: '6px 12px', fontSize: '12px'}}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        ) : (
          <div style={styles.tableCard}>
            <div style={styles.tableHeader}>
              <h2>Machines & Resources</h2>
              <div style={{display: 'flex', gap: '12px'}}>
                <button onClick={() => setShowMachineForm(true)} style={{...styles.button, backgroundColor: '#16a34a'}}>+ Add New Machine</button>
                <button onClick={fetchMachines} style={styles.refreshButton}>Refresh</button>
              </div>
            </div>
            
            {loading ? (
              <p style={styles.message}>Loading machines...</p>
            ) : machines.length === 0 ? (
              <p style={styles.message}>No machines found. Add a machine to get started.</p>
            ) : (
              <table style={styles.table}>
                <thead>
                  <tr style={styles.thRow}>
                    <th style={styles.th}>Machine ID</th>
                    <th style={styles.th}>Type</th>
                    <th style={styles.th}>Capacity</th>
                  </tr>
                </thead>
                <tbody>
                  {machines.map((machine, index) => (
                    <tr key={index} style={styles.tr}>
                      <td style={styles.td}><strong>{machine.machine_id}</strong></td>
                      <td style={styles.td}>{machine.type}</td>
                      <td style={styles.td}>{machine.capacity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

const styles = {
  container: { padding: '24px', maxWidth: '1200px', margin: '0 auto' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' },
  title: { fontSize: '24px', fontWeight: 'bold', color: '#111827' },
  button: { color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', fontWeight: '6px', fontSize: '14px' },
  refreshButton: { background: 'none', border: '1px solid #d1d5db', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' },
  kpiGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' },
  card: { background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  cardTitle: { margin: '0 0 8px 0', fontSize: '14px', color: '#6b7280', textTransform: 'uppercase' },
  cardValue: { margin: 0, fontSize: '24px', fontWeight: 'bold' },
  mainContent: { background: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' },
  tableCard: { padding: '24px' },
  tableHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
  table: { width: '100%', borderCollapse: 'collapse', textAlign: 'left' },
  thRow: { borderBottom: '2px solid #e5e7eb', background: '#f9fafb' },
  th: { padding: '12px', color: '#374151', fontWeight: '600' },
  tr: { borderBottom: '1px solid #e5e7eb' },
  td: { padding: '12px' },
  message: { textAlign: 'center', padding: '40px', color: '#6b7280' },
  badge: { backgroundColor: '#dcfce7', color: '#14532d', padding: '4px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: '500' },
  nav: { display: 'flex', gap: '12px', marginTop: '12px' },
  navButton: { background: 'none', border: 'none', padding: '8px 16px', cursor: 'pointer', borderBottom: '2px solid transparent', fontSize: '14px', color: '#6b7280' },
  activeNav: { borderBottomColor: '#2563eb', color: '#2563eb', fontWeight: 'bold' },
  formModal: { background: 'rgba(0,0,0,0.5)', position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
  formContent: { background: '#fff', padding: '32px', borderRadius: '12px', width: '100%', maxWidth: '500px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' },
  label: { display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '600', color: '#374151' },
  input: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', marginBottom: '16px', fontSize: '14px', boxSizing: 'border-box' },
  formActions: { display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '12px' },
  cancelButton: { background: '#f3f4f6', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' },
  submitButton: { background: '#2563eb', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' },
};