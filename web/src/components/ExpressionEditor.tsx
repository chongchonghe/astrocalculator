import { useState, useCallback, useEffect, useMemo } from 'react';
import constantsData from '../data/constants.json';
import unitsData from '../data/units.json';
import type { ConstantEntry, UnitEntry } from '../types';

const constants: ConstantEntry[] = constantsData as ConstantEntry[];
const units: UnitEntry[] = unitsData as UnitEntry[];

interface ExpressionEditorProps {
  editorRef: React.RefObject<HTMLTextAreaElement | null>;
}

export default function ExpressionEditor({ editorRef }: ExpressionEditorProps) {
  const [value, setValue] = useState('');
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [suggestions, setSuggestions] = useState<{ text: string; type: 'constant' | 'unit' }[]>([]);
  const [selectedIdx, setSelectedIdx] = useState(0);

  const allItems = useMemo(() => [
    ...constants.map(c => ({ text: c.symbol, type: 'constant' as const })),
    ...units.map(u => ({ text: u.name, type: 'unit' as const })),
  ], []);

  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setValue(newValue);

    const cursorPos = e.target.selectionStart;
    const textBeforeCursor = newValue.slice(0, cursorPos);
    const lastWordMatch = textBeforeCursor.match(/[\w_]+$/);

    if (lastWordMatch) {
      const word = lastWordMatch[0].toLowerCase();
      const matches = allItems.filter(item =>
        item.text.toLowerCase().includes(word)
      ).slice(0, 8);
      if (matches.length > 0) {
        setSuggestions(matches);
        setShowAutocomplete(true);
        setSelectedIdx(0);
        return;
      }
    }
    setShowAutocomplete(false);
  }, [allItems]);

  const insertSuggestion = useCallback((text: string) => {
    const ta = editorRef.current;
    if (!ta) return;
    const cursorPos = ta.selectionStart;
    const textBeforeCursor = ta.value.slice(0, cursorPos);
    const lastWordMatch = textBeforeCursor.match(/[\w_]+$/);
    if (lastWordMatch) {
      const before = ta.value.slice(0, cursorPos - lastWordMatch[0].length);
      const after = ta.value.slice(cursorPos);
      const newValue = before + text + after;
      setValue(newValue);
      setTimeout(() => {
        ta.value = before + text + after;
        ta.selectionStart = ta.selectionEnd = before.length + text.length;
        ta.focus();
      }, 0);
    }
    setShowAutocomplete(false);
  }, [editorRef]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      window.dispatchEvent(new CustomEvent('evaluate', { detail: value }));
      return;
    }

    if (showAutocomplete) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIdx(prev => (prev + 1) % suggestions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIdx(prev => (prev - 1 + suggestions.length) % suggestions.length);
      } else if (e.key === 'Enter' || e.key === 'Tab') {
        e.preventDefault();
        insertSuggestion(suggestions[selectedIdx].text);
      } else if (e.key === 'Escape') {
        setShowAutocomplete(false);
      }
    }
  }, [showAutocomplete, suggestions, selectedIdx, insertSuggestion, value]);

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

  const lines = value.split('\n').length;

  return (
    <div style={{ position: 'relative', flex: 1, display: 'flex', flexDirection: 'column' }}>
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
          fontSize: 13,
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
          placeholder={`Enter expressions...\ne.g. M = 1.4 M_sun\nR = 10 km\nsqrt(2 G M / R) in km/s`}
          spellCheck={false}
          style={{
            flex: 1,
            border: 'none',
            outline: 'none',
            resize: 'none',
            padding: '8px 10px',
            fontFamily: 'monospace',
            fontSize: 13,
            lineHeight: 1.5,
            background: 'transparent',
          }}
        />
      </div>

      {showAutocomplete && suggestions.length > 0 && (
        <div style={{
          position: 'absolute',
          bottom: 'calc(100% + 4px)',
          left: 36,
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius)',
          boxShadow: 'var(--shadow)',
          zIndex: 10,
          minWidth: 200,
        }}>
          {suggestions.map((s, i) => (
            <div
              key={s.text}
              onClick={() => insertSuggestion(s.text)}
              style={{
                padding: '4px 10px',
                cursor: 'pointer',
                background: i === selectedIdx ? 'var(--color-accent-light)' : undefined,
                fontSize: 12,
                fontFamily: 'monospace',
                display: 'flex',
                justifyContent: 'space-between',
              }}
            >
              <span>{s.text}</span>
              <span style={{ color: 'var(--color-text-muted)', fontSize: 10 }}>{s.type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
