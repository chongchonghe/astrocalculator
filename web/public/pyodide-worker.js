// web/public/pyodide-worker.js
// Classic web worker — must be plain JS (not module) for importScripts to work

var pyodideReady = false;
var evaluateFn = null;

var PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.25.1/full/';

function log(msg) {
  self.postMessage({ type: 'log', payload: msg });
  console.log('[worker] ' + msg);
}

async function initPyodide() {
  log('Step 1/5: Loading pyodide.js via importScripts...');
  importScripts(PYODIDE_URL + 'pyodide.js');
  log('Step 1/5: pyodide.js loaded');

  log('Step 2/5: Initializing Pyodide runtime...');
  var pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
  log('Step 2/5: Pyodide runtime ready (Python ' + pyodide.runPython('import sys; sys.version').trim() + ')');

  log('Step 3/5: Loading packages (numpy, astropy, sympy)...');
  await pyodide.loadPackage(['numpy', 'astropy', 'sympy']);
  log('Step 3/5: Packages loaded');

  log('Step 4/5: Fetching calculator.py...');
  var resp = await fetch(new URL('calculator.py', self.location.href));
  if (!resp.ok) throw new Error('Failed to fetch calculator.py: ' + resp.status + ' ' + resp.statusText);
  var calcCode = await resp.text();
  log('Step 4/5: calculator.py fetched (' + calcCode.length + ' chars)');

  log('Step 5/5: Running calculator.py in Pyodide...');
  try {
    await pyodide.runPythonAsync(calcCode);
  } catch (pyErr) {
    log('ERROR running calculator.py: ' + pyErr);
    // Try to get Python traceback
    try {
      var tb = pyodide.runPython('\n'.join(pyErr));
      log('Traceback: ' + tb);
    } catch (_) {}
    throw pyErr;
  }
  log('Step 5/5: calculator.py loaded successfully');

  log('Creating evaluate wrapper...');
  evaluateFn = pyodide.runPython('\n\
from calculator import evaluate as _evaluate\n\
def evaluate_wrapper(expr):\n\
    import json\n\
    result = _evaluate(expr)\n\
    return json.dumps(result)\n\
evaluate_wrapper\n\
  ');
  log('Evaluate wrapper created');

  pyodideReady = true;
  self.postMessage({ type: 'ready' });
  log('Engine ready!');
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
      log('FATAL: init failed - ' + String(err));
      self.postMessage({ id: id, type: 'error', payload: String(err) });
    }
    return;
  }

  if (!pyodideReady) {
    self.postMessage({ id: id, type: 'error', payload: 'Engine not ready' });
    return;
  }

  if (type === 'evaluate') {
    log('Evaluating: ' + payload);
    try {
      var jsonStr = evaluateFn(payload);
      var result = JSON.parse(jsonStr);
      log('Result: ' + jsonStr);
      self.postMessage({ id: id, type: 'result', payload: result });
    } catch (err) {
      log('Eval error: ' + String(err));
      self.postMessage({ id: id, type: 'error', payload: String(err) });
    }
  }
};
