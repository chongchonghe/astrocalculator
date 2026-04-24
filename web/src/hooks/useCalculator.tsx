import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { CalculatorResult } from '../types';

export interface LogEntry {
  id: number;
  text: string;
  time: number;
}

interface CalculatorState {
  ready: boolean;
  loading: boolean;
  error: string | null;
  evaluate: (expression: string) => Promise<CalculatorResult>;
  logs: LogEntry[];
}

const CalculatorContext = createContext<CalculatorState>({
  ready: false,
  loading: true,
  error: null,
  evaluate: async () => ({ parsed: '', si: '', cgs: '' }),
  logs: [],
});

let logId = 0;

export function PyodideProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([{ id: logId++, text: 'Initializing...', time: Date.now() }]);
  const workerRef = useRef<Worker | null>(null);
  const pendingRef = useRef<Map<number, (r: CalculatorResult) => void>>(new Map());
  const nextIdRef = useRef(1);

  const addLog = useCallback((msg: string) => {
    setLogs(prev => [...prev.slice(-200), { id: logId++, text: msg, time: Date.now() }]);
  }, []);

  useEffect(() => {
    addLog('Creating web worker for Pyodide...');
    const worker = new Worker(import.meta.env.BASE_URL + 'pyodide-worker.js');
    workerRef.current = worker;

    worker.onmessage = (e) => {
      const { id, type, payload } = e.data;
      if (type === 'log') {
        addLog(payload);
      } else if (type === 'ready') {
        addLog('Engine ready');
        setReady(true);
        setLoading(false);
      } else if (type === 'result') {
        addLog('Result received');
        const resolve = pendingRef.current.get(id);
        if (resolve) {
          pendingRef.current.delete(id);
          resolve(payload);
        }
      } else if (type === 'error') {
        addLog('ERROR: ' + payload);
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
      addLog('Worker error: ' + err.message);
      setError(err.message);
      setLoading(false);
    };

    addLog('Sending init to worker...');
    worker.postMessage({ type: 'init' });

    return () => {
      worker.terminate();
    };
  }, [addLog]);

  const evaluate = useCallback((expression: string): Promise<CalculatorResult> => {
    return new Promise((resolve) => {
      addLog('Evaluating: ' + expression);
      const worker = workerRef.current;
      if (!worker || !ready) {
        addLog('Evaluation skipped: engine not ready');
        resolve({ parsed: '', si: 'Engine not ready', cgs: '' });
        return;
      }
      const id = nextIdRef.current++;
      pendingRef.current.set(id, resolve);
      worker.postMessage({ id, type: 'evaluate', payload: expression });
    });
  }, [ready, addLog]);

  return (
    <CalculatorContext.Provider value={{ ready, loading, error, evaluate, logs }}>
      {children}
    </CalculatorContext.Provider>
  );
}

export function useCalculator() {
  return useContext(CalculatorContext);
}
