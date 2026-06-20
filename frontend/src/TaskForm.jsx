import React from 'react';
import { styles } from './styles';

export function TaskForm({ newTask, setNewTask, onSubmit, onClose }) {
  return (
    <div style={styles.formModal}>
      <div style={styles.formContent}>
        <h2>Add New Task</h2>
        <form onSubmit={onSubmit}>
          <label style={styles.label}>Job ID</label>
          <input
            type="text"
            value={newTask.job_id}
            onChange={(e) => setNewTask({...newTask, job_id: e.target.value})}
            style={styles.input}
            required
          />

          <label style={styles.label}>Duration (hrs)</label>
          <input
            type="number"
            value={newTask.duration}
            onChange={(e) => setNewTask({...newTask, duration: e.target.value})}
            style={styles.input}
            min="1"
          />

          <label style={styles.label}>Predecessor Job ID</label>
          <input
            type="text"
            value={newTask.predecessor}
            onChange={(e) => setNewTask({...newTask, predecessor: e.target.value})}
            style={styles.input}
          />

          <label style={styles.label}>Due Date</label>
          <input
            type="number"
            value={newTask.due_date}
            onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
            style={styles.input}
          />

          <label style={styles.label}>Lock to Specific Machine (optional)</label>
          <input
            type="number"
            value={newTask.resources}
            onChange={(e) => setNewTask({...newTask, resources: e.target.value})}
            style={styles.input}
            placeholder="Leave empty to allow any machine"
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