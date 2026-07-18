import React from 'react';
import { styles } from '../styles';

export function TaskForm({ newTask, setNewTask, onSubmit, onClose }) {
  return (
    <div style={styles.formModal}>
      <div style={styles.formContent}>
        <h2>Add New Task</h2>
        
        {/* Validation subtitle indicator */}
        <p style={{ color: '#ef4444', fontSize: '13px', marginBottom: '15px' }}>
          * Indicates a required operational field
        </p>

        <form onSubmit={onSubmit}>
          {/* 1. JOB ID - REQUIRED */}
          <label style={styles.label}>
            Job ID (Unique String) <span style={{ color: '#ef4444' }}>*</span>
          </label>
          <input
            type="text"
            value={newTask.job_id || ''}
            onChange={(e) => setNewTask({...newTask, job_id: e.target.value})}
            style={styles.input}
            placeholder="e.g., OP-101"
            required
          />

          {/* 2. WORK ORDER ID - REQUIRED */}
          <label style={styles.label}>
            Work Order ID <span style={{ color: '#ef4444' }}>*</span>
          </label>
          <input
            type="text"
            value={newTask.work_order_id || ''}
            onChange={(e) => setNewTask({...newTask, work_order_id: e.target.value})}
            style={styles.input}
            placeholder="e.g., MFG-WO-2026-00001"
            required
          />

          {/* 3. DURATION - REQUIRED */}
          <label style={styles.label}>
            Duration (Hours) <span style={{ color: '#ef4444' }}>*</span>
          </label>
          <input
            type="number"
            value={newTask.duration || ''}
            onChange={(e) => setNewTask({...newTask, duration: e.target.value})}
            style={styles.input}
            min="1"
            required
          />

          {/* 4. MACHINE ID - OPTIONAL */}
          <label style={styles.label}>
            Assign to Specific Machine ID <span style={{ color: '#6b7280', fontSize: '12px', fontWeight: 'normal' }}>(Optional)</span>
          </label>
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
