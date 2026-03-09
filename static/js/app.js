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
				if(!q || s.includes(q)) b.style.display = 'inline-block'; else b.style.display='none';
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
