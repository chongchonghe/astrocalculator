import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { CalculatorResult } from '../types';

interface CalculatorState {
  ready: boolean;
  loading: boolean;
  error: string | null;
  evaluate: (expression: string) => Promise<CalculatorResult>;
}

const CalculatorContext = createContext<CalculatorState>({
  ready: false,
  loading: true,
  error: null,
  evaluate: async () => ({ parsed: '', si: '', cgs: '' }),
});

export function PyodideProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const workerRef = useRef<Worker | null>(null);
  const pendingRef = useRef<Map<number, (r: CalculatorResult) => void>>(new Map());
  const nextIdRef = useRef(1);

  useEffect(() => {
    // Classic worker from public/ — needed for importScripts support in Pyodide
    // import.meta.env.BASE_URL handles base path in both dev (/) and prod (/astrocalculator/)
    const worker = new Worker(import.meta.env.BASE_URL + 'pyodide-worker.js');
    workerRef.current = worker;

    worker.onmessage = (e) => {
      const { id, type, payload } = e.data;
      if (type === 'ready') {
        setReady(true);
        setLoading(false);
      } else if (type === 'result') {
        const resolve = pendingRef.current.get(id);
        if (resolve) {
          pendingRef.current.delete(id);
          resolve(payload);
        }
      } else if (type === 'error') {
        setError(payload);
        setLoading(false);
        const resolve = pendingRef.current.get(id);
        if (resolve) {
          pendingRef.current.delete(id);
          resolve({ parsed: '', si: payload, cgs: '' });
        }
      }
    };

    worker.onerror = (err) => {
      setError(err.message);
      setLoading(false);
    };

    worker.postMessage({ type: 'init' });

    return () => {
      worker.terminate();
    };
  }, []);

  const evaluate = useCallback((expression: string): Promise<CalculatorResult> => {
    return new Promise((resolve) => {
      const worker = workerRef.current;
      if (!worker || !ready) {
        resolve({ parsed: '', si: 'Engine not ready', cgs: '' });
        return;
      }
      const id = nextIdRef.current++;
      pendingRef.current.set(id, resolve);
      worker.postMessage({ id, type: 'evaluate', payload: expression });
    });
  }, [ready]);

  return (
    <CalculatorContext.Provider value={{ ready, loading, error, evaluate }}>
      {children}
    </CalculatorContext.Provider>
  );
}

export function useCalculator() {
  return useContext(CalculatorContext);
}
