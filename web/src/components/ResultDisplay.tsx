import { useState, useEffect, useCallback, useRef } from 'react';
import { useCalculator } from '../hooks/useCalculator';
import type { CalculatorResult } from '../types';

export default function ResultDisplay() {
  const { evaluate, setPrecision, ready } = useCalculator();
  const [result, setResult] = useState<CalculatorResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [precision, setPrecisionLocal] = useState(4);
  const lastExprRef = useRef<string>('');

  const runEvaluate = useCallback((expr: string) => {
    if (!expr.trim()) return;
    setEvaluating(true);
    setError(null);
    evaluate(expr).then(res => {
      setResult(res);
      setEvaluating(false);
    }).catch(err => {
      setError(String(err));
      setEvaluating(false);
    });
  }, [evaluate]);

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail as string;
      lastExprRef.current = detail;
      runEvaluate(detail);
    };
    window.addEventListener('evaluate', handler);
    return () => window.removeEventListener('evaluate', handler);
  }, [runEvaluate]);

  const handlePrecisionChange = useCallback((n: number) => {
    setPrecisionLocal(n);
    setPrecision(n);
    if (lastExprRef.current) {
      setTimeout(() => runEvaluate(lastExprRef.current), 0);
    }
  }, [setPrecision, runEvaluate]);

  const copyText = useCallback((text: string) => {
    navigator.clipboard.writeText(text).catch(() => {});
  }, []);

  const precisionControl = (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'flex-end' }}>
      <label style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>Precision</label>
      <select
        value={precision}
        onChange={e => handlePrecisionChange(Number(e.target.value))}
        style={{
          fontSize: 'var(--font-xs)',
          padding: '2px 4px',
          border: '1px solid var(--color-border)',
          borderRadius: 4,
          background: 'var(--color-surface)',
          color: 'var(--color-text)',
          cursor: 'pointer',
        }}
      >
        {[1,2,3,4,5,6,7,8,9].map(n => (
          <option key={n} value={n}>{n}</option>
        ))}
      </select>
    </div>
  );

  if (!result && !error && !evaluating) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {precisionControl}
        <div style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-base)', textAlign: 'center', padding: 20 }}>
          {ready ? 'Cmd+Enter to evaluate' : 'Loading scientific engine...'}
        </div>
      </div>
    );
  }

  if (evaluating) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {precisionControl}
        <div style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-base)', textAlign: 'center', padding: 20 }}>Evaluating...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {precisionControl}
        <div style={{ background: '#fff5f5', padding: 12, borderRadius: 'var(--radius)', color: 'var(--color-error)', fontSize: 'var(--font-base)' }}>
          {error}
        </div>
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
      {precisionControl}
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
            <div style={{ fontFamily: 'monospace', fontSize: 'var(--font-base)', wordBreak: 'break-all', maxHeight: 120, overflowY: 'auto' }}>
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
