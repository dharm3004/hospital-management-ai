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

let diagnosisChart = null;

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
      const results = data.results.slice(0, 3);
      let html = '';
      if (data.summary) {
        html += `<div class="alert alert-info mb-3">${data.summary}</div>`;
      }

      results.forEach((r, idx) => {
        let borderClass = 'border-secondary';
        let barClass = 'bg-secondary';
        let rankLabel = 'Possible';
        if (idx === 0) {
          borderClass = 'border-success';
          barClass = 'bg-success';
          rankLabel = 'Top match';
        } else if (idx === 1) {
          borderClass = 'border-primary';
          barClass = 'bg-primary';
        }
        const safeProb = Math.max(0, Math.min(100, Number(r.probability) || 0));
        html += `<div class="card mb-3 border ${borderClass}">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start gap-3">
              <div>
                <h5 class="card-title mb-1">${r.disease}</h5>
                <div class="text-muted small">Prediction accuracy: ${safeProb}%</div>
              </div>
              <span class="badge bg-light text-dark">${idx + 1}️⃣ ${rankLabel}</span>
            </div>
            <div class="progress mt-3" style="height: 8px;">
              <div class="progress-bar ${barClass} ai-progress-bar" role="progressbar" style="width:0%;" data-target="${safeProb}" aria-valuenow="${safeProb}" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
            <div class="mt-3 d-flex justify-content-between align-items-center">
              <small class="text-muted">Higher bar means higher predicted likelihood.</small>
              <a href="https://www.google.com/search?q=${encodeURIComponent(r.disease + ' disease symptoms treatment')}" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary">Learn More</a>
            </div>
          </div>
        </div>`;
      });

      html += `<div class="card mt-3">
        <div class="card-body">
          <h6 class="card-title mb-3">Prediction probabilities</h6>
          <canvas id="diagnosisChart" height="150"></canvas>
        </div>
      </div>`;

      html += '<div class="mt-3"><small class="text-muted">⚠ This AI prediction is for informational purposes only and should not replace professional medical advice. Please consult a qualified doctor.</small></div>';
      resultsDiv.innerHTML = html;

      // animate progress bars
      requestAnimationFrame(() => {
        document.querySelectorAll('.ai-progress-bar').forEach((bar) => {
          const target = Number(bar.dataset.target) || 0;
          bar.style.width = `${target}%`;
        });
      });

      // render chart if Chart.js is available
      if (window.Chart) {
        const ctx = document.getElementById('diagnosisChart');
        if (ctx) {
          const labels = results.map((r) => r.disease);
          const values = results.map((r) => Math.max(0, Math.min(100, Number(r.probability) || 0)));
          if (diagnosisChart) {
            diagnosisChart.destroy();
          }
          diagnosisChart = new Chart(ctx, {
            type: 'bar',
            data: {
              labels,
              datasets: [{
                label: 'Prediction probability (%)',
                data: values,
                backgroundColor: ['#198754', '#0d6efd', '#6c757d'],
                borderRadius: 6,
              }],
            },
            options: {
              responsive: true,
              plugins: {
                legend: { display: false },
              },
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  ticks: { stepSize: 20 },
                },
              },
            },
          });
        }
      }
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

