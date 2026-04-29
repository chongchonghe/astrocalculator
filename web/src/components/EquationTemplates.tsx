import { useMemo } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import type { Equation } from '../types';
import equationsData from '../data/equations.json';

const equations: Equation[] = equationsData as Equation[];

interface EquationTemplatesProps {
  query: string;
  onAdd: (params: { symbol: string; default: string }[], expression: string) => void;
}

function renderLatex(latex: string): string {
  try {
    return katex.renderToString(latex, { throwOnError: false, displayMode: true });
  } catch {
    return latex;
  }
}

export default function EquationTemplates({ query, onAdd }: EquationTemplatesProps) {
  const filtered = useMemo(() => {
    if (!query.trim()) return equations;
    const q = query.toLowerCase();
    return equations.filter(eq =>
      eq.title.toLowerCase().includes(q) ||
      eq.tags.some(t => t.toLowerCase().includes(q)) ||
      eq.category.toLowerCase().includes(q) ||
      eq.params.some(p => p.symbol.toLowerCase().includes(q)) ||
      eq.expressions.some(ex => ex.name.toLowerCase().includes(q))
    );
  }, [query]);

  return (
    <div style={{ height: '100%', overflowY: 'auto', fontSize: 'var(--font-sm)' }}>
      {filtered.map(eq => (
        <div
          key={eq.slug}
          style={{ padding: '10px 12px', borderBottom: '1px solid var(--color-border)' }}
        >
          <div style={{ fontWeight: 600, marginBottom: 2 }}>{eq.title}</div>
          <div style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-xs)', marginBottom: 8 }}>
            {eq.category} · {eq.params.map(p => p.symbol).join(', ')}
          </div>

          {eq.expressions.map((ex, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                padding: '6px 0',
                borderTop: i > 0 ? '1px solid #f0f0f0' : 'none',
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-xs)', marginBottom: 2 }}>
                  {ex.name}
                </div>
                {ex.latex ? (
                  <div
                    style={{ fontSize: 'var(--font-sm)' }}
                    dangerouslySetInnerHTML={{ __html: renderLatex(ex.latex) }}
                  />
                ) : (
                  <code style={{ fontSize: 'var(--font-xs)', color: '#555' }}>{ex.expression}</code>
                )}
                {ex.description && (
                  <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)', marginTop: 2 }}>
                    {ex.description}
                  </div>
                )}
              </div>
              <button
                onClick={() => onAdd(eq.params, ex.expression)}
                style={{
                  marginLeft: 8,
                  padding: '2px 10px',
                  fontSize: 'var(--font-xs)',
                  background: 'var(--color-accent)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 'var(--radius)',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                Add
              </button>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
