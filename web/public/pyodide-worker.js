// web/public/pyodide-worker.js
// Classic web worker — must be plain JS (not module) for importScripts to work

let pyodideReady = false;
let evaluateFn = null;

const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.25.1/full/';

async function initPyodide() {
  importScripts(PYODIDE_URL + 'pyodide.js');

  const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
  await pyodide.loadPackage(['numpy', 'astropy', 'sympy']);

  // Fetch calculator.py from public/
  const resp = await fetch(new URL('calculator.py', self.location.href));
  const calcCode = await resp.text();
  await pyodide.runPythonAsync(calcCode);

  evaluateFn = pyodide.runPython(`
from calculator import evaluate as _evaluate
def evaluate_wrapper(expr):
    import json
    result = _evaluate(expr)
    return json.dumps(result)
evaluate_wrapper
  `);

  pyodideReady = true;
  self.postMessage({ type: 'ready' });
}

self.onmessage = async function(e) {
  var data = e.data;
  var id = data.id;
  var type = data.type;
  var payload = data.payload;

  if (type === 'init') {
    try {
      await initPyodide();
    } catch (err) {
      self.postMessage({ id: id, type: 'error', payload: String(err) });
    }
    return;
  }

  if (!pyodideReady) {
    self.postMessage({ id: id, type: 'error', payload: 'Engine not ready' });
    return;
  }

  if (type === 'evaluate') {
    try {
      var jsonStr = evaluateFn(payload);
      var result = JSON.parse(jsonStr);
      self.postMessage({ id: id, type: 'result', payload: result });
    } catch (err) {
      self.postMessage({ id: id, type: 'error', payload: String(err) });
    }
  }
};
