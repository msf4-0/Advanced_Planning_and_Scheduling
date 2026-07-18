// src/form/ItemForm.jsx
import React from 'react';
import { styles } from '../styles';

export function ItemForm({ newItem, setNewItem, onSubmit, onClose }) {
  return (
    <div style={styles.formModal}>
      <div style={styles.formContent}>
        <h2>Add New Item Master SKU</h2>
        
        <p style={{ color: '#ef4444', fontSize: '13px', marginBottom: '15px' }}>
          * Indicates a required database master record field
        </p>

        <form onSubmit={onSubmit}>
          {/* 1. ITEM ID - REQUIRED */}
          <label style={styles.label}>
            Item ID (Unique Identification Code) <span style={{ color: '#ef4444' }}>*</span>
          </label>
          <input
            type="text"
            value={newItem.id || ''}
            onChange={(e) => setNewItem({...newItem, id: e.target.value})}
            style={styles.input}
            placeholder="e.g., prod_servo_motor"
            required
          />

          {/* 2. ITEM NAME - REQUIRED */}
          <label style={styles.label}>
            Item Name <span style={{ color: '#ef4444' }}>*</span>
          </label>
          <input
            type="text"
            value={newItem.name || ''}
            onChange={(e) => setNewItem({...newItem, name: e.target.value})}
            style={styles.input}
            placeholder="e.g., High-Torque Servo Motor"
            required
          />

          {/* 3. SKU - REQUIRED & UNIQUE */}
          <label style={styles.label}>
            SKU Code <span style={{ color: '#ef4444' }}>*</span>
          </label>
          <input
            type="text"
            value={newItem.sku || ''}
            onChange={(e) => setNewItem({...newItem, sku: e.target.value})}
            style={styles.input}
            placeholder="e.g., SKU-SERVO-001"
            required
          />

          <div style={styles.formActions}>
            <button type="button" onClick={onClose} style={styles.cancelButton}>
              Cancel
            </button>
            <button type="submit" style={styles.submitButton}>
              Add Item
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}