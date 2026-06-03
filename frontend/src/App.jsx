import React, { useState, useEffect } from 'react';

// Dynamically use the injected environment variable or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [metrics, setMetrics] = useState({ makespan: 0, tardiness: 0 });

  // Fetch current schedule from FastAPI backend
  const fetchSchedule = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/schedule`);
      if (response.ok) {
        const data = await response.json();
        setSchedule(data.tasks || []);
        setMetrics(data.metrics || { makespan: 0, tardiness: 0 });
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
      const response = await fetch(`${API_BASE_URL}/api/v1/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        await fetchSchedule();
      }
    } catch (error) {
      console.error("Failed to trigger optimization pipeline:", error);
    } finally {
      setOptimizing(false);
    }
  };

  useEffect(() => {
    fetchSchedule();
  }, []);

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.title}>Advanced Planning & Scheduling (APS) Engine</h1>
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
                    <td style={styles.td}>{task.resource_id}</td>
                    <td style={styles.td}>{task.start_time}</td>
                    <td style={styles.td}>{task.end_time}</td>
                    <td style={styles.td}>
                      <span style={styles.badge}>Scheduled</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
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
  badge: { backgroundColor: '#dcfce7', color: '#14532d', padding: '4px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: '500' }
};