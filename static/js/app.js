// Hospital AI front-end helpers: search/filter, toasts, loading overlay, CSRF helper
console.log('Hospital AI static loaded');

function getCookie(name) {
	const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
	return v ? v.pop() : '';
}

function showToast(message, kind='info'){
	const el = document.createElement('div');
	el.className = `toast align-items-center text-bg-${kind} border-0 show m-2`;
	el.role = 'alert';
	el.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
	const container = document.getElementById('toast-container') || (function(){ const c=document.createElement('div'); c.id='toast-container'; c.style.position='fixed'; c.style.right='1rem'; c.style.top='1rem'; c.style.zIndex=9999; document.body.appendChild(c); return c; })();
	container.appendChild(el);
	setTimeout(()=>{ try{ el.remove(); }catch(e){} }, 4000);
}

function showLoading(){
	if(document.getElementById('loading-overlay')) return;
	const o = document.createElement('div');
	o.id = 'loading-overlay';
	o.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
	document.body.appendChild(o);
}

function hideLoading(){
	const o = document.getElementById('loading-overlay'); if(o) o.remove();
}

// Attach search filtering if relevant elements exist
document.addEventListener('DOMContentLoaded', ()=>{
	const search = document.getElementById('symptom-search');
	if(search){
		search.addEventListener('input', ()=>{
			const q = search.value.trim().toLowerCase();
			document.querySelectorAll('#symptom-list .symptom-btn').forEach(b=>{
				const s = (b.dataset.symptom||b.textContent||'').toLowerCase();
				if(!q || s.includes(q)) b.style.display = ''; else b.style.display='none';
			});
		});
	}
	// show server-side Django messages as toasts
	const dm = document.getElementById('django-messages');
	if(dm){
		Array.from(dm.children).forEach(c=>{
			const level = c.dataset.tags || 'info';
			const text = c.textContent.trim();
			if(text) showToast(text, level === 'error' ? 'danger' : 'info');
		});
	}
});

// Export helpers for inline templates
window.HospitalAI = { getCookie, showToast, showLoading, hideLoading };

let diagnosisChart = null;

function parseSymptomsPayload() {
	const el = document.getElementById('symptoms-data');
	if (!el) return [];
	try {
		const parsed = JSON.parse(el.textContent || '[]');
		return Array.isArray(parsed) ? parsed : [];
	} catch (e) {
		return [];
	}
}

function selectedSymptomValues() {
	return Array.from(document.querySelectorAll('#selected-symptoms .selected-chip'))
		.map((chip) => (chip.dataset.symptom || '').trim())
		.filter(Boolean);
}

function updateSelectedCount() {
	const countEl = document.getElementById('selected-count');
	if (!countEl) return;
	const count = selectedSymptomValues().length;
	countEl.textContent = `${count} selected`;
}

function ensureSelectedPlaceholder() {
	const selectedWrap = document.getElementById('selected-symptoms');
	if (!selectedWrap) return;
	const count = selectedSymptomValues().length;
	let placeholder = document.getElementById('symptom-placeholder');
	if (count === 0 && !placeholder) {
		placeholder = document.createElement('small');
		placeholder.id = 'symptom-placeholder';
		placeholder.className = 'text-muted';
		placeholder.textContent = 'No symptoms selected';
		selectedWrap.appendChild(placeholder);
	}
	if (count > 0 && placeholder) placeholder.remove();
	updateSelectedCount();
}

function setChipState(symptom, selected) {
	document.querySelectorAll('#symptom-list .symptom-chip').forEach((chip) => {
		if ((chip.dataset.symptom || '') === symptom) {
			chip.classList.toggle('selected', selected);
			chip.setAttribute('aria-pressed', selected ? 'true' : 'false');
		}
	});
}

function removeSelectedSymptom(symptom) {
	const selectedWrap = document.getElementById('selected-symptoms');
	if (!selectedWrap) return;
	Array.from(selectedWrap.querySelectorAll('.selected-chip')).forEach((chip) => {
		if ((chip.dataset.symptom || '') === symptom) chip.remove();
	});
	setChipState(symptom, false);
	ensureSelectedPlaceholder();
}

function addSelectedSymptom(symptom) {
	const selectedWrap = document.getElementById('selected-symptoms');
	if (!selectedWrap) return;
	if (selectedSymptomValues().includes(symptom)) return;

	ensureSelectedPlaceholder();
	const placeholder = document.getElementById('symptom-placeholder');
	if (placeholder) placeholder.remove();

	const chip = document.createElement('button');
	chip.type = 'button';
	chip.className = 'selected-chip';
	chip.dataset.symptom = symptom;
	chip.textContent = symptom;
	chip.title = 'Click to remove';
	chip.addEventListener('click', () => removeSelectedSymptom(symptom));
	selectedWrap.appendChild(chip);

	setChipState(symptom, true);
	ensureSelectedPlaceholder();
}

