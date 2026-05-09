import { useState, useCallback, useEffect } from 'react';
import { useCalculator } from '../hooks/useCalculator';

interface ExpressionEditorProps {
  editorRef: React.RefObject<HTMLTextAreaElement | null>;
}

export default function ExpressionEditor({ editorRef }: ExpressionEditorProps) {
  const [value, setValue] = useState('');
  const [precision, setPrecisionLocal] = useState(4);
  const { setPrecision } = useCalculator();

  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
  }, []);

  const run = useCallback(() => {
    const text = editorRef.current?.value ?? value;
    window.dispatchEvent(new CustomEvent('evaluate', { detail: text }));
  }, [editorRef, value]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      run();
    }
  }, [run]);

  // Cmd+J to focus editor
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'j') {
        e.preventDefault();
        editorRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [editorRef]);

  const handlePrecisionChange = useCallback((n: number) => {
    setPrecisionLocal(n);
    setPrecision(n);
    const text = editorRef.current?.value ?? value;
    if (text.trim()) {
      window.dispatchEvent(new CustomEvent('evaluate', { detail: text }));
    }
  }, [setPrecision, editorRef, value]);

  const lines = (editorRef.current?.value || value).split('\n').length;

  return (
    <div style={{ height: 600, minHeight: 200, maxHeight: '80vh', resize: 'vertical', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <div style={{
        display: 'flex',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius)',
        background: 'var(--color-surface)',
        flex: 1,
      }}>
        <div style={{
          padding: '8px 0',
          background: '#f8fafc',
          borderRight: '1px solid var(--color-border)',
          fontFamily: 'monospace',
          fontSize: 'var(--font-base)',
          color: 'var(--color-text-muted)',
          textAlign: 'right',
          minWidth: 36,
          userSelect: 'none',
        }}>
          {Array.from({ length: Math.max(lines, 1) }, (_, i) => (
            <div key={i} style={{ padding: '0 8px', lineHeight: '1.5' }}>{i + 1}</div>
          ))}
        </div>

        <textarea
          ref={editorRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={`e.g.\nM = 1.4 M_sun, R = 10 km\nv = sqrt(2 G M / R)\nv in km/s`}
          spellCheck={false}
          style={{
            flex: 1,
            border: 'none',
            outline: 'none',
            resize: 'none',
            padding: '8px 10px',
            fontFamily: 'monospace',
            fontSize: 'var(--font-base)',
            lineHeight: 1.5,
            background: 'transparent',
          }}
        />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
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
        <button
          onClick={run}
          style={{
            padding: '4px 12px',
            background: 'var(--color-accent)',
            color: '#fff',
            border: 'none',
            borderRadius: 'var(--radius)',
            cursor: 'pointer',
            fontSize: 'var(--font-sm)',
            fontWeight: 600,
          }}
        >
          Run (⌘↵)
        </button>
      </div>
    </div>
  );
}
