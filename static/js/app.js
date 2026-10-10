// EPR Compliance Copilot - Frontend Logic (IMP-009, IMP-013)

function switchTab(tabId, btn) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  btn.classList.add('active');
  if (tabId === 'kbTab') loadKnowledgeBase();
}

function fillQuery(pill) {
  document.getElementById('questionInput').value = pill.innerText;
  askQuestion();
}

async function askQuestion() {
  const q = document.getElementById('questionInput').value.trim();
  if (!q) return;
  const loading = document.getElementById('qaLoading');
  const output = document.getElementById('qaOutput');

  loading.style.display = 'block';
  output.style.display = 'none';

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: q})
    });
    const data = await res.json();

    if (!res.ok) {
      output.innerHTML = `<span style="color:#f4a261;">Error: ${data.error || 'Request failed'}</span>`;
      output.style.display = 'block';
      return;
    }

    let formatted = data.answer.replace(/\n/g, '<br>');
    let html = formatted;

    if (data.citations && data.citations.length > 0) {
      html += '<br><br><b>Ground-truth Citations:</b><br>';
      data.citations.forEach(c => {
        html += `<span class="citation-tag ${c.confidence}">[${c.id}] ${c.title} (${c.confidence})</span>`;
      });
    }
    html += `<br><br><i style="color:#9aa59d;font-size:12px;">${data.disclaimer}</i>`;
    output.innerHTML = html;
    output.style.display = 'block';
  } catch (err) {
    output.innerHTML = '<span style="color:#f4a261;">Network error querying copilot: ' + err + '</span>';
    output.style.display = 'block';
  } finally {
    loading.style.display = 'none';
  }
}

let lastCalcResult = null;

async function calculateObligations() {
  const piboType = document.getElementById('piboType').value;
  const fiscalYear = document.getElementById('fiscalYearSelect').value;
  const tonnages = {
    cat_1: parseFloat(document.getElementById('cat1Input').value) || 0,
    cat_2: parseFloat(document.getElementById('cat2Input').value) || 0,
    cat_3: parseFloat(document.getElementById('cat3Input').value) || 0,
    cat_4: parseFloat(document.getElementById('cat4Input').value) || 0,
  };

  try {
    const res = await fetch('/api/calculate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({pibo_type: piboType, fiscal_year: fiscalYear, tonnages})
    });
    const data = await res.json();
    lastCalcResult = data;

    document.getElementById('resTotalIntroduced').innerText = data.total_introduced_packaging_mt + ' MT';
    document.getElementById('resRecyclingTarget').innerText = data.total_recycling_obligation_mt + ' MT';
    document.getElementById('resRecycledContent').innerText = data.total_recycled_content_required_mt + ' MT';
    document.getElementById('resPenaltyExposure').innerText = 'Rs ' + data.potential_ec_penalty_exposure_inr.toLocaleString('en-IN');
    document.getElementById('resCertRange').innerText = data.estimated_cert_procurement_cost_range_inr.formatted;

    document.getElementById('refYr1').innerText = data.ec_refund_schedule.year_1_fulfillment;
    document.getElementById('refYr2').innerText = data.ec_refund_schedule.year_2_fulfillment;
    document.getElementById('refYr3').innerText = data.ec_refund_schedule.year_3_fulfillment;

    const tbody = document.querySelector('#categoryTable tbody');
    tbody.innerHTML = '';
    for (const [key, c] of Object.entries(data.categories)) {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><b>${c.name.split(':')[0]}</b><br><span style="font-size:11px;color:#9aa59d">${c.name.split(':')[1]}</span></td>
        <td>${c.introduced_mt}</td>
        <td>${c.recycling_target_pct}%</td>
        <td><b>${c.recycling_obligation_mt}</b></td>
        <td>${c.recycled_content_mandate_pct}% (${c.recycled_content_required_mt} MT)</td>
        <td>Rs ${c.estimated_cert_cost_range_inr[0].toLocaleString('en-IN')} - ${c.estimated_cert_cost_range_inr[1].toLocaleString('en-IN')}</td>
      `;
      tbody.appendChild(row);
    }

    document.getElementById('calcResultsSection').style.display = 'block';
  } catch (e) {
    alert('Error computing liability: ' + e);
  }
}

function applyPreset(presetType) {
  const presets = {
    fmcg: { pibo: 'Brand Owner', cat1: 500, cat2: 180, cat3: 40, cat4: 0 },
    ecommerce: { pibo: 'Brand Owner', cat1: 60, cat2: 380, cat3: 90, cat4: 0 },
    pharma: { pibo: 'Producer', cat1: 150, cat2: 45, cat3: 75, cat4: 10 },
    importer: { pibo: 'Importer', cat1: 120, cat2: 220, cat3: 30, cat4: 0 }
  };

  const p = presets[presetType];
  if (!p) return;

  document.getElementById('piboType').value = p.pibo;
  document.getElementById('cat1Input').value = p.cat1;
  document.getElementById('cat2Input').value = p.cat2;
  document.getElementById('cat3Input').value = p.cat3;
  document.getElementById('cat4Input').value = p.cat4;

  calculateObligations();
}

function exportFormVII() {
  if (!lastCalcResult) {
    calculateObligations().then(() => downloadFormVIIJSON());
  } else {
    downloadFormVIIJSON();
  }
}

function downloadFormVIIJSON() {
  if (!lastCalcResult) return;
  const payload = {
    cpcb_portal_spec: "Form-VII Annual Return (Rule 13 PWM Rules 2016)",
    generated_at: new Date().toISOString(),
    filing_entity: {
      pibo_type: lastCalcResult.pibo_type,
      assessment_year: lastCalcResult.fiscal_year,
      statutory_deadline: "June 30",
    },
    introduced_packaging_mt: {
      category_1_rigid: lastCalcResult.categories.cat_1.introduced_mt,
      category_2_flexible: lastCalcResult.categories.cat_2.introduced_mt,
      category_3_multilayer: lastCalcResult.categories.cat_3.introduced_mt,
      category_4_compostable: lastCalcResult.categories.cat_4.introduced_mt,
      total_mt: lastCalcResult.total_introduced_packaging_mt
    },
    statutory_obligations_mt: {
      recycling_obligation: lastCalcResult.total_recycling_obligation_mt,
      recycled_content_required: lastCalcResult.total_recycled_content_required_mt
    },
    compliance_exposure: {
      potential_ec_penalty_inr: lastCalcResult.potential_ec_penalty_exposure_inr,
      cert_budget_min_inr: lastCalcResult.estimated_cert_procurement_cost_range_inr.min,
      cert_budget_max_inr: lastCalcResult.estimated_cert_procurement_cost_range_inr.max
    }
  };

  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `CPCB_Form_VII_Annual_Return_${lastCalcResult.fiscal_year}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function printReport() {
  window.print();
}

async function loadKnowledgeBase() {
  const container = document.getElementById('kbListContainer');
  try {
    const res = await fetch('/api/kb');
    const chunks = await res.json();
    let html = '';
    chunks.forEach(c => {
      html += `
        <div style="background:#0f1511; border:1px solid var(--border); border-radius:6px; padding:12px; margin-bottom:10px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <b style="font-size:13.5px; color:#e1e7e2;">[${c.id}] ${c.title}</b>
            <span class="citation-tag ${c.confidence}">${c.confidence}</span>
          </div>
          <div style="font-size:12px; color:var(--text-muted); margin-bottom:6px;"><b>Citation:</b> ${c.citation}</div>
          <div style="font-size:12.5px; color:#c5cdc7; line-height:1.4;">${c.text_preview}</div>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = 'Error loading knowledge base: ' + e;
  }
}
