import { useRef, useEffect } from 'react';
import { useCalculator } from '../hooks/useCalculator';

export default function DebugPanel() {
  const { logs, ready, error } = useCalculator();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const statusColor = error ? 'var(--color-error)' : ready ? 'var(--color-success)' : '#f59e0b';
  const statusText = error ? 'ERROR' : ready ? 'READY' : 'LOADING';

  return (
    <div style={{
      borderTop: '1px solid var(--color-border)',
      background: '#0f172a',
      color: '#e2e8f0',
      fontFamily: 'monospace',
      fontSize: 'var(--font-xs)',
      maxHeight: 160,
      display: 'flex',
      flexDirection: 'column',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '4px 10px',
        background: '#1e293b',
        borderBottom: '1px solid #334155',
      }}>
        <span style={{ fontWeight: 600 }}>Debug Log</span>
        <span style={{ color: statusColor, fontSize: 'var(--font-xs)' }}>{statusText}</span>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '4px 10px', lineHeight: 1.5 }}>
        {logs.map((entry) => (
          <div key={entry.id} style={{ color: entry.text.startsWith('ERROR') ? '#f87171' : entry.text.startsWith('FATAL') ? '#ef4444' : '#94a3b8' }}>
            <span style={{ color: '#475569', marginRight: 6 }}>{new Date(entry.time).toLocaleTimeString()}</span>
            {entry.text}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