function toggleSymptom(symptom) {
	if (selectedSymptomValues().includes(symptom)) removeSelectedSymptom(symptom);
	else addSelectedSymptom(symptom);
}

function renderSymptomChips(symptoms) {
	const list = document.getElementById('symptom-list');
	if (!list) return;
	list.innerHTML = '';

	symptoms.forEach((symptom) => {
		const chip = document.createElement('button');
		chip.type = 'button';
		chip.className = 'symptom-chip symptom-btn';
		chip.dataset.symptom = symptom;
		chip.textContent = symptom;
		chip.setAttribute('aria-pressed', 'false');
		chip.addEventListener('click', () => toggleSymptom(symptom));
		list.appendChild(chip);
	});
}

function applyDiagnosisFilter(query) {
	const q = (query || '').trim().toLowerCase();
	document.querySelectorAll('#symptom-list .symptom-chip').forEach((chip) => {
		const label = ((chip.dataset.symptom || chip.textContent || '') + '').toLowerCase();
		chip.style.display = !q || label.includes(q) ? '' : 'none';
	});
}

function setDiagnoseLoading(isLoading) {
	const btn = document.getElementById('diagnose-btn');
	const status = document.getElementById('diagnosis-status');
	if (!btn) return;
	const label = btn.querySelector('.btn-label');
	const loader = btn.querySelector('.btn-loader');

	btn.disabled = isLoading;
	if (label) label.classList.toggle('d-none', isLoading);
	if (loader) loader.classList.toggle('d-none', !isLoading);
	if (status) status.textContent = isLoading ? 'Analyzing symptoms with AI...' : '';
}

function cardClassForRank(rank) {
	if (rank === 1) return 'prediction-rank-1';
	if (rank === 2) return 'prediction-rank-2';
	return 'prediction-rank-3';
}

function rankLabel(rank) {
	if (rank === 1) return 'Prediction #1';
	if (rank === 2) return 'Prediction #2';
	return 'Prediction #3';
}

function diseaseUrl(name) {
	return `https://www.google.com/search?q=${encodeURIComponent(`${name} disease symptoms treatment`)}`;
}

function chartValuesFromResults(results) {
	const safe = (Array.isArray(results) ? results : [])
		.map((item) => ({
			label: String(item.disease || 'Unknown'),
			value: Math.max(0, Math.min(100, Number(item.probability) || 0)),
		}))
		.sort((a, b) => b.value - a.value)
		.slice(0, 3);

	return {
		labels: safe.map((item) => item.label),
		values: safe.map((item) => item.value),
	};
}

