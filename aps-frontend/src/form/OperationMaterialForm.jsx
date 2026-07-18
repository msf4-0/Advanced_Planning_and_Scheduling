// src/form/OperationMaterialForm.jsx
import React, { useState } from 'react';

export function OperationMaterialForm({ availableOperations, availableMaterials, onSubmit, onClose }) {
  const [opId, setOpId] = useState('');
  const [materialId, setMaterialId] = useState('');
  const [qty, setQty] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!opId || !materialId || !qty) {
      setError('All mapping fields are required.');
      return;
    }

    if (parseFloat(qty) <= 0) {
      setError('Allocated requirements quantity must be greater than zero.');
      return;
    }

    onSubmit({
      operation_id: opId,
      material_id: materialId,
      quantity_required: qty
    });
  };

  const modalStyles = {
    overlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1100 },
    content: { backgroundColor: '#fff', padding: '24px', borderRadius: '8px', width: '400px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' },
    formGroup: { marginBottom: '16px', display: 'flex', flexDirection: 'column', gap: '6px' },
    label: { fontWeight: 'bold', fontSize: '14px', color: '#374151' },
    select: { padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', fontSize: '14px', backgroundColor: '#fff' },
    input: { padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db', fontSize: '14px' },
    actions: { display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' },
    saveBtn: { padding: '8px 16px', backgroundColor: '#16a34a', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: '500' },
    cancelBtn: { padding: '8px 16px', backgroundColor: '#6b7280', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' },
    errorText: { color: '#dc2626', fontSize: '13px', marginBottom: '12px', fontWeight: '500' }
  };

  return (
    <div style={modalStyles.overlay}>
      <div style={modalStyles.content}>
        <h3 style={{ marginTop: 0, marginBottom: '8px' }}>Allocate BOM Materials</h3>
        <p style={{ color: '#6b7280', fontSize: '13px', marginBottom: '20px' }}>
          Assign raw inventory stock tracking directly to a production task[cite: 27].
        </p>

        {error && <div style={modalStyles.errorText}>{error}</div>}

        <form onSubmit={handleSubmit}>
          {/* Operation Selector */}
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Target Operation ID</label>
            <select value={opId} onChange={(e) => setOpId(e.target.value)} style={modalStyles.select}>
              <option value="">-- Select Operation Target --</option>
              {availableOperations.map((op) => (
                <option key={op.raw_id} value={op.raw_id}>
                  {op.job_id} {op.work_order_id ? `(WO: ${op.work_order_id})` : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Material Ledger Item Selector */}
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Material Allocation Item</label>
            <select value={materialId} onChange={(e) => setMaterialId(e.target.value)} style={modalStyles.select}>
              <option value="">-- Select Inventory Sku --</option>
              {availableMaterials.map((mat) => (
                <option key={mat.id} value={mat.id}>{mat.name || mat.id} ({mat.id})</option>
              ))}
            </select>
          </div>

          {/* Numeric Quantity */}
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Quantity Required</label>
            <input 
              type="number" 
              step="any"
              placeholder="e.g., 1.0"
              value={qty} 
              onChange={(e) => setQty(e.target.value)} 
              style={modalStyles.input}
            />
          </div>

          <div style={modalStyles.actions}>
            <button type="button" onClick={onClose} style={modalStyles.cancelBtn}>Cancel</button>
            <button type="submit" style={modalStyles.saveBtn}>Allocate Stock</button>
          </div>
        </form>
      </div>
    </div>
  );
}