import React, { useState, useEffect } from 'react';
import { api } from './api';
import { styles } from './styles';
import { KPICards } from './KPICards';
import { ScheduleView } from './ScheduleView';
import { BacklogView } from './BacklogView';
import { MachinesView } from './MachinesView';
import { TaskForm } from './TaskForm';
import { MachineForm } from './MachineForm';

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

  // Fetch unscheduled tasks
  const fetchBacklog = async () => {
    setLoading(true);
    try {
      const data = await api.fetchBacklog();
      setBacklog(data || []);
    } catch (error) {
      console.error("Error fetching backlog:", error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch machines
  const fetchMachines = async () => {
    setLoading(true);
    try {
      const data = await api.fetchMachines();
      setMachines(data || []);
    } catch (error) {
      console.error("Error fetching machines:", error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch schedule
  const fetchSchedule = async () => {
    setLoading(true);
    try {
      const scheduleArray = await api.fetchSchedule();
      setSchedule(scheduleArray);

      const maxEnd = scheduleArray.reduce((max, job) => Math.max(max, job.end || 0), 0);
      setMetrics({ makespan: maxEnd, tardiness: 0 });
    } catch (error) {
      console.error("Error fetching schedule execution data:", error);
    } finally {
      setLoading(false);
    }
  };

  // Trigger optimization
  const triggerOptimization = async () => {
    setOptimizing(true);
    try {
      await api.triggerOptimization();
      await fetchSchedule();
      await fetchBacklog();
      setView('schedule');
    } catch (error) {
      console.error("Failed to trigger optimization pipeline:", error);
    } finally {
      setOptimizing(false);
    }
  };

  // Handle add task
  const handleAddTask = async (e) => {
    e.preventDefault();
    try {
      const result = await api.addTask(newTask);
      if (Array.isArray(result) && result.length > 0) {
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

  // Handle add machine
  const handleAddMachine = async (e) => {
    e.preventDefault();
    try {
      await api.addMachine(newMachine);
      setShowMachineForm(false);
      setNewMachine({ machine_id: '', type: '', capacity: 1 });
      fetchMachines();
    } catch (error) {
      console.error("Failed to add machine:", error);
    }
  };

  // Handle delete task
  const handleDeleteTask = async (jobId) => {
    if (!window.confirm(`Are you sure you want to delete job ${jobId}?`)) return;
    
    try {
      await api.deleteTask(jobId);
      fetchBacklog();
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchSchedule();
    fetchBacklog();
    fetchMachines();
  }, []);

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Advanced Planning & Scheduling</h1>
          <nav style={styles.nav}>
            <button
              onClick={() => setView('schedule')}
              style={{
                ...styles.navButton,
                ...(view === 'schedule' ? styles.activeNav : {})
              }}
            >
              Schedule
            </button>
            <button
              onClick={() => setView('backlog')}
              style={{
                ...styles.navButton,
                ...(view === 'backlog' ? styles.activeNav : {})
              }}
            >
              Backlog
            </button>
            <button
              onClick={() => setView('machines')}
              style={{
                ...styles.navButton,
                ...(view === 'machines' ? styles.activeNav : {})
              }}
            >
              Machines
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
      <KPICards metrics={metrics} optimizing={optimizing} />

      {/* Main Content */}
      <main style={styles.mainContent}>
        {view === 'schedule' && (
          <ScheduleView 
            schedule={schedule} 
            loading={loading}
            onRefresh={fetchSchedule}
          />
        )}

        {view === 'backlog' && (
          <>
            <BacklogView 
              backlog={backlog} 
              loading={loading}
              onRefresh={fetchBacklog}
              onAddClick={() => setShowForm(true)}
              onDeleteTask={handleDeleteTask}
            />
            {showForm && (
              <TaskForm 
                newTask={newTask}
                setNewTask={setNewTask}
                onSubmit={handleAddTask}
                onClose={() => setShowForm(false)}
              />
            )}
          </>
        )}

        {view === 'machines' && (
          <>
            <MachinesView 
              machines={machines} 
              loading={loading}
              onRefresh={fetchMachines}
              onAddClick={() => setShowMachineForm(true)}
            />
            {showMachineForm && (
              <MachineForm 
                newMachine={newMachine}
                setNewMachine={setNewMachine}
                onSubmit={handleAddMachine}
                onClose={() => setShowMachineForm(false)}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}