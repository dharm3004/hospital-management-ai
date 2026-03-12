/* AI Diagnosis UI logic (kept out of templates for MVC separation) */

function getSymptomsFromDom() {
  const el = document.getElementById('symptoms-data');
  if (!el) return [];
  try {
    const parsed = JSON.parse(el.textContent || '[]');
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

function renderPlaceholderIfEmpty() {
  const container = document.getElementById('selected-symptoms');
  if (!container) return;
  if (container.children.length === 0) {
    const small = document.createElement('small');
    small.id = 'symptom-placeholder';
    small.className = 'text-muted';
    small.textContent = 'No symptoms selected';
    container.appendChild(small);
  }
}

function addSymptom(symptom) {
  const container = document.getElementById('selected-symptoms');
  if (!container) return;

  const placeholder = document.getElementById('symptom-placeholder');
  if (placeholder) placeholder.remove();

  const exists = Array.from(container.querySelectorAll('.badge')).some((b) => (b.textContent || '').trim() === symptom);
  if (exists) return;

  const span = document.createElement('span');
  span.className = 'badge bg-secondary me-1';
  span.textContent = symptom;
  span.style.cursor = 'pointer';
  span.title = 'Click to remove';
  span.addEventListener('click', () => removeSymptom(symptom));
  container.appendChild(span);

  document.querySelectorAll('#symptom-list .symptom-btn').forEach((it) => {
    if (it.dataset.symptom === symptom) it.classList.add('selected');
  });
}

function removeSymptom(symptom) {
  const container = document.getElementById('selected-symptoms');
  if (!container) return;

  Array.from(container.querySelectorAll('.badge')).forEach((b) => {
    if ((b.textContent || '').trim() === symptom) b.remove();
  });
  document.querySelectorAll('#symptom-list .symptom-btn').forEach((it) => {
    if (it.dataset.symptom === symptom) it.classList.remove('selected');
  });
  renderPlaceholderIfEmpty();
}

function toggleSymptomSelection(symptom) {
  const container = document.getElementById('selected-symptoms');
  if (!container) return;
  const exists = Array.from(container.querySelectorAll('.badge')).some((b) => (b.textContent || '').trim() === symptom);
  if (exists) removeSymptom(symptom);
  else addSymptom(symptom);
}

function initSymptomList(symptoms) {
  const dropdown = document.getElementById('symptom-list');
  if (!dropdown) return;
  dropdown.innerHTML = '';

  symptoms.forEach((symptom) => {
    const item = document.createElement('a');
    item.className = 'list-group-item list-group-item-action symptom-btn';
    item.textContent = symptom;
    item.dataset.symptom = symptom;
    item.href = '#';
    item.addEventListener('click', (e) => {
      e.preventDefault();
      toggleSymptomSelection(symptom);
    });
    dropdown.appendChild(item);
  });
}

function applySymptomFilter(q) {
  const query = (q || '').trim().toLowerCase();
  document.querySelectorAll('#symptom-list .symptom-btn').forEach((b) => {
    const s = (b.dataset.symptom || b.textContent || '').toLowerCase();
    b.style.display = !query || s.includes(query) ? '' : 'none';
  });
}

async function runDiagnosis() {
  const resultsDiv = document.getElementById('prediction-results');
  const btn = document.getElementById('diagnose-btn');
  if (!resultsDiv || !btn) return;

  const selected = Array.from(document.querySelectorAll('#selected-symptoms .badge')).map((el) => (el.textContent || '').trim()).filter(Boolean);
  if (selected.length === 0) {
    resultsDiv.innerHTML = '<div class="alert alert-warning">Please select at least one symptom.</div>';
    return;
  }

  const saveHistoryCheckbox = document.getElementById('save-history');
  const saveHistory = !saveHistoryCheckbox || saveHistoryCheckbox.checked;

  btn.disabled = true;
  resultsDiv.innerHTML = '<div class="text-center my-4"><div class="spinner-border text-primary" role="status"></div><div class="mt-2">Analyzing symptoms...</div></div>';
  try {
    const csrf = (window.HospitalAI && window.HospitalAI.getCookie) ? window.HospitalAI.getCookie('csrftoken') : '';
    const response = await fetch(btn.dataset.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf,
      },
      body: JSON.stringify({ symptoms: selected, save_history: saveHistory }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error || 'Request failed.'}</div>`;
      return;
    }
    if (data.error) {
      resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
      return;
    }

    if (Array.isArray(data.results) && data.results.length) {
      let html = '';
      if (data.summary) {
        html += `<div class="alert alert-info mb-3">${data.summary}</div>`;
      }
      data.results.forEach((r, idx) => {
        let borderClass = 'border-secondary';
        if (idx === 0) borderClass = 'border-success';
        else if (idx === 1) borderClass = 'border-info';
        html += `<div class="card mb-3 ${borderClass}">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start gap-3">
              <div>
                <h5 class="card-title mb-1">${r.disease}</h5>
                <div class="text-muted small">Estimated confidence: ${r.probability}%</div>
              </div>
              <span class="badge bg-light text-dark">${idx === 0 ? 'Top match' : 'Possible'}</span>
            </div>
            <div class="mt-3">
              <a href="https://www.google.com/search?q=${encodeURIComponent(r.disease + ' disease symptoms treatment')}" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary">More info</a>
            </div>
          </div>
        </div>`;
      });
      html += '<div class="mt-2"><small class="text-muted">This AI prediction is for informational purposes only and should not replace professional medical advice.</small></div>';
      resultsDiv.innerHTML = html;
    } else {
      resultsDiv.innerHTML = '<div class="alert alert-info">No prediction available.</div>';
    }
  } catch (err) {
    resultsDiv.innerHTML = '<div class="alert alert-danger">Unexpected error occurred.</div>';
  } finally {
    btn.disabled = false;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const symptoms = getSymptomsFromDom();
  const listEl = document.getElementById('symptom-list');
  if (!Array.isArray(symptoms) || symptoms.length === 0) {
    if (listEl) listEl.innerHTML = '<div class="alert alert-warning mb-0">No symptoms available.</div>';
    return;
  }

  initSymptomList(symptoms);

  const search = document.getElementById('symptom-search');
  if (search) {
    search.addEventListener('input', () => applySymptomFilter(search.value));
  }

  const btn = document.getElementById('diagnose-btn');
  if (btn) {
    btn.addEventListener('click', runDiagnosis);
  }
});

