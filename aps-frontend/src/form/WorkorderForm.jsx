// src/form/WorkorderForm.jsx
import React from 'react';
import { styles } from '../styles';

export function WorkorderForm({ newWorkorder, setNewWorkorder, availableItems = [], onSubmit, onClose }) {
  const hasNoItems = availableItems.length === 0;

  return (
    <div style={styles.formModal}>
      <div style={styles.formContent}>
        <h2>Add New Workorder</h2>
        <form onSubmit={onSubmit}>
          
          <label style={styles.label}>Work Order ID</label>
          <input
            type="text"
            value={newWorkorder.work_order_id}
            onChange={(e) => setNewWorkorder({...newWorkorder, work_order_id: e.target.value})}
            style={styles.input}
            placeholder="e.g., WO-2026-001"
            required
          />

          <label style={styles.label}>Target Item ID</label>
          <select
            value={newWorkorder.target_item_id}
            onChange={(e) => setNewWorkorder({...newWorkorder, target_item_id: e.target.value})}
            style={{
              ...styles.input,
              backgroundColor: hasNoItems ? '#f3f4f6' : '#fff',
              color: hasNoItems ? '#9ca3af' : '#000',
              cursor: hasNoItems ? 'not-allowed' : 'default'
            }}
            disabled={hasNoItems}
            required
          >
            {hasNoItems ? (
              <option value="">⚠️ Hey, you need an item before making a workorder!</option>
            ) : (
              <>
                <option value="">-- Select Target SKU Item --</option>
                {availableItems.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name ? `${item.name} (${item.id})` : item.id}
                  </option>
                ))}
              </>
            )}
          </select>

          <label style={styles.label}>Quantity to Make</label>
          <input
            type="number"
            value={newWorkorder.quantity_to_make || ''}
            onChange={(e) => setNewWorkorder({...newWorkorder, quantity_to_make: parseInt(e.target.value) || 0})}
            style={styles.input}
            min="1"
            required
          />

          <label style={styles.label}>Due Date</label>
          <input
            type="date"
            value={newWorkorder.due_date}
            onChange={(e) => setNewWorkorder({...newWorkorder, due_date: e.target.value})}
            style={styles.input}
            required
          />

          <div style={styles.formActions}>
            <button type="button" onClick={onClose} style={styles.cancelButton}>
              Cancel
            </button>
            <button 
              type="submit" 
              style={{
                ...styles.submitButton,
                backgroundColor: hasNoItems ? '#9ca3af' : styles.submitButton.backgroundColor,
                cursor: hasNoItems ? 'not-allowed' : 'pointer'
              }}
              disabled={hasNoItems}
            >
              Add Workorder
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}