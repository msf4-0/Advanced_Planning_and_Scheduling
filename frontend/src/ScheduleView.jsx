import React from 'react';
import { styles } from './styles';

export function ScheduleView({ schedule, loading, onRefresh }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Operational Schedule Outputs</h2>
        <button onClick={onRefresh} style={styles.refreshButton}>Refresh Data</button>
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
                  <span style={{
                      ...styles.badge,
                      backgroundColor: task.status === 'Completed' ? '#d1fae5' : 
                                       task.status === 'In Progress' ? '#fee2e2' : 
                                       '#dbeafe', // Scheduled default
                      color: task.status === 'Completed' ? '#065f46' : 
                             task.status === 'In Progress' ? '#991b1b' : 
                             '#1e40af'
                    }}>
                      {task.status || 'Scheduled'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}