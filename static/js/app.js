// EPR Compliance Copilot - Frontend Logic (Person 3 / Hours 1-4)

document.addEventListener('DOMContentLoaded', () => {
  loadRulesVersion();
  initKeyboardShortcuts();
  loadQuickCompliance('Brand Owner');
});

async function loadRulesVersion() {
  try {
    const res = await fetch('/api/rules-version');
    const data = await res.json();
    const bannerEl = document.getElementById('rulesBannerDate');
    const footerEl = document.getElementById('footerRulesVersion');
    if (bannerEl) bannerEl.innerText = data.verified_on || '10 Oct 2026';
    if (footerEl) footerEl.innerText = `${data.rules_version} (${data.verified_on})`;
  } catch (e) {
    console.warn('Could not fetch rules version:', e);
  }
}

function initKeyboardShortcuts() {
  const input = document.getElementById('questionInput');
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        askQuestion();
      }
    });
  }
}

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
  const skeleton = document.getElementById('qaSkeleton');
  const output = document.getElementById('qaOutput');

  if (loading) loading.style.display = 'block';
  if (skeleton) skeleton.style.display = 'block';
  if (output) output.style.display = 'none';

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

    const isLive = data.mode !== 'mock';
    let verifierBadge = isLive 
      ? '<div class="verifier-box verified">✅ Answer grounded &amp; verified against official CPCB gazette chunks</div>'
      : '<div class="verifier-box unverified">⚠️ Raw source view (Mock Mode / unverified generation)</div>';

    let formatted = data.answer.replace(/\n/g, '<br>');
    let html = verifierBadge + '<br>' + formatted;

    if (data.citations && data.citations.length > 0) {
      html += '<br><br><b>Ground-truth Statutory Citations:</b><br>';
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
    if (loading) loading.style.display = 'none';
    if (skeleton) skeleton.style.display = 'none';
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

function exportCSV() {
  if (!lastCalcResult) {
    calculateObligations().then(() => downloadCSV());
  } else {
    downloadCSV();
  }
}

function downloadCSV() {
  if (!lastCalcResult) return;
  const cats = lastCalcResult.categories;
  const rows = [
    ["EPR Compliance Assessment Report", "Schedule II PWM Rules 2016"],
    ["Filing Entity", lastCalcResult.pibo_type],
    ["Assessment Fiscal Year", lastCalcResult.fiscal_year],
    ["Generated On", new Date().toLocaleString()],
    [],
    ["Category Code", "Category Name", "Introduced Packaging (MT)", "Recycling Target (%)", "Recycling Obligation (MT)", "Recycled Content Mandate (%)", "Recycled Content (MT)", "Cert Price Range Min (INR)", "Cert Price Range Max (INR)"],
    ["Cat I", cats.cat_1.name, cats.cat_1.introduced_mt, cats.cat_1.recycling_target_pct, cats.cat_1.recycling_obligation_mt, cats.cat_1.recycled_content_mandate_pct, cats.cat_1.recycled_content_required_mt, cats.cat_1.estimated_cert_cost_range_inr[0], cats.cat_1.estimated_cert_cost_range_inr[1]],
    ["Cat II", cats.cat_2.name, cats.cat_2.introduced_mt, cats.cat_2.recycling_target_pct, cats.cat_2.recycling_obligation_mt, cats.cat_2.recycled_content_mandate_pct, cats.cat_2.recycled_content_required_mt, cats.cat_2.estimated_cert_cost_range_inr[0], cats.cat_2.estimated_cert_cost_range_inr[1]],
    ["Cat III", cats.cat_3.name, cats.cat_3.introduced_mt, cats.cat_3.recycling_target_pct, cats.cat_3.recycling_obligation_mt, cats.cat_3.recycled_content_mandate_pct, cats.cat_3.recycled_content_required_mt, cats.cat_3.estimated_cert_cost_range_inr[0], cats.cat_3.estimated_cert_cost_range_inr[1]],
    ["Cat IV", cats.cat_4.name, cats.cat_4.introduced_mt, cats.cat_4.recycling_target_pct, cats.cat_4.recycling_obligation_mt, cats.cat_4.recycled_content_mandate_pct, cats.cat_4.recycled_content_required_mt, cats.cat_4.estimated_cert_cost_range_inr[0], cats.cat_4.estimated_cert_cost_range_inr[1]],
    [],
    ["TOTAL INTRODUCED (MT)", lastCalcResult.total_introduced_packaging_mt],
    ["TOTAL RECYCLING OBLIGATION (MT)", lastCalcResult.total_recycling_obligation_mt],
    ["TOTAL RECYCLED CONTENT REQUIRED (MT)", lastCalcResult.total_recycled_content_required_mt],
    ["POTENTIAL EC PENALTY EXPOSURE (INR)", lastCalcResult.potential_ec_penalty_exposure_inr],
    ["ESTIMATED CERT PROCUREMENT MIN (INR)", lastCalcResult.estimated_cert_procurement_cost_range_inr.min],
    ["ESTIMATED CERT PROCUREMENT MAX (INR)", lastCalcResult.estimated_cert_procurement_cost_range_inr.max],
  ];

  const csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.map(cell => `"${cell !== undefined ? cell : ''}"`).join(",")).join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `EPR_Liability_Assessment_${lastCalcResult.fiscal_year}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function loadQuickCompliance(entity) {
  const container = document.getElementById('complianceProfileDetails');
  if (!container) return;
  try {
    const res = await fetch(`/api/compliance-check/${encodeURIComponent(entity)}`);
    const p = await res.json();
    let rulesHtml = p.applicable_rules.map(r => `<li style="margin-bottom:6px;">${r}</li>`).join('');
    container.innerHTML = `
      <div style="background:#101713; border:1px solid var(--border); border-radius:6px; padding:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <b style="font-size:16px; color:#d8f3dc;">${p.title}</b>
          <span class="rules-pill">Statutory Profile</span>
        </div>
        <p style="font-size:13px; color:var(--text-muted); margin-bottom:14px;">${p.description}</p>
        
        <b style="font-size:13px; color:var(--accent);">Applicable CPCB Rules &amp; Obligations:</b>
        <ul style="font-size:12.5px; color:#c5cdc7; margin:8px 0 14px 20px; line-height:1.45;">
          ${rulesHtml}
        </ul>
        
        <div style="font-size:12px; background:rgba(45,106,79,0.15); border-left:3px solid var(--accent); padding:8px 12px; margin-bottom:10px;">
          <b>Exemptions:</b> ${p.exemptions}
        </div>
        <div style="font-size:12px; background:rgba(231,111,81,0.12); border-left:3px solid #e76f51; padding:8px 12px; color:#f4a261;">
          <b>Non-Compliance Penalty Exposure:</b> ${p.penalties}
        </div>
      </div>
    `;
  } catch (e) {
    container.innerHTML = 'Error loading compliance profile: ' + e;
  }
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
