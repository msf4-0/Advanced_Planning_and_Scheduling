// src/view/ItemsView.jsx
import React from 'react';
import { styles } from '../styles';

export function ItemsView({ items, loading, onRefresh, onAddClick, onDeleteItem }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Product Item Master Catalog</h2>
        <div style={{display: 'flex', gap: '12px'}}>
          <button onClick={onAddClick} style={{...styles.button, backgroundColor: '#16a34a'}}>+ Add New Item</button>
          <button onClick={onRefresh} style={styles.refreshButton}>Refresh</button>
        </div>
      </div>
      
      {loading ? (
        <p style={styles.message}>Loading catalog records...</p>
      ) : items.length === 0 ? (
        <p style={styles.message}>No item templates found. Add a master record to get started.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr style={styles.thRow}>
              <th style={styles.th}>Item ID</th>
              <th style={styles.th}>Item Name</th>
              <th style={styles.th}>SKU Registry Code</th>
              <th style={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, index) => (
              <tr key={index} style={styles.tr}>
                <td style={styles.td}><strong>{item.id}</strong></td>
                <td style={styles.td}>{item.name}</td>
                <td style={styles.td}>
                  <span style={{...styles.badge, backgroundColor: '#f3f4f6', color: '#374151'}}>
                    {item.sku}
                  </span>
                </td>
                <td style={styles.td}>
                  <button 
                    onClick={() => onDeleteItem(item.id)}
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