// web/src/components/UnitsTable.tsx
import { useMemo } from 'react';
import type { UnitEntry } from '../types';
import unitsData from '../data/units.json';

const units: UnitEntry[] = unitsData as UnitEntry[];

interface UnitsTableProps {
  query: string;
  onClick: (name: string) => void;
}

export default function UnitsTable({ query, onClick }: UnitsTableProps) {
  const grouped = useMemo(() => {
    const q = query.toLowerCase().trim();
    const filtered = q
      ? units.filter(u => u.name.toLowerCase().includes(q) || u.category.toLowerCase().includes(q))
      : units;
    const map = new Map<string, UnitEntry[]>();
    for (const u of filtered) {
      const list = map.get(u.category) || [];
      list.push(u);
      map.set(u.category, list);
    }
    return map;
  }, [query]);

  return (
    <div style={{ height: '100%', overflowY: 'auto', fontSize: 'var(--font-sm)' }}>
      {Array.from(grouped.entries()).map(([category, entries]) => (
        <div key={category}>
          <div style={{
            padding: '6px 12px',
            fontWeight: 600,
            color: 'var(--color-text-muted)',
            background: '#f8fafc',
            position: 'sticky', top: 0,
            borderBottom: '1px solid var(--color-border)',
          }}>
            {category}
          </div>
          {entries.map(u => (
            <div
              key={u.name}
              onClick={() => onClick(u.name)}
              style={{
                padding: '5px 12px',
                borderBottom: '1px solid #f5f5f5',
                cursor: 'pointer',
                fontFamily: 'monospace',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'var(--color-accent-light)')}
              onMouseLeave={e => (e.currentTarget.style.background = '')}
            >
              {u.name}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
