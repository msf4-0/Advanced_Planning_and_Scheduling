// src/view/RoutingTemplatesView.jsx
import React from 'react';
import { styles } from '../styles';

export function RoutingTemplatesView({ data, loading, onRefresh, onAddClick }) {
  return (
    <div style={styles.tableCard}>
      <div style={styles.tableHeader}>
        <h2>Manufacturing Routing Blueprints</h2>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button onClick={onAddClick} style={{ ...styles.refreshButton, backgroundColor: '#16a34a', color: '#fff' }}>
            + Add Template
          </button>
          <button onClick={onRefresh} style={styles.refreshButton}>
            Refresh Blueprints
          </button>
        </div>
      </div>
      
      {loading ? (
        <p style={styles.message}>Loading routing templates...</p>
      ) : data.length === 0 ? (
        <p style={styles.message}>No routing configurations found.</p>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr style={styles.thRow}>
              <th style={styles.th}>Product ID</th>
              <th style={styles.th}>Product Name</th>
              <th style={styles.th}>SKU</th>
              <th style={styles.th}>Sequence No.</th>
              <th style={styles.th}>Required Resource</th>
              <th style={styles.th}>Std. Duration</th>
            </tr>
          </thead>
          <tbody>
            {data.map((template) => (
              <tr key={template.id} style={styles.tr}>
                <td style={styles.td}><strong>{template.target_item_id}</strong></td>
                <td style={styles.td}>{template.item_name || 'N/A'}</td>
                <td style={styles.td}><code>{template.item_sku || 'N/A'}</code></td>
                <td style={styles.td}>{template.step_sequence}</td>
                <td style={styles.td}>{template.required_resource_type}</td>
                <td style={styles.td}>{template.standard_duration_minutes} mins</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}