import { useState, useEffect, useCallback } from 'react';
import type { HistoryEntry } from '../types';

export const HISTORY_KEY = 'astrocalculator-history';
export const MAX_HISTORY = 100;

interface HistoryPanelProps {
  onClick: (input: string) => void;
}

export default function HistoryPanel({ onClick }: HistoryPanelProps) {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);

  // Load history from localStorage on mount and whenever tab becomes visible
  useEffect(() => {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      if (raw) {
        setEntries(JSON.parse(raw));
      } else {
        setEntries([]);
      }
    } catch {}
  }, []);

  const clearHistory = useCallback(() => {
    setEntries([]);
    localStorage.removeItem(HISTORY_KEY);
  }, []);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1, overflowY: 'auto', fontSize: 12 }}>
        {entries.length === 0 ? (
          <div style={{ color: 'var(--color-text-muted)', padding: 16, textAlign: 'center' }}>
            No history yet
          </div>
        ) : (
          entries.map(entry => (
            <div
              key={entry.id}
              onClick={() => onClick(entry.input)}
              style={{
                padding: '8px 12px',
                borderBottom: '1px solid #f0f0f0',
                cursor: 'pointer',
                fontFamily: 'monospace',
                fontSize: 12,
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'var(--color-accent-light)')}
              onMouseLeave={e => (e.currentTarget.style.background = '')}
            >
              <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{entry.input}</div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: 10, marginTop: 2 }}>
                {new Date(entry.timestamp).toLocaleString()}
              </div>
            </div>
          ))
        )}
      </div>
      {entries.length > 0 && (
        <button
          onClick={clearHistory}
          style={{
            margin: 8,
            padding: '4px 0',
            background: 'none',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            cursor: 'pointer',
            fontSize: 12,
            color: 'var(--color-text-muted)',
          }}
        >
          Clear history
        </button>
      )}
    </div>
  );
}
