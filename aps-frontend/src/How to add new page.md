# How to Add a New Page/View

## Quick Answer

Use `ScheduleView.jsx` or `BacklogView.jsx` as templates - they're simple and reusable.

---

## Step-by-Step Guide

### Step 1: Create a New View Component

Create a new file like `ReportView.jsx` in your `view/` directory:

```javascript
// src/view/ReportView.jsx
import React from 'react';
import { styles } from '../styles';

export function ReportView({ data, loading, onRefresh }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Report Title Here</h2>
        <button onClick={onRefresh} style={styles.refreshButton}>Refresh Data</button>
      </div>
      
      {loading ? (
        <p style={styles.message}>Loading data...</p>
      ) : data.length === 0 ? (
        <p style={styles.message}>No data found.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr style={styles.thRow}>
              <th style={styles.th}>Column 1</th>
              <th style={styles.th}>Column 2</th>
              <th style={styles.th}>Column 3</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={index} style={styles.tr}>
                <td style={styles.td}>{item.field1}</td>
                <td style={styles.td}>{item.field2}</td>
                <td style={styles.td}>{item.field3}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

```

---

### Step 2: Add API Service Function

Following the application's actual modular API layer, isolate your server calls by creating a distinct service file under `src/api/services/`:

```javascript
// src/api/services/report.js
import { API_CONFIG } from '../config.js';
import { handleApiError } from '../utils/errorHandler.js';

export const reportApi = {
  fetchReportData: async () => {
    // Uses generic CRUD routing matching the base backend endpoint configuration paths
    const response = await fetch(`${API_CONFIG.BASE_URL}/reports`);
    if (!response.ok) {
      throw new Error('Failed to fetch report data');
    }
    const payload = await response.json();
    return payload.data || [];
  }
};

```

Make sure to export this new service from your central `src/api/index.js` file so it is attached correctly to the global `api` client wrapper:

```javascript
// src/api/index.js example addition
import { reportApi } from './services/report.js';

export const api = {
  // ... existing services (jobs, machines, workorder, schedule)
  report: reportApi
};

```

---

### Step 3: Add State & Logic to App.jsx

Open `App.jsx` and add the management hooks pointing to your aggregated client object namespace (`api.report.<method>`):

```javascript
// Add state for your new page
const [reportData, setReportData] = useState([]);

// Add fetch function
const fetchReportData = async () => {
  setLoading(true);
  try {
    const data = await api.report.fetchReportData(); // Clean modular structure
    setReportData(data || []);
  } catch (error) {
    console.error("Error fetching report:", error);
  } finally {
    setLoading(false);
  }
};

// Call it on component load mounting
useEffect(() => {
  fetchSchedule();
  fetchBacklog();
  fetchMachines();
  fetchReportData(); // Add this

  // ... other code if there are any
}, []);

```

---

### Step 4: Add Navigation Button

In your App.jsx header section, add a matching route selector button:

```javascript
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
  {/* ADD THIS NEW BUTTON */}
  <button
    onClick={() => setView('report')}
    style={{
      ...styles.navButton,
      ...(view === 'report' ? styles.activeNav : {})
    }}
  >
    Reports
  </button>
</nav>

```

---

### Step 5: Add View Conditional in App.jsx

In the main layout render area, add the wrapper execution block for the component lifecycle:

```javascript
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

  {/* ADD THIS NEW VIEW RENDER STEP */}
  {view === 'report' && (
    <ReportView 
      data={reportData} 
      loading={loading}
      onRefresh={fetchReportData}
    />
  )}
</main>

```

---

## Template: Copy-Paste Ready

Here's a minimal template you can use:

```javascript
// src/view/MyNewView.jsx
import React from 'react';
import { styles } from '../styles';

export function MyNewView({ data, loading, onRefresh, onAdd }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>My New Page</h2>
        <div style={{display: 'flex', gap: '12px'}}>
          {onAdd && <button onClick={onAdd} style={{...styles.button, backgroundColor: '#16a34a'}}>+ Add New</button>}
          <button onClick={onRefresh} style={styles.refreshButton}>Refresh</button>
        </div>
      </div>
      
      {loading ? (
        <p style={styles.message}>Loading...</p>
      ) : data.length === 0 ? (
        <p style={styles.message}>No data found.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr style={styles.thRow}>
              <th style={styles.th}>Column A</th>
              <th style={styles.th}>Column B</th>
              <th style={styles.th}>Column C</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={index} style={styles.tr}>
                <td style={styles.td}>{item.fieldA}</td>
                <td style={styles.td}>{item.fieldB}</td>
                <td style={styles.td}>{item.fieldC}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

```

---

## File Structure Reference

```
src/
├── api/
│   ├── services/
│   │   ├── report.js ✨ (NEW)
│   │   ├── jobs.js
│   │   ├── machines.js
│   │   ├── schedule.js
│   │   └── workorder.js
│   ├── utils/
│   │   ├── errorHandler.js
│   │   └── mappers.js
│   ├── config.js
│   ├── index.js (Export new services here)
│   └── README.md
├── form/
│   ├── MachineForm.jsx
│   ├── TaskForm.jsx
│   └── WorkorderForm.jsx
├── view/
│   ├── BacklogView.jsx
│   ├── GanttChartView.jsx
│   ├── MachinesView.jsx
│   ├── ScheduleView.jsx
│   ├── WorkorderView.jsx
│   └── ReportView.jsx ✨ (NEW)
├── App.jsx (updated with new state/logic) 
├── styles.js
├── KPICards.jsx
└── main.jsx

```