function renderPredictionResults(data) {
	const container = document.getElementById('prediction-results');
	if (!container) return;
	const results = (Array.isArray(data.results) ? data.results : [])
		.map((item) => ({
			disease: String(item.disease || 'Unknown'),
			probability: Math.max(0, Math.min(100, Number(item.probability) || 0)),
		}))
		.sort((a, b) => b.probability - a.probability)
		.slice(0, 3);

	if (!results.length) {
		container.innerHTML = '<div class="alert alert-info">No prediction available.</div>';
		return;
	}

	let html = '';
	if (data.summary) {
		html += `<div class="alert alert-info mb-3">${data.summary}</div>`;
	}

	html += '<div class="result-grid">';
	results.forEach((item, i) => {
		const rank = i + 1;
		const safeProb = Math.max(0, Math.min(100, Number(item.probability) || 0));
		html += `
			<article class="prediction-card ${cardClassForRank(rank)} p-3 p-md-4">
				<div class="d-flex justify-content-between align-items-start gap-3 mb-2">
					<h5 class="mb-0">${item.disease}</h5>
					<span class="prediction-rank-badge">${rankLabel(rank)}</span>
				</div>
				<p class="prediction-percent mb-2">Prediction Accuracy: ${safeProb}%</p>
				<div class="prediction-progress mb-3">
					<div class="progress-bar ${rank === 1 ? 'bg-success' : rank === 2 ? 'bg-primary' : 'bg-secondary'} ai-progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${safeProb}" data-target="${safeProb}"></div>
				</div>
				<div class="d-grid">
					<a href="${diseaseUrl(item.disease)}" target="_blank" rel="noopener" class="btn btn-outline-primary btn-sm">Learn More</a>
				</div>
			</article>
		`;
	});
	html += '</div>';

	html += `
		<div class="chart-card p-3 p-md-4 mt-3">
			<h6 class="mb-3">Probability Overview</h6>
			<canvas id="diagnosisChart" height="120"></canvas>
		</div>
		<div class="medical-disclaimer mt-3">
			<strong>Warning:</strong> This AI prediction is for informational purposes only and should not replace professional medical advice. Please consult a qualified doctor.
		</div>
	`;

	container.innerHTML = html;

	document.querySelectorAll('.ai-progress-bar').forEach((bar) => {
		bar.style.width = '0%';
	});
	setTimeout(() => {
		document.querySelectorAll('.ai-progress-bar').forEach((bar) => {
			const target = Number(bar.dataset.target) || 0;
			bar.style.minWidth = target > 0 ? '12px' : '0';
			bar.style.width = `${target}%`;
		});
	}, 90);

	if (!window.Chart) return;
	const canvas = document.getElementById('diagnosisChart');
	if (!canvas) return;
	const chartData = chartValuesFromResults(results);
	if (!chartData.labels.length) return;
	if (diagnosisChart) diagnosisChart.destroy();
	diagnosisChart = new Chart(canvas, {
		type: 'bar',
		data: {
			labels: chartData.labels,
			datasets: [{
				label: 'Probability (%)',
				data: chartData.values,
				backgroundColor: ['#198754', '#0d6efd', '#6c757d'],
				borderRadius: 8,
				maxBarThickness: 54,
			}],
		},
		options: {
			responsive: true,
			plugins: { legend: { display: false } },
			animation: { duration: 900, easing: 'easeOutQuart' },
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

async function runAIDiagnosis() {
	const btn = document.getElementById('diagnose-btn');
	const output = document.getElementById('prediction-results');
	if (!btn || !output) return;

	const symptoms = selectedSymptomValues();
	if (!symptoms.length) {
		output.innerHTML = '<div class="alert alert-warning">Please select at least one symptom.</div>';
		return;
	}

	const saveHistoryCheckbox = document.getElementById('save-history');
	const saveHistory = !saveHistoryCheckbox || saveHistoryCheckbox.checked;
	setDiagnoseLoading(true);
	output.innerHTML = '<div class="card border-0 ai-empty-state"><div class="card-body text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-3 mb-0">Analyzing symptoms with AI...</p></div></div>';

	try {
		const response = await fetch(btn.dataset.endpoint, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken'),
			},
			body: JSON.stringify({ symptoms, save_history: saveHistory }),
		});
		const data = await response.json().catch(() => ({}));
		if (!response.ok) {
			output.innerHTML = `<div class="alert alert-danger">${data.error || 'Request failed.'}</div>`;
			return;
		}
		if (data.error) {
			output.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
			return;
		}
		renderPredictionResults(data);
	} catch (err) {
		output.innerHTML = '<div class="alert alert-danger">Unexpected error occurred.</div>';
	} finally {
		setDiagnoseLoading(false);
	}
}

function initButtonRipple() {
	document.querySelectorAll('.ripple-btn').forEach((btn) => {
		btn.addEventListener('click', (event) => {
			const rect = btn.getBoundingClientRect();
			const size = Math.max(rect.width, rect.height);
			const circle = document.createElement('span');
			circle.className = 'btn-ripple';
			circle.style.width = `${size}px`;
			circle.style.height = `${size}px`;
			circle.style.left = `${event.clientX - rect.left - size / 2}px`;
			circle.style.top = `${event.clientY - rect.top - size / 2}px`;
			btn.appendChild(circle);
			setTimeout(() => {
				if (circle.parentNode) circle.remove();
			}, 600);
		});
	});
}

function initAIDiagnosisPage() {
	const list = document.getElementById('symptom-list');
	const diagnoseBtn = document.getElementById('diagnose-btn');
	if (!list || !diagnoseBtn) return;

	const symptoms = parseSymptomsPayload();
	if (!symptoms.length) {
		list.innerHTML = '<div class="alert alert-warning mb-0">No symptoms available.</div>';
		return;
	}

	renderSymptomChips(symptoms);
	ensureSelectedPlaceholder();

	const search = document.getElementById('symptom-search');
	if (search) {
		search.addEventListener('input', () => applyDiagnosisFilter(search.value));
	}

	diagnoseBtn.addEventListener('click', runAIDiagnosis);
	initButtonRipple();
}

document.addEventListener('DOMContentLoaded', initAIDiagnosisPage);
