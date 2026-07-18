import React, { useState, useEffect } from 'react';
import { api } from './api';
import { styles } from './styles';
import { KPICards } from './KPICards';
import { ScheduleView } from './view/ScheduleView';
import { BacklogView } from './view/BacklogView';
import { ResourcesView } from './view/ResourcesView';
import { TaskForm } from './form/TaskForm';
import { ResourceForm } from './form/ResourceForm';
import { WorkorderView } from './view/WorkorderView';
import { WorkorderForm } from './form/WorkorderForm';
import { GanttChartView } from './view/GanttChartView';
import { ItemsView } from './view/ItemsView';
import { ItemForm } from './form/ItemForm';
import { MaterialsView } from './view/MaterialsView';
import { MaterialForm } from './form/MaterialForm';
import { RoutingTemplatesView } from './view/RoutingTemplatesView';
import { RoutingTemplateForm } from './form/RoutingTemplateForm';
import { OperationDependencyForm } from './form/OperationDependencyForm';

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

  const [resources, setResources] = useState([]);
  const [showResourceForm, setShowResourceForm] = useState(false);
  const [newResource, setNewResource] = useState({
    id: '',
    name: '',
    resource_type: ''
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

  const [materials, setMaterials] = useState([]);
  const [showMaterialForm, setShowMaterialForm] = useState(false);
  const [newMaterial, setNewMaterial] = useState({ id: '', name: '', quantity_available: 0, available_date_minutes: 0 });

  const [routingTemplates, setRoutingTemplates] = useState([]);
  const [showRoutingForm, setShowRoutingForm] = useState(false);
  const [newRoutingTemplate, setNewRoutingTemplate] = useState({
    target_item_id: '',
    step_sequence: '',
    required_resource_type: 'Machine',
    standard_duration_minutes: ''
  });

  const [showDependencyForm, setShowDependencyForm] = useState(false);

  const handleAddDependencyLink = async (dependencyData) => {
    try {
      await api.jobs.addDependencyLink(dependencyData);
      setShowDependencyForm(false);
      
      // Refresh task lists immediately so the "Predecessor" column recalculates text
      fetchBacklogData(); 
    } catch (error) {
      console.error("Error connecting operation flow paths:", error);
      alert("Could not establish dependency line. Verify the link does not duplicate an existing row.");
    }
  };

  const fetchRoutingTemplates = async () => {
    setLoading(true);
    try {
      const data = await api.routing.fetchTemplates();
      setRoutingTemplates(data || []);
    } catch (error) {
      console.error("Error syncing routing templates:", error);
    } finally {
      setLoading(false);
    }
  };

  // Add the submission callback function
  const handleAddRoutingTemplate = async () => {
    try {
      await api.routing.createTemplate(newRoutingTemplate);
      
      // Reset form state & close modal view window
      setNewRoutingTemplate({
        target_item_id: '',
        step_sequence: '',
        required_resource_type: 'Machine',
        standard_duration_minutes: ''
      });
      setShowRoutingForm(false);
      
      // Refresh table view list contents
      fetchRoutingTemplates();
    } catch (error) {
      console.error("Error creating routing template:", error);
    }
  };

  const fetchMaterialsData = async () => {
    setLoading(true);
    try {
      const data = await api.materials.fetchMaterials();
      setMaterials(data || []);
    } catch (error) {
      console.error("Error updating materials ledger:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddMaterial = async (e) => {
    e.preventDefault();
    try {
      await api.materials.addMaterial(newMaterial);
      setShowMaterialForm(false);
      setNewMaterial({ id: '', name: '', quantity_available: 0, available_date_minutes: 0 });
      fetchMaterialsData();
    } catch (error) {
      console.error("Failed to append material schema entry:", error);
    }
  };

  const handleDeleteMaterial = async (matId) => {
    if (!window.confirm(`Are you sure you want to completely drop material allocation entry: ${matId}?`)) return;
    try {
      await api.materials.deleteMaterial(matId);
      fetchMaterialsData();
    } catch (error) {
      console.error("Error dropped cascade tracking entry:", error);
    }
  };

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
  const fetchBacklogData = async () => {
    setLoading(true);
    try {
      const data = await api.jobs.fetchBacklogData();
      setBacklog(data || []);
    } catch (error) {
      console.error("Error fetching backlog:", error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch Resources
  const fetchResources = async () => {
    setLoading(true);
    try {
      const data = await api.resources.fetchResources();
      setResources(data || []);
    } catch (error) {
      console.error("Error fetching resources:", error);
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
      await fetchBacklogData();
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
          fetchBacklogData();
        } else {
          console.error('Failed to add task, backend response:', result);
        }
      } catch (error) {
        console.error("Failed to add task:", error);
      }
    };

  // Handle add resource
  const handleAddResource = async (e) => {
    e.preventDefault();
    try {
      await api.resources.addResource(newResource);
      setShowResourceForm(false);
      setNewResource({ id: '', name: '', resource_type: '' });
      fetchResources();
    } catch (error) {
      console.error("Failed to add resource:", error);
    }
  };

  // Handle delete task
  const handleDeleteTask = async (jobId) => {
    if (!window.confirm(`Are you sure you want to delete job ${jobId}?`)) return;
    
    try {
      await api.jobs.deleteTask(jobId);
      fetchBacklogData();
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchSchedule();
    fetchBacklogData();
    fetchResources();
    fetchWorkorderData();
    fetchItemsData();
    fetchMaterialsData();
    fetchRoutingTemplates();

    // Debugging: Log API data fetches to console for verification
    api.schedule.fetchSchedule().then(data => console.log(" Gantt/Schedule Data Input:", data));
    api.jobs.fetchBacklogData().then(data => console.log(" Backlog Data Input:", data));
    api.resources.fetchResources().then(data => console.log(" Resources Data Input:", data));
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
              📅 Schedule
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
              📋 Backlog
            </button>
            <button
              onClick={() => setView('resources')}
              style={{
                ...styles.navButton,
                ...(view === 'resources' ? styles.activeNav : {})
              }}
            >
              🏭 Resources
            </button>
            
            <button
              onClick={() => setView('workorder')}
              style={{
                ...styles.navButton,
                ...(view === 'workorder' ? styles.activeNav : {})
              }}
            >
              📝 Workorders
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

            <button
              onClick={() => setView('materials')}
              style={{
                ...styles.navButton,
                ...(view === 'materials' ? styles.activeNav : {})
              }}
            >
              🧱 Materials Ledger
            </button>

            <button
              onClick={() => setView('routing')}
              style={{
                ...styles.navButton,
                ...(view === 'routing' ? styles.activeNav : {})
              }}
            >
              Routing Blueprints
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
              onRefresh={fetchBacklogData}
              onAddClick={() => setShowTaskForm(true)}
              onLinkClick={() => setShowDependencyForm(true)}
              onDeleteTask={handleDeleteTask}
            />
            
            {showDependencyForm && (
              <OperationDependencyForm 
                availableOperations={backlog}
                onClose={() => setShowDependencyForm(false)}
                onSubmit={handleAddDependencyLink}
              />
            )}
          </>
        )}

        {view === 'resources' && (
          <>
            <ResourcesView 
              resources={resources} 
              loading={loading}
              onRefresh={fetchResources}
              onAddClick={() => setShowResourceForm(true)}
            />
            {showResourceForm && (
              <ResourceForm 
                newResource={newResource}
                setNewResource={setNewResource}
                onSubmit={handleAddResource}
                onClose={() => setShowResourceForm(false)}
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

        {view === 'materials' && (
          <>
            <MaterialsView 
              materials={materials} 
              loading={loading}
              onRefresh={fetchMaterialsData}
              onAddClick={() => setShowMaterialForm(true)}
              onDeleteMaterial={handleDeleteMaterial}
            />
            {showMaterialForm && (
              <MaterialForm 
                newMaterial={newMaterial}
                setNewMaterial={setNewMaterial}
                onSubmit={handleAddMaterial}
                onClose={() => setShowMaterialForm(false)}
              />
            )}
          </>
        )}

        {view === 'routing' && (
          <>
            <RoutingTemplatesView 
              data={routingTemplates} 
              loading={loading}
              onRefresh={fetchRoutingTemplates}
              onAddClick={() => setShowRoutingForm(true)}
            />
            
            {showRoutingForm && (
              <RoutingTemplateForm 
                newTemplate={newRoutingTemplate}
                setNewTemplate={setNewRoutingTemplate}
                onSubmit={handleAddRoutingTemplate}
                onClose={() => setShowRoutingForm(false)}
              />
            )}
          </>
        )}
        
      </main>
    </div>
  );
}