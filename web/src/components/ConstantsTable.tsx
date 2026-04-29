// web/src/components/ConstantsTable.tsx
import { useMemo } from 'react';
import type { ConstantEntry } from '../types';
import constantsData from '../data/constants.json';

const constants: ConstantEntry[] = constantsData as ConstantEntry[];

interface ConstantsTableProps {
  query: string;
  onClick: (symbol: string) => void;
}

export default function ConstantsTable({ query, onClick }: ConstantsTableProps) {
  const filtered = useMemo(() => {
    if (!query.trim()) return constants;
    const q = query.toLowerCase();
    return constants.filter(c =>
      c.symbol.toLowerCase().includes(q) ||
      c.name.toLowerCase().includes(q)
    );
  }, [query]);

  return (
    <div style={{ height: '100%', overflowY: 'auto', fontSize: 'var(--font-sm)' }}>
      <div style={{
        display: 'flex',
        padding: '6px 12px',
        borderBottom: '1px solid var(--color-border)',
        fontWeight: 600,
        color: 'var(--color-text-muted)',
        position: 'sticky', top: 0, background: 'var(--color-surface)',
      }}>
        <span style={{ flex: 1 }}>Symbol</span>
        <span style={{ flex: 2 }}>Name</span>
        <span style={{ flex: 1.5, textAlign: 'right' }}>Value</span>
        <span style={{ flex: 1, textAlign: 'right' }}>Unit</span>
      </div>
      {filtered.map(c => (
        <div
          key={c.symbol}
          onClick={() => onClick(c.symbol)}
          style={{
            display: 'flex',
            padding: '5px 12px',
            borderBottom: '1px solid #f5f5f5',
            cursor: 'pointer',
          }}
          onMouseEnter={e => (e.currentTarget.style.background = 'var(--color-accent-light)')}
          onMouseLeave={e => (e.currentTarget.style.background = '')}
        >
          <span style={{ flex: 1, fontWeight: 600, fontFamily: 'monospace' }}>{c.symbol}</span>
          <span style={{ flex: 2, color: 'var(--color-text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.name}</span>
          <span style={{ flex: 1.5, textAlign: 'right', fontFamily: 'monospace', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.value.toExponential(3)}</span>
          <span style={{ flex: 1, textAlign: 'right', color: 'var(--color-text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.unit}</span>
        </div>
      ))}
    </div>
  );
}
