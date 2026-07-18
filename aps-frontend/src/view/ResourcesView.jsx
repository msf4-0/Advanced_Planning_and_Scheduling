import React from 'react';
import { styles } from '../styles';

export function ResourcesView({ resources, loading, onRefresh, onAddClick }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Resources Registry</h2>
        <div style={{display: 'flex', gap: '12px'}}>
          <button onClick={onAddClick} style={{...styles.button, backgroundColor: '#16a34a'}}>+ Add New Resource</button>
          <button onClick={onRefresh} style={styles.refreshButton}>Refresh</button>
        </div>
      </div>
      
      {loading ? (
        <p style={styles.message}>Loading resources...</p>
      ) : resources.length === 0 ? (
        <p style={styles.message}>No resources found. Add a resource to get started.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr style={styles.thRow}>
              <th style={styles.th}>Resource ID</th>
              <th style={styles.th}>Name</th>
              <th style={styles.th}>Type</th>
              <th style={styles.th}>Status</th>
            </tr>
          </thead>
          <tbody>
            {resources.map((resource, index) => (
              <tr key={index} style={styles.tr}>
                <td style={styles.td}><strong>{resource.id}</strong></td>
                <td style={styles.td}>{resource.name}</td>
                <td style={styles.td}>{resource.resource_type}</td>
                <td style={styles.td}>
                  <span style={{
                    color: resource.is_active ? '#16a34a' : '#dc2626',
                    fontWeight: 'bold'
                  }}>
                    {resource.is_active ? 'Active' : 'Inactive'}
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