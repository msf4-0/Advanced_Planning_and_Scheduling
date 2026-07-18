// src/form/RoutingTemplateForm.jsx
import React from 'react';

export function RoutingTemplateForm({ newTemplate, setNewTemplate, onSubmit, onClose }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setNewTemplate((prev) => ({
      ...prev,
      [name]: name === 'step_sequence' || name === 'standard_duration_minutes' 
        ? parseInt(value, 10) || '' 
        : value
    }));
  };

  const modalStyles = {
    overlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
    content: { backgroundColor: '#fff', padding: '24px', borderRadius: '8px', width: '400px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' },
    formGroup: { marginBottom: '16px', display: 'flex', flexDirection: 'column', gap: '6px' },
    label: { fontWeight: 'bold', fontSize: '14px' },
    input: { padding: '8px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '14px' },
    actions: { display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' },
    saveBtn: { padding: '8px 16px', backgroundColor: '#16a34a', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' },
    cancelBtn: { padding: '8px 16px', backgroundColor: '#6b7280', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }
  };

  return (
    <div style={modalStyles.overlay}>
      <div style={modalStyles.content}>
        <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Add Routing Blueprint</h3>
        <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }}>
          
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Target Item ID</label>
            <input 
              type="text" 
              name="target_item_id" 
              value={newTemplate.target_item_id || ''} 
              onChange={handleChange} 
              placeholder="e.g., prod_servo_motor" 
              required 
              style={modalStyles.input}
            />
          </div>

          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Sequence Number</label>
            <input 
              type="number" 
              name="step_sequence" 
              value={newTemplate.step_sequence || ''} 
              onChange={handleChange} 
              placeholder="e.g., 10" 
              required 
              style={modalStyles.input}
            />
          </div>

          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Required Resource Type</label>
            <select 
              name="required_resource_type" 
              value={newTemplate.required_resource_type || 'Machine'} 
              onChange={handleChange}
              style={modalStyles.input}
            >
              <option value="Machine">Machine</option>
              <option value="Human">Human</option>
            </select>
          </div>

          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Standard Duration (Minutes)</label>
            <input 
              type="number" 
              name="standard_duration_minutes" 
              value={newTemplate.standard_duration_minutes || ''} 
              onChange={handleChange} 
              placeholder="e.g., 45" 
              required 
              style={modalStyles.input}
            />
          </div>

          <div style={modalStyles.actions}>
            <button type="button" onClick={onClose} style={modalStyles.cancelBtn}>Cancel</button>
            <button type="submit" style={modalStyles.saveBtn}>Save Blueprint</button>
          </div>
        </form>
      </div>
    </div>
  );
}