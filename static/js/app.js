// EPR Compliance Copilot - Frontend Logic with Energy Recovery & Verifier UI

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
  if (tabId === 'leaderboardTab') loadLeaderboard();
  if (tabId === 'roadTab') runRoadEvaluation();
  if (tabId === 'auditTab') initAuditTab();
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

    let html = '';

    // Render Verifier Status Badge (G11)
    if (data.verification) {
      const v = data.verification;
      if (v.is_verified) {
        html += `<div class="verifier-status-badge pass">
          <span>✅ Ground-Truth Verified</span>
          <span style="font-weight:400; opacity:0.85;">(${v.checked_claims_count || 0} numeric/statutory claims checked against cited gazette text)</span>
        </div>`;
      } else {
        html += `<div class="verifier-status-badge warn">
          <span>⚠️ Statutory Verification Warning</span>
          <span style="font-weight:400;">(Potential ungrounded claims: ${v.ungrounded_claims.join(', ') || 'review required'})</span>
        </div>`;
      }
    }

    let formatted = data.answer.replace(/\n/g, '<br>');
    html += formatted;

    if (data.citations && data.citations.length > 0) {
      html += '<br><br><b>Ground-truth Statutory Citations:</b><br>';
      data.citations.forEach(c => {
        html += `<span class="citation-tag ${c.confidence}">[${c.id}] ${c.title} (${c.confidence})</span>`;
      });
    }

    const rulesVer = data._meta ? data._meta.rules_version : '2026-10-10.1';
    html += `<br><br><i style="color:#9aa59d;font-size:12px;">Ruleset: v${rulesVer} · ${data.disclaimer}</i>`;
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

    // EC Escalation
    if (data.ec_escalation_by_consecutive_year) {
      const esc = data.ec_escalation_by_consecutive_year;
      document.getElementById('ecYr1').innerText = `Rs ${esc.year_1_total_inr.toLocaleString('en-IN')}`;
      document.getElementById('ecYr2').innerText = `Rs ${esc.year_2_total_inr.toLocaleString('en-IN')}`;
      document.getElementById('ecYr3').innerText = `Rs ${esc.year_3_total_inr.toLocaleString('en-IN')}`;
    }

    // EC Refund Schedule
    document.getElementById('refYr1').innerText = data.ec_refund_schedule.year_1_fulfillment;
    document.getElementById('refYr2').innerText = data.ec_refund_schedule.year_2_fulfillment;
    document.getElementById('refYr3').innerText = data.ec_refund_schedule.year_3_fulfillment;

    // Energy Recovery Bridge Metrics (Track 03)
    if (data.energy_recovery) {
      const en = data.energy_recovery;
      document.getElementById('resEnergyFeedstock').innerText = en.non_recycled_energy_feedstock_mt + ' MT';
      document.getElementById('resThermalMwh').innerText = en.cement_kiln_coprocessing_thermal_mwh.toLocaleString('en-IN') + ' MWh';
      document.getElementById('resElectricalMwh').innerText = en.waste_to_energy_electrical_mwh.toLocaleString('en-IN') + ' MWh';
      document.getElementById('resCoalDisplaced').innerText = en.fossil_coal_displaced_mt_estimate.toLocaleString('en-IN') + ' MT';

      // Circular Waste-Flow Allocation Bar
      const total = data.total_introduced_packaging_mt || 1;
      const recMt = data.total_recycling_obligation_mt || 0;
      const wteMt = en.non_recycled_energy_feedstock_mt || 0;

      const recPct = Math.min(100, Math.round((recMt / total) * 100));
      const wtePct = Math.max(0, Math.min(100 - recPct, Math.round((wteMt / total) * 100)));

      const elRec = document.getElementById('flowRec');
      const elWte = document.getElementById('flowWte');

      elRec.style.width = recPct + '%';
      elRec.innerText = `Mandated Recycling: ${recPct}% (${recMt} MT)`;

      elWte.style.width = wtePct + '%';
      elWte.innerText = `Energy Recovery: ${wtePct}% (${wteMt} MT)`;

      document.getElementById('legRecText').innerText = `Mandated Mechanical Recycling: ${recMt} MT (${recPct}%)`;
      document.getElementById('legWteText').innerText = `Prescribed Energy Recovery: ${wteMt} MT (${wtePct}%)`;
    }

    const tbody = document.querySelector('#categoryTable tbody');
    tbody.innerHTML = '';
    for (const [key, c] of Object.entries(data.categories)) {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><b>${c.name.split(':')[0]}</b><br><span style="font-size:11px;color:#9aa59d">${c.name.split(':')[1]}</span></td>
        <td>${c.introduced_mt}</td>
        <td>${c.recycling_target_pct}%</td>
        <td><b>${c.recycling_obligation_mt}</b></td>
        <td><span style="color:#e9c46a;">${c.remainder_mt || 0}</span></td>
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
      const effective = c.effective_from ? ` · Effective: ${c.effective_from}` : '';
      html += `
        <div style="background:#0f1511; border:1px solid var(--border); border-radius:6px; padding:12px; margin-bottom:10px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <b style="font-size:13.5px; color:#e1e7e2;">[${c.id}] ${c.title}</b>
            <span class="citation-tag ${c.confidence}">${c.confidence}</span>
          </div>
          <div style="font-size:12px; color:var(--text-muted); margin-bottom:6px;"><b>Citation:</b> ${c.citation}${effective}</div>
          <div style="font-size:12.5px; color:#c5cdc7; line-height:1.4;">${c.text_preview}</div>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = 'Error loading knowledge base: ' + e;
  }
}

// ── Mentor Feature 1: Enterprise Leaderboard ─────────────────────────────
let leaderboardCache = null;

async function loadLeaderboard() {
  const tbody = document.getElementById('leaderboardBody');
  if (!tbody) return;
  try {
    const res = await fetch('/api/leaderboard');
    const data = await res.json();
    leaderboardCache = data.rankings;
    renderLeaderboardRows(data.rankings);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="6" style="color:#f4a261;">Error loading leaderboard: ${e}</td></tr>`;
  }
}

