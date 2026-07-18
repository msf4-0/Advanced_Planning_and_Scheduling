import React from 'react';
import { styles } from '../styles';

export function BacklogView({ backlog, loading, onRefresh, onAddClick, onLinkClick, onAllocateClick, onDeleteTask }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Unscheduled Task Backlog</h2>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            onClick={onAllocateClick} 
            style={{ ...styles.button, backgroundColor: '#16a34a', padding: '8px 16px' }}
          >
            📦 Allocate Materials
          </button>
          <button 
            onClick={onLinkClick} 
            style={{ ...styles.button, backgroundColor: '#2563eb', padding: '8px 16px' }}
          >
            🔗 Link Dependencies
          </button>
          <button onClick={onAddClick} style={{ ...styles.button, backgroundColor: '#4b5563' }}>+ Add New Task</button>
          <button onClick={onRefresh} style={styles.refreshButton}>Refresh</button>
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
                  <span style={{
                      ...styles.badge,
                      backgroundColor: task.status === 'Scheduled' ? '#dbeafe' : // Soft Blue
                                       task.status === 'Completed' ? '#d1fae5' : // Soft Green
                                       '#fef3c7',                                // Yellow (Unscheduled)
                      color: task.status === 'Scheduled' ? '#1e40af' : 
                             task.status === 'Completed' ? '#065f46' : 
                             '#92400e'
                    }}>
                      {task.status || 'Unscheduled'}
                  </span>
                </td>
                <td style={styles.td}>
                  <button 
                    onClick={() => onDeleteTask(task.job_id)}
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
  );
}