import React from 'react';
import { styles } from '../styles';

export function ResourceForm({ newResource, setNewResource, onSubmit, onClose }) {
  return (
    <div style={styles.formModal}>
      <div style={styles.formContent}>
        <h2>Add New Resource</h2>
        <form onSubmit={onSubmit}>
          <label style={styles.label}>Resource ID</label>
          <input
            type="text"
            value={newResource.id}
            onChange={(e) => setNewResource({...newResource, id: e.target.value})}
            style={styles.input}
            placeholder="e.g., R-101"
            required
          />

          <label style={styles.label}>Resource Name</label>
          <input
            type="text"
            value={newResource.name}
            onChange={(e) => setNewResource({...newResource, name: e.target.value})}
            style={styles.input}
            placeholder="e.g., Workcenter Alpha"
            required
          />

          <label style={styles.label}>Resource Type</label>
          <input
            type="text"
            value={newResource.resource_type}
            onChange={(e) => setNewResource({...newResource, resource_type: e.target.value})}
            style={styles.input}
            placeholder="e.g., CNC, Operator, Assembly Line"
            required
          />

          <div style={styles.formActions}>
            <button type="button" onClick={onClose} style={styles.cancelButton}>
              Cancel
            </button>
            <button type="submit" style={styles.submitButton}>
              Add Resource
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}