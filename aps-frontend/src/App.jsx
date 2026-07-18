import React, { useState, useEffect } from 'react';
import { api } from './api';
import { styles } from './styles';
import { KPICards } from './KPICards';
import { ScheduleView } from './view/ScheduleView';
import { BacklogView } from './view/BacklogView';
import { MachinesView } from './view/MachinesView';
import { TaskForm } from './form/TaskForm';
import { MachineForm } from './form/MachineForm';
import { WorkorderView } from './view/WorkorderView';
import { WorkorderForm } from './form/WorkorderForm';
import { GanttChartView } from './view/GanttChartView';
import { ItemsView } from './view/ItemsView';
import { ItemForm } from './form/ItemForm';

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
    work_order_id: '', // ADDED: Required matching database constraint element
    duration: '',      // Changed baseline to empty string for safe entry scaling
    predecessor: '',
    due_date: '',
    resources: ''
  });

  const [machines, setMachines] = useState([]);
  const [showMachineForm, setShowMachineForm] = useState(false);
  const [newMachine, setNewMachine] = useState({
    machine_id: '',
    type: '',
    capacity: 1
  });

  const [workorderData, setWorkorderData] = useState([]);
  const [showWorkorderForm, setShowWorkorderForm] = useState(false);
  const [newWorkorder, setNewWorkorder] = useState({
    work_order_id: '',
    target_item_id: '',
    quantity_to_make: 0,
    due_date: ''
  })

  const fetchWorkorderData = async () => {
    setLoading(true);
    try {
      const data = await api.workorder.fetchWorkorders()
      setWorkorderData(data || []);
    } catch (error) {
      console.error(("Error fetching workorder:", error))
    } finally {
      setLoading(false)
    }
  };

  const handleAddWorkorder = async (e) => {
    e.preventDefault();
    try {
      await api.workorder.addWorkorders(newWorkorder);
      setShowWorkorderForm(false);
      setNewWorkorder({
        work_order_id: '',
        target_item_id: '',
        quantity_to_make: 0,
        due_date: ''
      });
      fetchWorkorderData();
    } catch (error) {
      console.error("Failed to add workorder:", error)
    }
  };

  const [items, setItems] = useState([]);
  const [showItemForm, setShowItemForm] = useState(false);
  const [newItem, setNewItem] = useState({ id: '', name: '', sku: '' });

  const fetchItemsData = async () => {
    setLoading(true);
    try {
      const data = await api.items.fetchItems();
      setItems(data || []);
    } catch (error) {
      console.error("Error fetching items:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    try {
      await api.items.addItem(newItem);
      setShowItemForm(false);
      setNewItem({ id: '', name: '', sku: '' });
      fetchItemsData();
    } catch (error) {
      console.error("Failed to append item record:", error);
    }
  };

  const handleDeleteItem = async (itemId) => {
    if (!window.confirm(`Are you sure you want to remove item template ${itemId}?`)) return;
    try {
      await api.items.deleteItem(itemId);
      fetchItemsData();
    } catch (error) {
      console.error("Error removing item template reference:", error);
    }
  };

  // Fetch unscheduled tasks
  const fetchBacklog = async () => {
    setLoading(true);
    try {
      const data = await api.jobs.fetchBacklog();
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
      const data = await api.machines.fetchMachines();
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
      const scheduleArray = await api.schedule.fetchSchedule();
      setSchedule(scheduleArray);

      const maxEnd = scheduleArray.reduce((max, job) => Math.max(max, job.end_minute || 0), 0);
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
      await api.schedule.triggerOptimization();
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
        const result = await api.jobs.addTask(newTask);
        
        // CHANGED: Verifies wrapper success state flag token values
        if (result && result.success) {
          setShowForm(false);
          setNewTask({ 
            job_id: '', 
            work_order_id: '', 
            duration: '', 
            predecessor: '', 
            due_date: '', 
            resources: '' 
          });
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
      await api.machines.addMachine(newMachine);
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
      await api.jobs.deleteTask(jobId);
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
    fetchWorkorderData();
    fetchItemsData();

    // Debugging: Log API data fetches to console for verification
    api.schedule.fetchSchedule().then(data => console.log(" Gantt/Schedule Data Input:", data));
    api.jobs.fetchBacklog().then(data => console.log(" Backlog Data Input:", data));
    api.machines.fetchMachines().then(data => console.log(" Machines Data Input:", data));
    api.workorder.fetchWorkorders().then(data => console.log(" Workorders Data Input:", data));
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
              onClick={() => setView('gantt')} 
              style={{
                ...styles.navButton,
                ...(view === 'gantt' ? styles.activeNav : {})
              }}
            >
              📊 Gantt Chart
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
            
            <button
              onClick={() => setView('workorder')}
              style={{
                ...styles.navButton,
                ...(view === 'workorder' ? styles.activeNav : {})
              }}
            >
              Workorders
            </button>

            <button
              onClick={() => setView('items')}
              style={{
                ...styles.navButton,
                ...(view === 'items' ? styles.activeNav : {})
              }}
            >
              📦 Items Master
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

        {view === 'workorder' && (
          <>
            <WorkorderView 
              workorder={workorderData} 
              loading={loading}
              onRefresh={fetchWorkorderData}
              onAddClick={() => setShowWorkorderForm(true)}
              onDeleteTask={(id) => console.log("Delete workorder", id)}
            />
            {showWorkorderForm && (
              <WorkorderForm 
                newWorkorder={newWorkorder}
                setNewWorkorder={setNewWorkorder}
                onSubmit={handleAddWorkorder}
                onClose={() => setShowWorkorderForm(false)}
              />
            )}
          </>
        )}

        {view === 'gantt' && (
          <GanttChartView 
            schedule={schedule}
            loading={loading}
            onRefresh={fetchSchedule}
          />
        )}

        {view === 'items' && (
          <>
            <ItemsView 
              items={items} 
              loading={loading}
              onRefresh={fetchItemsData}
              onAddClick={() => setShowItemForm(true)}
              onDeleteItem={handleDeleteItem}
            />
            {showItemForm && (
              <ItemForm 
                newItem={newItem}
                setNewItem={setNewItem}
                onSubmit={handleAddItem}
                onClose={() => setShowItemForm(false)}
              />
            )}
          </>
        )}
        
      </main>
    </div>
  );
}