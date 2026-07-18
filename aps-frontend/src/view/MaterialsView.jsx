// src/view/MaterialsView.jsx
import React from 'react';
import { styles } from '../styles';

export function MaterialsView({ materials, loading, onRefresh, onAddClick, onDeleteMaterial }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Raw Materials & Inventory Catalog</h2>
        <div style={{display: 'flex', gap: '12px'}}>
          <button onClick={onAddClick} style={{...styles.button, backgroundColor: '#16a34a'}}>+ Add Material</button>
          <button onClick={onRefresh} style={styles.refreshButton}>Refresh</button>
        </div>
      </div>
      
      {loading ? (
        <p style={styles.message}>Loading raw material metrics...</p>
      ) : materials.length === 0 ? (
        <p style={styles.message}>No materials found in inventory ledger.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr style={styles.thRow}>
              <th style={styles.th}>Material ID</th>
              <th style={styles.th}>Material Name</th>
              <th style={styles.th}>Quantity Available</th>
              <th style={styles.th}>Lead Time Offset (Mins)</th>
              <th style={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {materials.map((mat, index) => (
              <tr key={index} style={styles.tr}>
                <td style={styles.td}><strong>{mat.id}</strong></td>
                <td style={styles.td}>{mat.name}</td>
                <td style={styles.td}>
                  <span style={{...styles.badge, backgroundColor: '#eff6ff', color: '#1e40af'}}>
                    {Number(mat.quantity_available).toFixed(4)}
                  </span>
                </td>
                <td style={styles.td}>{mat.available_date_minutes || 0} mins</td>
                <td style={styles.td}>
                  <button 
                    onClick={() => onDeleteMaterial(mat.id)}
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