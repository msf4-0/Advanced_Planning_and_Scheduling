export const styles = {
  container: {
    padding: '24px',
    maxWidth: '1200px',
    margin: '0 auto'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#111827'
  },
  button: {
    color: '#fff',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '6px',
    fontSize: '14px'
  },
  refreshButton: {
    background: 'none',
    border: '1px solid #d1d5db',
    padding: '6px 12px',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  kpiGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '16px',
    marginBottom: '24px'
  },
  card: {
    background: '#fff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
  },
  cardTitle: {
    margin: '0 0 8px 0',
    fontSize: '14px',
    color: '#6b7280',
    textTransform: 'uppercase'
  },
  cardValue: {
    margin: 0,
    fontSize: '24px',
    fontWeight: 'bold'
  },
  mainContent: {
    background: '#fff',
    borderRadius: '8px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    overflow: 'hidden'
  },
  tableCard: {
    padding: '24px'
  },
  tableHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    textAlign: 'left'
  },
  thRow: {
    borderBottom: '2px solid #e5e7eb',
    background: '#f9fafb'
  },
  th: {
    padding: '12px',
    color: '#374151',
    fontWeight: '600'
  },
  tr: {
    borderBottom: '1px solid #e5e7eb'
  },
  td: {
    padding: '12px'
  },
  message: {
    textAlign: 'center',
    padding: '40px',
    color: '#6b7280'
  },
  badge: {
    backgroundColor: '#dcfce7',
    color: '#14532d',
    padding: '4px 8px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500'
  },
  nav: {
    display: 'flex',
    gap: '12px',
    marginTop: '12px'
  },
  navButton: {
    background: 'none',
    border: 'none',
    padding: '8px 16px',
    cursor: 'pointer',
    borderBottom: '2px solid transparent',
    fontSize: '14px',
    color: '#6b7280'
  },
  activeNav: {
    borderBottomColor: '#2563eb',
    color: '#2563eb',
    fontWeight: 'bold'
  },
  formModal: {
    background: 'rgba(0,0,0,0.5)',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
  },
  formContent: {
    background: '#fff',
    padding: '32px',
    borderRadius: '12px',
    width: '100%',
    maxWidth: '500px',
    boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)'
  },
  label: {
    display: 'block',
    marginBottom: '6px',
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151'
  },
  input: {
    width: '100%',
    padding: '10px',
    borderRadius: '6px',
    border: '1px solid #d1d5db',
    marginBottom: '16px',
    fontSize: '14px',
    boxSizing: 'border-box'
  },
  formActions: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '12px',
    marginTop: '12px'
  },
  cancelButton: {
    background: '#f3f4f6',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '500'
  },
  submitButton: {
    background: '#2563eb',
    color: '#fff',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '500'
  },
};