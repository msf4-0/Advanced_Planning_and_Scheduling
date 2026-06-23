import React from 'react';
import { styles } from './styles';

export function TaskForm({ newTask, setNewTask, onSubmit, onClose }) {
  return (
    <div style={styles.formModal}>
      <div style={styles.formContent}>
        <h2>Add New Task</h2>
        <form onSubmit={onSubmit}>
          <label style={styles.label}>Job ID (Unique String)</label>
          <input
            type="text"
            value={newTask.job_id || ''}
            onChange={(e) => setNewTask({...newTask, job_id: e.target.value})}
            style={styles.input}
            placeholder="e.g., OP-101"
            required
          />

          <label style={styles.label}>Work Order ID</label>
          <input
            type="text"
            value={newTask.work_order_id || ''}
            onChange={(e) => setNewTask({...newTask, work_order_id: e.target.value})}
            style={styles.input}
            placeholder="e.g., MFG-WO-2026-00001"
            required
          />

          <label style={styles.label}>Duration (Hours)</label>
          <input
            type="number"
            value={newTask.duration || ''}
            onChange={(e) => setNewTask({...newTask, duration: e.target.value})}
            style={styles.input}
            min="1"
            required
          />

          <label style={styles.label}>Predecessor Job ID(s)</label>
          <input
            type="text"
            value={newTask.predecessor || ''}
            onChange={(e) => setNewTask({...newTask, predecessor: e.target.value})}
            style={styles.input}
            placeholder="e.g., OP-100, OP-099 (Separate with commas)"
          />

          <label style={styles.label}>Due Date (Minutes Offset)</label>
          <input
            type="number"
            value={newTask.due_date || ''}
            onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
            style={styles.input}
            min="0"
          />

          <label style={styles.label}>Assign to Specific Machine ID (optional)</label>
          <input
            type="text"
            value={newTask.resources || ''}
            onChange={(e) => setNewTask({...newTask, resources: e.target.value})}
            style={styles.input}
            placeholder="e.g., MCH-ALPHA (Leave blank for any)"
          />

          <div style={styles.formActions}>
            <button type="button" onClick={onClose} style={styles.cancelButton}>
              Cancel
            </button>
            <button type="submit" style={styles.submitButton}>
              Add Task
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
