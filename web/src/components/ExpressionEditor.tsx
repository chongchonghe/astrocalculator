import { useState, useCallback, useEffect } from 'react';

interface ExpressionEditorProps {
  editorRef: React.RefObject<HTMLTextAreaElement | null>;
}

export default function ExpressionEditor({ editorRef }: ExpressionEditorProps) {
  const [value, setValue] = useState('');

  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      const text = editorRef.current?.value ?? value;
      window.dispatchEvent(new CustomEvent('evaluate', { detail: text }));
    }
  }, [editorRef, value]);

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

  const lines = (editorRef.current?.value || value).split('\n').length;

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
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
    </div>
  );
}
