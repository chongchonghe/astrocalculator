import { useState } from 'react';
import { useCalculator } from '../hooks/useCalculator';

export default function Header() {
  const { ready, loading } = useCalculator();
  const [showHelp, setShowHelp] = useState(false);

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

      {/* Help popup */}
      <div
        style={{ position: 'relative' }}
        onMouseEnter={() => setShowHelp(true)}
        onMouseLeave={() => setShowHelp(false)}
      >
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 18, height: 18,
          borderRadius: '50%',
          background: 'var(--color-border)',
          color: 'var(--color-text-muted)',
          fontSize: 11,
          fontWeight: 600,
          cursor: 'help',
          userSelect: 'none',
        }}>?</span>
        {showHelp && (
          <div style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            marginTop: 8,
            width: 280,
            padding: '12px 14px',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
            fontSize: 12,
            lineHeight: 1.6,
            color: 'var(--color-text)',
            zIndex: 100,
          }}>
            <p style={{ marginBottom: 6 }}>
              <strong>AstroCalculator</strong> — a calculator for astronomers and physicists.
            </p>
            <p style={{ marginBottom: 6 }}>
              Type expressions using physical constants (e.g. <code>m_e c^2 in MeV</code>),
              or browse the <strong>Equations</strong> tab and press <strong>Add</strong> to insert
              a pre-built equation with default parameters.
            </p>
            <p style={{ marginBottom: 6 }}>
              <strong>Cmd+Enter</strong> to evaluate &middot; <strong>Cmd+K</strong> to search &middot; <strong>Cmd+J</strong> to focus editor
            </p>
            <p style={{ color: 'var(--color-text-muted)', fontSize: 11 }}>
              Author: ChongChong He (<a href="mailto:chongchong.he@anu.edu.au" style={{ color: 'var(--color-accent)' }}>chongchong.he@anu.edu.au</a>)
            </p>
          </div>
        )}
      </div>

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
