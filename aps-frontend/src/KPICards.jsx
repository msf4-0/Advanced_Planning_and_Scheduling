import React from 'react';
import { styles } from './styles';

export function KPICards({ metrics, optimizing }) {
  return (
    <section style={styles.kpiGrid}>
      <div style={styles.card}>
        <h3 style={styles.cardTitle}>Makespan (C_max)</h3>
        <p style={styles.cardValue}>{metrics.makespan} minutes</p>
      </div>
      <div style={styles.card}>
        <h3 style={styles.cardTitle}>Total Tardiness</h3>
        <p style={styles.cardValue}>{metrics.tardiness} jobs</p>
      </div>
      <div style={styles.card}>
        <h3 style={styles.cardTitle}>System Status</h3>
        <p style={{...styles.cardValue, color: optimizing ? '#d97706' : '#16a34a'}}>
          {optimizing ? 'Re-calculating' : 'Idle / Optimized'}
        </p>
      </div>
    </section>
  );
}