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
      <h1 style={{ fontSize: 'var(--font-lg)', fontWeight: 700 }}>AstroCalculator</h1>

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
          fontSize: 'var(--font-xs)',
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
            width: 320,
            padding: '14px 16px',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
            fontSize: 'var(--font-base)',
            lineHeight: 1.6,
            color: 'var(--color-text)',
            zIndex: 100,
          }}>
            <p style={{ fontWeight: 700, marginBottom: 8 }}>AstroCalculator</p>

            <p style={{ marginBottom: 10, color: 'var(--color-text-muted)' }}>
              A calculator for astronomers and physicists. Type expressions using
              physical constants and units, e.g. <code style={{ background: '#f0f0f0', padding: '1px 4px', borderRadius: 3 }}>m_e c^2 in MeV</code>.
              Use the <strong>Equations</strong> tab to insert pre-built templates.
            </p>

            <p style={{ fontWeight: 600, marginBottom: 6, fontSize: 'var(--font-xs)', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)' }}>
              Keyboard shortcuts
            </p>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: 12, fontSize: 'var(--font-sm)' }}>
              {([
                ['Cmd+Enter', 'Evaluate expression'],
                ['Cmd+K', 'Focus search bar'],
                ['Cmd+J', 'Focus editor'],
              ] as [string, string][]).map(([key, desc]) => (
                <tr key={key}>
                  <td style={{ paddingBottom: 3, paddingRight: 12, whiteSpace: 'nowrap' }}>
                    <kbd style={{ background: '#f0f0f0', border: '1px solid #ccc', borderRadius: 3, padding: '1px 5px', fontSize: 'var(--font-xs)' }}>{key}</kbd>
                  </td>
                  <td style={{ paddingBottom: 3, color: 'var(--color-text-muted)' }}>{desc}</td>
                </tr>
              ))}
            </table>

            <p style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)', borderTop: '1px solid var(--color-border)', paddingTop: 8 }}>
              Author: ChongChong He &middot; <a href="mailto:chongchong.he@anu.edu.au" style={{ color: 'var(--color-accent)' }}>chongchong.he@anu.edu.au</a>
            </p>
          </div>
        )}
      </div>

      <span style={{ fontSize: 'var(--font-sm)', color: 'var(--color-text-muted)' }}>
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
