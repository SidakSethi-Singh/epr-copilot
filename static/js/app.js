// EPR Compliance Copilot - Frontend Logic with Energy Recovery & Verifier UI

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
      html += '<br><br><b>Ground-Truth Citations:</b><br>';
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
    loading.style.display = 'none';
  }
}

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
