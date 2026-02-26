(function () {
  const STORAGE_KEY = 'chna_api_base';
  const DEFAULT_API = 'http://localhost:8000';

  function getApiBase() {
    return (localStorage.getItem(STORAGE_KEY) || DEFAULT_API).replace(/\/$/, '');
  }

  function setApiBase(url) {
    const cleaned = (url || '').trim().replace(/\/$/, '');
    if (!cleaned) {
      throw new Error('API URL cannot be empty.');
    }
    localStorage.setItem(STORAGE_KEY, cleaned);
    return cleaned;
  }

  async function api(path, options) {
    const res = await fetch(getApiBase() + path, {
      headers: { 'Content-Type': 'application/json' },
      ...(options || {}),
    });

    const text = await res.text();
    let body;
    try {
      body = text ? JSON.parse(text) : null;
    } catch {
      body = text;
    }

    if (!res.ok) {
      const detail = body && body.detail ? body.detail : body || ('HTTP ' + res.status);
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }

    return body;
  }

  function setStatus(node, message, kind) {
    if (!node) return;
    node.textContent = message || '';
    node.classList.remove('good', 'bad');
    if (kind === 'good') node.classList.add('good');
    if (kind === 'bad') node.classList.add('bad');
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function formatNumber(value) {
    const n = Number(value);
    if (Number.isNaN(n)) return String(value ?? '');
    return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }

  function downloadCsv(filename, headers, rows) {
    const headerLine = headers.map((h) => `"${String(h).replaceAll('"', '""')}"`).join(',');
    const lines = rows.map((row) =>
      row
        .map((cell) => `"${String(cell ?? '').replaceAll('"', '""')}"`)
        .join(',')
    );
    const csv = [headerLine, ...lines].join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  function renderSourceBar(container, sources) {
    if (!container) return;
    const items = Array.isArray(sources) ? sources : [];
    if (!items.length) {
      container.innerHTML = '<span class="source-label">Sources:</span><span class="helper">No sources loaded for current view.</span>';
      return;
    }

    const chips = items
      .map((source) => {
        const name = escapeHtml(source.name || 'Unknown Source');
        const citation = escapeHtml(source.citation || '');
        const url = source.url ? String(source.url) : '';
        if (url) {
          return `<a class="source-chip" href="${escapeHtml(url)}" title="${citation}" target="_blank" rel="noopener">${name}</a>`;
        }
        return `<span class="source-chip" title="${citation}">${name}</span>`;
      })
      .join('');

    container.innerHTML = `<span class="source-label">Sources:</span>${chips}`;
  }

  function uniqueByName(items) {
    const seen = new Set();
    const out = [];
    for (const item of items || []) {
      const name = item && item.name ? item.name : '';
      if (!name || seen.has(name)) continue;
      seen.add(name);
      out.push(item);
    }
    return out;
  }

  async function loadSourceMap() {
    const sources = await api('/sources');
    const map = new Map();
    for (const source of sources) {
      map.set(source.name, source);
    }
    return map;
  }

  async function loadGeographyOptions() {
    return api('/geography/options');
  }

  function fillStateSelect(select, states) {
    select.innerHTML = '';
    for (const state of states || []) {
      const opt = document.createElement('option');
      opt.value = state.fips;
      opt.textContent = `${state.name} (${state.abbr})`;
      select.appendChild(opt);
    }
  }

  function fillCountySelect(select, counties, stateFips, focusOnly) {
    const filtered = (counties || []).filter((county) => {
      if (stateFips && county.state_fips !== stateFips) return false;
      if (focusOnly && !county.focus_region) return false;
      return true;
    });

    select.innerHTML = '';
    for (const county of filtered) {
      const opt = document.createElement('option');
      opt.value = county.geo_id;
      const availability = county.available ? '' : ' (no local data yet)';
      opt.textContent = `${county.name}, ${county.state_abbr}${availability}`;
      select.appendChild(opt);
    }

    return filtered;
  }

  function getSelectedValues(select) {
    if (!select) return [];
    return Array.from(select.selectedOptions || []).map((opt) => opt.value).filter(Boolean);
  }

  function setSelectedValues(select, values) {
    const target = new Set(values || []);
    for (const opt of Array.from(select.options || [])) {
      opt.selected = target.has(opt.value);
    }
  }

  function parseStateFips(geoId) {
    const value = String(geoId || '');
    return value.length >= 2 ? value.slice(0, 2) : '';
  }

  function mapSourceAttributionFromRows(rows, sourceMap) {
    const names = [...new Set((rows || []).map((row) => row.source_name).filter(Boolean))];
    const mapped = names.map((name) => {
      const source = sourceMap.get(name);
      if (source) {
        return {
          name: source.name,
          url: source.url,
          citation: source.citation,
          category: source.category,
        };
      }
      return { name, url: '', citation: '', category: '' };
    });
    return uniqueByName(mapped);
  }

  window.CHNA = {
    getApiBase,
    setApiBase,
    api,
    setStatus,
    escapeHtml,
    formatNumber,
    downloadCsv,
    renderSourceBar,
    loadSourceMap,
    loadGeographyOptions,
    fillStateSelect,
    fillCountySelect,
    getSelectedValues,
    setSelectedValues,
    parseStateFips,
    mapSourceAttributionFromRows,
  };
})();
