import { useState, useEffect, useCallback } from 'react';
import { useCalculator } from '../hooks/useCalculator';
import type { CalculatorResult } from '../types';

export default function ResultDisplay() {
  const { evaluate, ready } = useCalculator();
  const [result, setResult] = useState<CalculatorResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail as string;
      if (!detail.trim()) return;
      setEvaluating(true);
      setError(null);
      evaluate(detail).then(res => {
        setResult(res);
        setEvaluating(false);
      }).catch(err => {
        setError(String(err));
        setEvaluating(false);
      });
    };
    window.addEventListener('evaluate', handler);
    return () => window.removeEventListener('evaluate', handler);
  }, [evaluate]);

  const copyText = useCallback((text: string) => {
    navigator.clipboard.writeText(text).catch(() => {});
  }, []);

  if (!result && !error && !evaluating) {
    return (
      <div style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-base)', textAlign: 'center', padding: 20 }}>
        {ready
          ? 'Cmd+Enter to evaluate'
          : 'Loading scientific engine...'}
      </div>
    );
  }

  if (evaluating) {
    return <div style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-base)', textAlign: 'center', padding: 20 }}>Evaluating...</div>;
  }

  if (error) {
    return (
      <div style={{ background: '#fff5f5', padding: 12, borderRadius: 'var(--radius)', color: 'var(--color-error)', fontSize: 'var(--font-base)' }}>
        {error}
      </div>
    );
  }

  if (!result) return null;

  const cards = [
    { label: 'PARSED', value: result.parsed, color: 'var(--color-parsed)' },
    { label: 'RESULT (SI)', value: result.si, color: 'var(--color-si)' },
    { label: 'RESULT (CGS)', value: result.cgs, color: 'var(--color-cgs)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ display: 'flex', gap: 8 }}>
        {cards.map(card => (
          <div key={card.label} style={{
            flex: 1,
            background: card.color,
            padding: '10px 12px',
            borderRadius: 'var(--radius)',
            position: 'relative',
          }}>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)', marginBottom: 2 }}>
              {card.label}
            </div>
            <div style={{ fontFamily: 'monospace', fontSize: 'var(--font-base)', wordBreak: 'break-all' }}>
              {card.value}
            </div>
            <button
              onClick={() => copyText(card.value)}
              title="Copy"
              style={{
                position: 'absolute',
                top: 4,
                right: 4,
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                fontSize: 'var(--font-xs)',
                color: 'var(--color-text-muted)',
                padding: '2px 4px',
              }}
            >
              Copy
            </button>
          </div>
        ))}
      </div>

      {result.converted && (
        <div style={{
          background: '#faf5ff',
          padding: '10px 12px',
          borderRadius: 'var(--radius)',
          position: 'relative',
        }}>
          <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)', marginBottom: 2 }}>
            IN {result.targetUnit?.toUpperCase() || 'CONVERTED'}
          </div>
          <div style={{ fontFamily: 'monospace', fontSize: 'var(--font-base)' }}>{result.converted}</div>
          <button
            onClick={() => copyText(result.converted!)}
            title="Copy"
            style={{
              position: 'absolute', top: 4, right: 4,
              background: 'transparent', border: 'none',
              cursor: 'pointer', fontSize: 'var(--font-xs)',
              color: 'var(--color-text-muted)', padding: '2px 4px',
            }}
          >
            Copy
          </button>
        </div>
      )}
    </div>
  );
}
