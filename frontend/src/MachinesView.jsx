import React from 'react';
import { styles } from './styles';

export function MachinesView({ machines, loading, onRefresh, onAddClick }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Machines & Resources</h2>
        <div style={{display: 'flex', gap: '12px'}}>
          <button onClick={onAddClick} style={{...styles.button, backgroundColor: '#16a34a'}}>+ Add New Machine</button>
          <button onClick={onRefresh} style={styles.refreshButton}>Refresh</button>
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
  );
}