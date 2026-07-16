import React from 'react';
import { styles } from '../styles';

export function WorkorderView({ workorder, loading, onRefresh, onAddClick, onDeleteTask }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Workorder list</h2>
        <div style={{display: 'flex', gap: '12px'}}>
          <button onClick={onAddClick} style={{...styles.button, backgroundColor: '#16a34a'}}>+ Add New Workorder</button>
          <button onClick={onRefresh} style={styles.refreshButton}>Refresh</button>
        </div>
      </div>
      
      {loading ? (
        <p style={styles.message}>Loading Workorders...</p>
      ) : workorder.length === 0 ? (
        <p style={styles.message}>No unscheduled tasks found. Add a task to get started.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr style={styles.thRow}>
              <th style={styles.th}>Work ID</th>
              <th style={styles.th}>Target item ID</th>
              <th style={styles.th}>Quantity to make</th>
              <th style={styles.th}>Due Date</th>
              <th style={styles.th}>Status</th>
              <th style={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {workorder.map((item, index) => (
              <tr key={index} style={styles.tr}>
                <td style={styles.td}>
                  <strong>{item.workorder_id}</strong>
                </td>
                <td style={styles.td}>
                  {item.target_item_id}
                </td>
                <td style={styles.td}>
                  {item.quantity} units
                </td>
                <td style={styles.td}>
                  {item.due_date || '-'}
                </td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    backgroundColor: item.status === 'Completed' ? '#d1fae5' : '#fef3c7',
                    color: item.status === 'Completed' ? '#065f46' : '#92400e'
                  }}>
                    {item.status || 'Unscheduled'}
                  </span>
                </td>
                <td style={styles.td}>
                  <button 
                    onClick={() => onDeleteTask(item.workorder_id)}
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