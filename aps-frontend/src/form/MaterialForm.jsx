// src/form/MaterialForm.jsx
import React from 'react';
import { styles } from '../styles';

export function MaterialForm({ newMaterial, setNewMaterial, onSubmit, onClose }) {
  return (
    <div style={styles.formModal}>
      <div style={styles.formContent}>
        <h2>Add Material Inventory Record</h2>
        
        <form onSubmit={onSubmit}>
          {/* Material ID */}
          <label style={styles.label}>Material ID *</label>
          <input
            type="text"
            value={newMaterial.id || ''}
            onChange={(e) => setNewMaterial({...newMaterial, id: e.target.value})}
            style={styles.input}
            placeholder="e.g., MAT-ALUM-01"
            required
          />

          {/* Material Name */}
          <label style={styles.label}>Material Name *</label>
          <input
            type="text"
            value={newMaterial.name || ''}
            onChange={(e) => setNewMaterial({...newMaterial, name: e.target.value})}
            style={styles.input}
            placeholder="e.g., Aluminum Sheet 6061"
            required
          />

          {/* Quantity Available */}
          <label style={styles.label}>Quantity Available</label>
          <input
            type="number"
            step="0.0001"
            value={newMaterial.quantity_available || ''}
            onChange={(e) => setNewMaterial({...newMaterial, quantity_available: e.target.value})}
            style={styles.input}
            placeholder="0.0000"
          />

          {/* Available Date Minutes */}
          <label style={styles.label}>Available Lead Time (Minutes)</label>
          <input
            type="number"
            value={newMaterial.available_date_minutes || ''}
            onChange={(e) => setNewMaterial({...newMaterial, available_date_minutes: e.target.value})}
            style={styles.input}
            placeholder="0"
          />

          <div style={styles.formActions}>
            <button type="button" onClick={onClose} style={styles.cancelButton}>Cancel</button>
            <button type="submit" style={styles.submitButton}>Save Material</button>
          </div>
        </form>
      </div>
    </div>
  );
}