function filterLeaderboard(filter) {
  if (!leaderboardCache) return;
  if (filter === 'all') {
    renderLeaderboardRows(leaderboardCache);
  } else if (filter === 'green') {
    renderLeaderboardRows(leaderboardCache.filter(c => c.esg_score >= 85));
  } else if (filter === 'red') {
    renderLeaderboardRows(leaderboardCache.filter(c => c.esg_score < 60));
  }
}

function renderLeaderboardRows(companies) {
  const tbody = document.getElementById('leaderboardBody');
  if (!tbody) return;
  tbody.innerHTML = '';
  companies.forEach((c, idx) => {
    const isGreen = c.esg_score >= 85;
    const isRed = c.esg_score < 60;
    const scoreColor = isGreen ? '#74c69d' : (isRed ? '#e76f51' : '#f3c969');
    const statusBadge = isGreen 
      ? '<span class="citation-tag verified">Green (Compliant)</span>' 
      : (isRed ? '<span class="citation-tag needs_verify">Red (Defaulter)</span>' : '<span class="citation-tag reported">Amber (Monitored)</span>');

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><b>#${idx + 1} ${c.name}</b><br><span style="font-size:11px;color:#9aa59d;">Reg: ${c.cpcb_reg}</span></td>
      <td style="font-size:12px;color:#c5cdc7;">${c.sector}</td>
      <td><b>${c.annual_plastic_mt.toLocaleString('en-IN')} MT</b></td>
      <td>${c.recycling_achieved_pct}% (rPET: ${c.recycled_content_pct}%)</td>
      <td><b style="color:${scoreColor};font-size:15px;">${c.esg_score}/100</b></td>
      <td>
        ${statusBadge}<br>
        <span style="font-size:11.5px;color:${isRed ? '#f4a261' : '#95d5b2'};">${c.subsidy_eligible}</span>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// ── Mentor Feature 2: Plastic Road Reuse Evaluation (IRC:SP:98) ────────────
async function runRoadEvaluation() {
  const polymer = document.getElementById('roadPolymerSelect')?.value || 'ldpe';
  const tonnage = parseFloat(document.getElementById('roadTonnageInput')?.value) || 0;

  try {
    const res = await fetch('/api/road-reuse/evaluate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({polymer, tonnage})
    });
    const d = await res.json();

    document.getElementById('roadPolymerName').innerText = d.polymer_evaluated;
    const badge = document.getElementById('roadSuitabilityBadge');
    if (d.is_prohibited) {
      badge.className = 'citation-tag needs_verify';
      badge.innerText = 'STRICTLY PROHIBITED (0% - TOXIC)';
    } else if (d.suitability_score_pct >= 85) {
      badge.className = 'citation-tag verified';
      badge.innerText = `${d.suitability_status} (${d.suitability_score_pct}% Compliant)`;
    } else {
      badge.className = 'citation-tag reported';
      badge.innerText = `${d.suitability_status} (${d.suitability_score_pct}%)`;
    }

    document.getElementById('roadKmPaved').innerText = d.road_impact.potential_highway_km_paved + ' km';
    document.getElementById('roadPouchesDiverted').innerText = d.road_impact.single_use_plastics_diverted.toLocaleString('en-IN');
    document.getElementById('roadBlendPct').innerText = d.recommended_blend_pct;
    document.getElementById('roadEolCredit').innerText = '₹' + d.road_impact.estimated_cpcb_eol_credit_value_inr.toLocaleString('en-IN');
    document.getElementById('roadTechnicalVerdict').innerText = d.technical_verdict;
  } catch (e) {
    console.warn('Road evaluation error:', e);
  }
}

// ── Mentor Feature 3: Compliance & Penalty Resolution Engine ────────────
let lastAuditResult = null;
let auditSamplesCache = null;

async function initAuditTab() {
  if (!lastAuditResult) {
    runAuditEvaluation();
  }
}

async function loadSampleManifest(sampleKey) {
  try {
    if (!auditSamplesCache) {
      const res = await fetch('/api/audit/samples');
      auditSamplesCache = await res.json();
    }
    const sample = auditSamplesCache[sampleKey];
    if (sample) {
      document.getElementById('auditCompanyId').value = sample.company_id || '';
      document.getElementById('auditCompanyName').value = sample.company_name || '';
      document.getElementById('auditTotalIntroduced').value = sample.manifest_tonnage_introduced_mt || 0;
      document.getElementById('auditWasteUtilized').value = sample.waste_utilized_mt || 0;
      document.getElementById('auditMandatedPct').value = sample.mandated_threshold_pct || 70;
      document.getElementById('auditDefaultYear').value = sample.consecutive_default_year || 1;
      await runAuditEvaluation();
    }
  } catch (e) {
    console.warn('Error loading sample manifest:', e);
  }
}

async function runAuditEvaluation() {
  const company_id = document.getElementById('auditCompanyId')?.value.trim() || 'CPCB-GEN-001';
  const company_name = document.getElementById('auditCompanyName')?.value.trim() || 'Generic Plastics Pvt Ltd';
  const manifest_tonnage_introduced_mt = parseFloat(document.getElementById('auditTotalIntroduced')?.value) || 0;
  const waste_utilized_mt = parseFloat(document.getElementById('auditWasteUtilized')?.value) || 0;
  const mandated_threshold_pct = parseFloat(document.getElementById('auditMandatedPct')?.value) || 70;
  const consecutive_default_year = parseInt(document.getElementById('auditDefaultYear')?.value) || 1;

  try {
    const res = await fetch('/api/audit/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_id,
        company_name,
        manifest_tonnage_introduced_mt,
        waste_utilized_mt,
        mandated_threshold_pct,
        consecutive_default_year
      })
    });
    const d = await res.json();
    lastAuditResult = d;

    const container = document.getElementById('auditResultContainer');
    if (container) container.style.display = 'block';

    document.getElementById('auditEntityMeta').innerText = d.company_id;
    document.getElementById('auditEntityName').innerText = d.company_name;

    const badge = document.getElementById('auditStatusBadge');
    if (d.compliance_status === 'COMPLIANT') {
      badge.className = 'badge live';
      badge.style.background = 'var(--badge-live)';
      badge.style.color = 'var(--badge-live-text)';
      badge.innerText = 'COMPLIANT';
      if (container) container.style.borderColor = '#2d6a4f';
    } else if (d.compliance_status === 'WARNING') {
      badge.className = 'badge mock';
      badge.style.background = 'var(--badge-mock)';
      badge.style.color = 'var(--badge-mock-text)';
      badge.innerText = 'WARNING';
      if (container) container.style.borderColor = '#b5832a';
    } else {
      badge.className = 'badge';
      badge.style.background = '#d06d4e';
      badge.style.color = '#ffffff';
      badge.innerText = 'PENALIZED';
      if (container) container.style.borderColor = '#993b2a';
    }

    const metrics = d.metrics || d.audit_metrics || {};
    const fin = d.financial_resolution || d.resolution_action || {};

    const utilMetric = document.getElementById('auditUtilizationMetric');
    const color = d.compliance_status === 'COMPLIANT' ? '#52b788' : (d.compliance_status === 'WARNING' ? '#f4a261' : '#e76f51');
    utilMetric.innerHTML = `<span style="color: ${color};">${metrics.actual_utilization_pct || 0}%</span> <span style="font-size: 13px; color: var(--text-muted);">/ ${metrics.mandated_threshold_pct || 70}% Target</span>`;
    document.getElementById('auditTonnageMetric').innerText = `Utilized: ${metrics.waste_utilized_mt || 0} MT | Mandated: ${metrics.mandated_threshold_mt || metrics.mandated_target_mt || 0} MT`;

    const labelEl = document.getElementById('auditCreditOrFineLabel');
    const valEl = document.getElementById('auditCreditOrFineVal');
    const subEl = document.getElementById('auditCreditOrFineSub');

    if (d.compliance_status === 'COMPLIANT') {
      labelEl.innerText = 'Net Green Credits Earned';
      valEl.style.color = '#74c69d';
      const credits = fin.net_credits_earned !== undefined ? fin.net_credits_earned : (fin.green_credits_earned_mt || 0);
      valEl.innerText = `+${credits} MT`;
      const valInr = (fin.green_credit_monetary_value_inr || 0).toLocaleString('en-IN');
      subEl.innerText = `Monetary Equivalent: ₹${valInr}`;
    } else if (d.compliance_status === 'WARNING') {
      labelEl.innerText = 'Regulatory Warning / Deficit';
      valEl.style.color = '#f4a261';
      valEl.innerText = `-${metrics.shortfall_mt || 0} MT Shortfall`;
      subEl.innerText = 'Deficit within 30-day statutory cure window';
    } else {
      labelEl.innerText = 'Statutory Fine Levied (EC)';
      valEl.style.color = '#e76f51';
      const fineInr = (fin.fine_levied_inr || 0).toLocaleString('en-IN');
      valEl.innerText = `₹${fineInr}`;
      const rateInr = (fin.penalty_rate_per_mt_inr || 0).toLocaleString('en-IN');
      subEl.innerText = `Tier: ${fin.penalty_tier} (@ ₹${rateInr}/MT)`;
    }

    document.getElementById('auditPenaltyTierPill').innerText = `Tier: ${fin.penalty_tier || 'NONE'}`;
    document.getElementById('auditGuidelineCitation').innerText = d.statutory_guideline_summary;

    const suspBox = document.getElementById('auditSuspensionBox');
    if (d.suspension_notice_payload) {
      suspBox.style.display = 'block';
      const susp = d.suspension_notice_payload;
      document.getElementById('suspensionNoticeId').innerText = susp.notice_id || susp.notice_reference_id || 'CPCB/PWM/SUSP/001';
      document.getElementById('suspensionGrounds').innerText = susp.fine_breakdown ? `Shortfall of ${susp.fine_breakdown.shortfall_mt} MT under ${susp.fine_breakdown.tier}` : 'Critical shortfall against Schedule II mandate';
      document.getElementById('suspensionAct').innerText = Array.isArray(susp.governing_statutes) ? susp.governing_statutes.join('; ') : (susp.issued_under_act || 'Section 15, EPA 1986');
      document.getElementById('suspensionAction').innerText = susp.action_levied || susp.cpcb_portal_action || 'PORTAL TRADING SUSPENSION';
      document.getElementById('suspensionCurePeriod').innerText = susp.curative_remedy || '15 calendar days';
      document.getElementById('suspensionNoticeText').innerText = `NOTICE: Pursuant to statutory powers vested under Section 15 of Environment (Protection) Act 1986, trading privileges for ${d.company_name} are restricted pending settlement of assessed penalty ₹${(susp.total_fine_inr || fin.fine_levied_inr || 0).toLocaleString('en-IN')}.`;
    } else {
      suspBox.style.display = 'none';
    }
  } catch (e) {
    console.error('Audit evaluation error:', e);
  }
}

function exportAuditResultJSON() {
  if (!lastAuditResult) {
    alert('Please evaluate a manifest before exporting.');
    return;
  }
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(lastAuditResult, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", `CPCB_Audit_Report_${lastAuditResult.company_id}_${lastAuditResult.compliance_status}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}

function printAuditNotice() {
  window.print();
}

