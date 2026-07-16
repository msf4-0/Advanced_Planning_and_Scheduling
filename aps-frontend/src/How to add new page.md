# How to Add a New Page/View

## Quick Answer
Yes, use `ScheduleView.jsx` or `BacklogView.jsx` as templates - they're simple and reusable.

---

## Step-by-Step Guide

### Step 1: Create a New View Component

Create a new file like `ReportView.jsx` in your `src/` directory:

```javascript
// src/ReportView.jsx
import React from 'react';
import { styles } from './styles';

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

### Step 2: Add State & Logic to App.jsx

Open `App.jsx` and add:

```javascript
// Add state for your new page
const [reportData, setReportData] = useState([]);

// Add fetch function
const fetchReportData = async () => {
  setLoading(true);
  try {
    const data = await api.fetchReportData(); // You'll need to add this to api.js
    setReportData(data || []);
  } catch (error) {
    console.error("Error fetching report:", error);
  } finally {
    setLoading(false);
  }
};

// Call it on component load
useEffect(() => {
  fetchSchedule();
  fetchBacklog();
  fetchMachines();
  fetchReportData(); // Add this
}, []);
```

---

### Step 3: Add Navigation Button

In your App.jsx header, add a nav button:

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

### Step 4: Add View Conditional in App.jsx

In the main content section, add your view:

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

  {/* ADD THIS NEW VIEW */}
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

### Step 5: Add API Function (if needed)

If your new page needs data from the backend, add it to `api.js`:

```javascript
// Add to api.js
fetchReportData: async () => {
  const response = await fetch(`${API_BASE_URL}/data?table_name=reports`);
  if (response.ok) {
    return await response.json();
  }
  throw new Error('Failed to fetch report data');
},
```

---

## Template: Copy-Paste Ready

Here's a minimal template you can use:

```javascript
// src/MyNewView.jsx
import React from 'react';
import { styles } from './styles';

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

## Common Examples

### Example 1: Analytics Page

```javascript
// src/AnalyticsView.jsx
export function AnalyticsView({ metrics, loading, onRefresh }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>System Analytics</h2>
        <button onClick={onRefresh} style={styles.refreshButton}>Refresh</button>
      </div>
      
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', padding: '24px'}}>
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} style={styles.card}>
            <h3 style={styles.cardTitle}>{key}</h3>
            <p style={styles.cardValue}>{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Example 2: Settings Page

```javascript
// src/SettingsView.jsx
export function SettingsView({ settings, onSave, loading }) {
  const [formData, setFormData] = React.useState(settings);
  
  return (
    <div style={styles.tableCard}>
      <h2>Settings</h2>
      <form onSubmit={(e) => { e.preventDefault(); onSave(formData); }}>
        {Object.entries(formData).map(([key, value]) => (
          <div key={key} style={{marginBottom: '16px'}}>
            <label style={styles.label}>{key}</label>
            <input
              type="text"
              value={value}
              onChange={(e) => setFormData({...formData, [key]: e.target.value})}
              style={styles.input}
            />
          </div>
        ))}
        <button type="submit" style={styles.submitButton}>Save Settings</button>
      </form>
    </div>
  );
}
```

---

## Checklist for Adding a New Page

- [ ] Create new `.jsx` file with export function
- [ ] Import `styles` from './styles'
- [ ] Add state in `App.jsx` for your data
- [ ] Add fetch function in `App.jsx`
- [ ] Add API method in `api.js` (if backend call needed)
- [ ] Add navigation button in App.jsx header
- [ ] Add conditional view in main content
- [ ] Import new view component at top of App.jsx
- [ ] Test locally with `npm run build`

---

## File Structure After Adding New Page

```
src/
├── App.jsx (updated with new state/logic)
├── api.js (updated with new API call)
├── styles.js
├── KPICards.jsx
├── ScheduleView.jsx
├── BacklogView.jsx
├── MachinesView.jsx
├── TaskForm.jsx
├── MachineForm.jsx
├── MyNewView.jsx ✨ (NEW)
├── main.jsx
└── index.html
```

---

## Need Help?

Share:
1. What kind of page you want to add
2. What data it should display
3. Any special functionality (forms, charts, etc.)

And I can create the exact component for you!
