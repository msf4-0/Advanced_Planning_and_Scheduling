import React from 'react';
import { styles } from './styles';

export function MachineForm({ newMachine, setNewMachine, onSubmit, onClose }) {
  return (
    <div style={styles.formModal}>
      <div style={styles.formContent}>
        <h2>Add New Machine</h2>
        <form onSubmit={onSubmit}>
          <label style={styles.label}>Machine ID</label>
          <input
            type="number"
            value={newMachine.machine_id}
            onChange={(e) => setNewMachine({...newMachine, machine_id: e.target.value})}
            style={styles.input}
            required
          />

          <label style={styles.label}>Machine Type</label>
          <input
            type="text"
            value={newMachine.type}
            onChange={(e) => setNewMachine({...newMachine, type: e.target.value})}
            style={styles.input}
            placeholder="e.g., CNC, Lathe, Assembly"
            required
          />

          <label style={styles.label}>Capacity</label>
          <input
            type="number"
            value={newMachine.capacity}
            onChange={(e) => setNewMachine({...newMachine, capacity: e.target.value})}
            style={styles.input}
            min="1"
          />

          <div style={styles.formActions}>
            <button type="button" onClick={onClose} style={styles.cancelButton}>
              Cancel
            </button>
            <button type="submit" style={styles.submitButton}>
              Add Machine
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}