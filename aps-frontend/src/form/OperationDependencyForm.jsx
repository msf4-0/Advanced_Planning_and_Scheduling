// src/form/OperationDependencyForm.jsx
import React, { useState } from 'react';

export function OperationDependencyForm({ availableOperations, onSubmit, onClose }) {
  const [upstreamId, setUpstreamId] = useState('');
  const [downstreamId, setDownstreamId] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!upstreamId || !downstreamId) {
      setError('Please select both an upstream and a downstream operation.');
      return;
    }

    if (upstreamId === downstreamId) {
      setError('An operation cannot depend on itself (circular dependency loop).');
      return;
    }

    onSubmit({
      upstream_op_id: upstreamId,
      downstream_op_id: downstreamId
    });
  };

  const modalStyles = {
    overlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1100 },
    content: { backgroundColor: '#fff', padding: '24px', borderRadius: '8px', width: '400px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' },
    formGroup: { marginBottom: '16px', display: 'flex', flexDirection: 'column', gap: '6px' },
    label: { fontWeight: 'bold', fontSize: '14px', color: '#374151' },
    select: { padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', fontSize: '14px', backgroundColor: '#fff' },
    actions: { display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' },
    saveBtn: { padding: '8px 16px', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: '500' },
    cancelBtn: { padding: '8px 16px', backgroundColor: '#6b7280', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' },
    errorText: { color: '#dc2626', fontSize: '13px', marginBottom: '12px', fontWeight: '500' }
  };

  return (
    <div style={modalStyles.overlay}>
      <div style={modalStyles.content}>
        <h3 style={{ marginTop: 0, marginBottom: '8px' }}>Link Operation Dependency</h3>
        <p style={{ color: '#6b7280', fontSize: '13px', marginBottom: '20px' }}>
          Establish an ordering constraint between two active operations.
        </p>

        {error && <div style={modalStyles.errorText}>{error}</div>}

        <form onSubmit={handleSubmit}>
          {/* Upstream Predecessor Selection */}
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>1. Upstream Operation (Must Finish First)</label>
            <select 
              value={upstreamId} 
              onChange={(e) => setUpstreamId(e.target.value)}
              style={modalStyles.select}
            >
              <option value="">-- Select Prerequisite Operation --</option>
              {availableOperations.map((op) => (
                <option key={op.raw_id} value={op.raw_id}>
                  {op.job_id} (WO: {op.work_order_id || 'Manual'})
                </option>
              ))}
            </select>
          </div>

          {/* Downstream Successor Selection */}
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>2. Downstream Operation (Blocked Step)</label>
            <select 
              value={downstreamId} 
              onChange={(e) => setDownstreamId(e.target.value)}
              style={modalStyles.select}
            >
              <option value="">-- Select Blocked Operation --</option>
              {availableOperations.map((op) => (
                <option key={op.raw_id} value={op.raw_id}>
                  {op.job_id} (WO: {op.work_order_id || 'Manual'})
                </option>
              ))}
            </select>
          </div>

          <div style={modalStyles.actions}>
            <button type="button" onClick={onClose} style={modalStyles.cancelBtn}>Cancel</button>
            <button type="submit" style={modalStyles.saveBtn}>Connect Operations</button>
          </div>
        </form>
      </div>
    </div>
  );
}