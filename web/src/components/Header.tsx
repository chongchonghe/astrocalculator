// web/src/components/Header.tsx
import { useCalculator } from '../hooks/useCalculator';

export default function Header() {
  const { ready, loading } = useCalculator();

  return (
    <header style={{
      height: 40,
      display: 'flex',
      alignItems: 'center',
      padding: '0 16px',
      background: 'var(--color-surface)',
      borderBottom: '1px solid var(--color-border)',
      gap: 12,
    }}>
      <h1 style={{ fontSize: 16, fontWeight: 700 }}>AstroCalculator</h1>
      <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
        {loading ? 'Loading engine...' : ready ? 'Ready' : 'Error'}
      </span>
      {loading && <div className="spinner" style={{
        width: 12, height: 12, border: '2px solid #e0e0e0',
        borderTopColor: 'var(--color-accent)', borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </header>
  );
}
