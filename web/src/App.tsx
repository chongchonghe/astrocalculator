// web/src/App.tsx
import { useRef, useCallback } from 'react';
import { PyodideProvider } from './hooks/useCalculator';
import Header from './components/Header';
import StudioLayout from './components/StudioLayout';
import ExpressionEditor from './components/ExpressionEditor';
import ResultDisplay from './components/ResultDisplay';

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

  const handleConstantClick = useCallback((symbol: string) => {
    const ta = editorRef.current;
    if (ta) {
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      ta.value = ta.value.slice(0, start) + symbol + ta.value.slice(end);
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
      const assignments = params.map(p => `${p.symbol} = ${p.default}`).join('\n');
      const text = assignments + '\n' + expression;
      if (ta.value.trim()) {
        ta.value = ta.value + '\n' + text;
      } else {
        ta.value = text;
      }
      ta.focus();
    }
  }, []);

  const handleHistoryClick = useCallback((input: string) => {
    const ta = editorRef.current;
    if (ta) {
      ta.value = input;
      ta.focus();
    }
  }, []);

  const handleSearchFocus = useCallback(() => {
    searchBarRef.current?.focus();
  }, []);

  return (
    <>
      <Header />
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
    </>
  );
}
