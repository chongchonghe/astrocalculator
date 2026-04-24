// web/src/App.tsx
import { useRef, useCallback, useEffect } from 'react';
import { PyodideProvider } from './hooks/useCalculator';
import Header from './components/Header';
import StudioLayout from './components/StudioLayout';
import ExpressionEditor from './components/ExpressionEditor';
import ResultDisplay from './components/ResultDisplay';
import DebugPanel from './components/DebugPanel';
import { HISTORY_KEY, MAX_HISTORY } from './components/HistoryPanel';
import type { HistoryEntry } from './types';

export default function App() {
  return (
    <PyodideProvider>
      <AppContent />
    </PyodideProvider>
  );
}

function AppContent() {
  const searchBarRef = useRef<HTMLInputElement>(null);
  const editorRef = useRef<HTMLTextAreaElement>(null);

  // Cmd+K → focus search bar
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        searchBarRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  // Record evaluation history (always mounted, not just when History tab is open)
  useEffect(() => {
    const handler = (e: Event) => {
      const input = (e as CustomEvent).detail as string;
      if (!input.trim()) return;
      try {
        const raw = localStorage.getItem(HISTORY_KEY);
        const entries: HistoryEntry[] = raw ? JSON.parse(raw) : [];
        const newEntry: HistoryEntry = {
          id: Date.now(),
          input,
          result: { parsed: '', si: '', cgs: '' },
          timestamp: Date.now(),
        };
        const updated = [newEntry, ...entries].slice(0, MAX_HISTORY);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
      } catch {}
    };
    window.addEventListener('evaluate', handler);
    return () => window.removeEventListener('evaluate', handler);
  }, []);

  // React's synthetic event system doesn't fire onChange from plain dispatchEvent.
  // Must use the native value setter to trigger React's controlled component update.
  const setTextareaValue = (ta: HTMLTextAreaElement, value: string) => {
    const nativeSetter = Object.getOwnPropertyDescriptor(
      HTMLTextAreaElement.prototype, 'value'
    )?.set;
    nativeSetter?.call(ta, value);
    ta.dispatchEvent(new Event('input', { bubbles: true }));
  };

  const handleConstantClick = useCallback((symbol: string) => {
    const ta = editorRef.current;
    if (ta) {
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const newValue = ta.value.slice(0, start) + symbol + ta.value.slice(end);
      setTextareaValue(ta, newValue);
      ta.focus();
      ta.setSelectionRange(start + symbol.length, start + symbol.length);
    }
  }, []);

  const handleEquationAdd = useCallback((
    params: { symbol: string; default: string }[],
    expression: string
  ) => {
    const ta = editorRef.current;
    if (ta) {
      const assignments = params.map(p => `${p.symbol} = ${p.default.trim()}`).join('\n');
      // Split on newlines, trim each line, rejoin — handles inline \n with stray spaces
      const exprLines = expression.split('\n').map(l => l.trim()).join('\n');
      const text = assignments + '\n' + exprLines + '\n';
      const newValue = ta.value.trim() ? ta.value + '\n' + text : text;
      setTextareaValue(ta, newValue);
      ta.focus();
    }
  }, []);

  const handleHistoryClick = useCallback((input: string) => {
    const ta = editorRef.current;
    if (ta) {
      setTextareaValue(ta, input);
      ta.focus();
    }
  }, []);

  const handleSearchFocus = useCallback(() => {
    searchBarRef.current?.focus();
  }, []);

  return (
    <>
      <Header />
      <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', maxWidth: 'var(--page-max-width)', width: '100%' }}>
        <StudioLayout
          editor={<ExpressionEditor editorRef={editorRef} />}
          results={<ResultDisplay />}
          onConstantClick={handleConstantClick}
          onEquationAdd={handleEquationAdd}
          onHistoryClick={handleHistoryClick}
          onSearchFocus={handleSearchFocus}
          searchBarRef={searchBarRef}
          editorRef={editorRef}
        />
      </div>
      <DebugPanel />
    </>
  );
}
