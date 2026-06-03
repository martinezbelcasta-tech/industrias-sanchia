/* ============================================================
   INDUSTRIAS SANCHIA — App: views, nav, rendering
   ============================================================ */
(function () {
  const D = window.SANCHIA, CH = window.CHART, C = D.COLORS;

  /* ---- tiny inline icons ---- */
  const I = {
    grid: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
    clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    health: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 9h18M12 12v5M9.5 14.5h5"/></svg>',
    gauge: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 16a8 8 0 0 1 16 0"/><path d="M12 16l4-4"/></svg>',
    cog: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M12 3v2.5M12 18.5V21M21 12h-2.5M5.5 12H3M18 6l-1.8 1.8M7.8 16.2 6 18M18 18l-1.8-1.8M7.8 7.8 6 6"/></svg>',
    bolt: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M13 3 5 13h6l-1 8 8-10h-6l1-8Z"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12.5 10 17l9-10"/></svg>',
    cal: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/></svg>',
    down: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 4v12M7 11l5 5 5-5M5 20h14"/></svg>',
    arrUp: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 19V6M6 11l6-6 6 6"/></svg>',
    arrDn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 5v13M6 13l6 6 6-6"/></svg>',
    users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="9" cy="8" r="3.2"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0M16 6.2a3 3 0 0 1 0 5.6M21 20a5.2 5.2 0 0 0-3.5-4.9"/></svg>',
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>',
    info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.5v.5"/></svg>',
  };

  const delta = (val, dir) => {
    const cls = dir === 'up' ? 'up' : dir === 'down' ? 'down' : 'flat';
    const ic = dir === 'up' ? I.arrUp : dir === 'down' ? I.arrDn : '';
    return `<span class="delta ${cls}">${ic}${val}</span>`;
  };

  const kpi = (label, value, unit, iconKey, gold, foot) => `
    <div class="kpi">
      <div class="kpi__top">
        <span class="kpi__label">${label}</span>
        <span class="kpi__icon ${gold ? 'is-gold' : ''}">${I[iconKey]}</span>
      </div>
      <div class="kpi__value">${value}${unit ? `<span class="u">${unit}</span>` : ''}</div>
      <div class="kpi__foot">${foot}</div>
    </div>`;

  const legend = items => `<div class="legend">${items.map(i => `<span><i style="background:${i.color}"></i>${i.label}</span>`).join('')}</div>`;

  /* ============================================================
     VIEW 1 — RESUMEN GENERAL
     ============================================================ */
  function viewResumen() {
    const topMachines = D.MACHINES.slice(0, 6).map(m => ({ k: m.maquina, v: m.total, label: m.total + ' h' }));
    const ausTipos = [
      { k: 'Incapacidad médica', v: D.T_INC, label: D.T_INC + ' días', color: C.navy },
      { k: 'Permiso personal', v: D.T_PERM, label: D.T_PERM + ' días', color: C.gold },
      { k: 'Falta injustificada', v: D.T_FALTA, label: D.T_FALTA + ' días', color: C.brick },
    ];
    return `
      <div class="grid grid--kpi">
        ${kpi('Tiempo total arranques', D.TOTAL_HORAS, 'hrs', 'clock', false, `${delta('8.4%', 'down')} vs. abril`)}
        ${kpi('Máquinas activas', D.MACHINES.length, '', 'cog', true, `${delta('+1', 'up')} en operación`)}
        ${kpi('Promedio por arranque', D.PROM_HORAS, 'hrs', 'gauge', false, `${delta('0.2 h', 'down')} más ágil`)}
        ${kpi('Ausentismo del mes', D.T_INC + D.T_PERM + D.T_FALTA, 'días', 'users', true, `${delta('3.1%', 'up')} vs. abril`)}
      </div>

      <div class="grid grid--3-1 mt">
        <div class="card">
          <div class="card__head">
            <div><h3>Tiempo de arranque por día</h3><div class="sub">Horas totales registradas · mayo 2026</div></div>
            ${legend([{ label: 'Horas', color: C.navy }])}
          </div>
          <div class="card__body">${CH.area(D.TREND, { color: C.navy })}</div>
        </div>
        <div class="card">
          <div class="card__head"><div><h3>Distribución por proceso</h3><div class="sub">Mayo 2026</div></div></div>
          <div class="card__body">
            ${CH.donut(D.PROCESOS)}
            <div class="divider" style="margin:16px 0 14px"></div>
            ${legend(D.PROCESOS.map(p => ({ label: `${p.name} · ${p.value}h`, color: p.color })))}
          </div>
        </div>
      </div>

      <div class="grid grid--2 mt">
        <div class="card">
          <div class="card__head"><div><h3>Máquinas por tiempo total</h3><div class="sub">Top 6 · horas acumuladas</div></div></div>
          <div class="card__body"><div class="rowlist">${CH.hbars(topMachines, { color: C.navy })}</div></div>
        </div>
        <div class="card">
          <div class="card__head"><div><h3>Ausentismo por tipo</h3><div class="sub">Días registrados · mayo 2026</div></div></div>
          <div class="card__body"><div class="rowlist">${CH.hbars(ausTipos)}</div>
            <div class="note" style="margin-top:18px">${I.info}<span><strong>3 faltas injustificadas</strong> concentradas en el Grupo C. Considera revisión con supervisores asignados.</span></div>
          </div>
        </div>
      </div>`;
  }

  /* ============================================================
     VIEW 2 — TIEMPOS DE ARRANQUE
     ============================================================ */
  function viewTiempos() {
    const series = [
      { key: 'cambio', label: 'Cambio de molde', color: C.navy },
      { key: 'arr', label: 'Arranque', color: C.gold },
      { key: 'val', label: 'Validación calidad', color: C.steel },
    ];
    const totalBars = D.MACHINES.map(m => ({ k: m.maquina, v: m.total }));
    const rows = D.MACHINES.map(m => {
      const maxT = D.MACHINES[0].total;
      return `<tr>
        <td>${m.maquina}</td>
        <td>${m.n}</td>
        <td>${m.cambio.toFixed(1)}</td>
        <td>${m.arr.toFixed(1)}</td>
        <td>${m.val.toFixed(1)}</td>
        <td><span class="bar-cell"><span class="mini"><i style="width:${(m.total / maxT) * 100}%"></i></span><strong style="color:var(--navy);font-variant-numeric:tabular-nums">${m.total.toFixed(1)}</strong></span></td>
      </tr>`;
    }).join('');

    return `
      <div class="grid grid--kpi">
        ${kpi('Total de registros', D.REGISTROS.length, '', 'clock', false, 'Periodo mayo 2026')}
        ${kpi('Máquinas activas', D.MACHINES.length, '', 'cog', true, 'Línea de inyección')}
        ${kpi('Tiempo total', D.TOTAL_HORAS, 'hrs', 'gauge', false, `${delta('8.4%', 'down')} vs. abril`)}
        ${kpi('Promedio por arranque', D.PROM_HORAS, 'hrs', 'bolt', true, 'Cambio + arranque + QA')}
      </div>

      <div class="card mt">
        <div class="card__head">
          <div><h3>Desglose de tiempos por máquina</h3><div class="sub">Horas por etapa del proceso de arranque</div></div>
          ${legend(series.map(s => ({ label: s.label, color: s.color })))}
        </div>
        <div class="card__body">${CH.stackedBar(D.MACHINES, series, { xkey: 'maquina' })}</div>
      </div>

      <div class="grid grid--3-1 mt">
        <div class="card">
          <div class="card__head"><div><h3>Tiempo total por máquina</h3><div class="sub">Horas acumuladas</div></div></div>
          <div class="card__body">${CH.bars(totalBars, { color: C.navy })}</div>
        </div>
        <div class="card">
          <div class="card__head"><div><h3>Total por proceso</h3></div></div>
          <div class="card__body">${CH.donut(D.PROCESOS)}
            <div class="divider" style="margin:14px 0 12px"></div>
            ${legend(D.PROCESOS.map(p => ({ label: `${p.name}`, color: p.color })))}
          </div>
        </div>
      </div>

      <div class="card mt">
        <div class="card__head"><div><h3>Detalle por máquina</h3><div class="sub">${D.MACHINES.length} máquinas · ordenado por tiempo total</div></div>
          <button class="chip">${I.down} Exportar CSV</button>
        </div>
        <div class="card__body">
          <div class="table-wrap"><table class="data">
            <thead><tr><th>Máquina</th><th>Registros</th><th>Cambio molde (h)</th><th>Arranque (h)</th><th>Validación (h)</th><th>Total (h)</th></tr></thead>
            <tbody>${rows}</tbody>
          </table></div>
        </div>
      </div>`;
  }

  /* ============================================================
     VIEW 3 — REGISTRO DE INCAPACIDADES
     ============================================================ */
  function viewIncap() {
    const supSeries = [
      { key: 'inc', label: 'Incapacidad', color: C.navy },
      { key: 'perm', label: 'Permiso', color: C.gold },
      { key: 'falta', label: 'Falta', color: C.brick },
    ];
    const supData = D.AUS_SUP.map(s => ({ name: s.name, inc: s.inc, perm: s.perm, falta: s.falta }));
    const tagFor = r => {
      if (r.falta) return '<span class="tag brick">Falta injust.</span>';
      if (r.inc) return '<span class="tag navy">Incapacidad</span>';
      if (r.perm) return '<span class="tag gold">Permiso</span>';
      return '<span class="tag muted">—</span>';
    };
    const dias = r => r.inc || r.perm || r.falta || 0;
    const rows = D.INCAP.map(r => `<tr>
      <td>${r.nombre}</td>
      <td><span class="tag muted">Grupo ${r.grupo}</span></td>
      <td style="text-align:left">${r.sup}</td>
      <td>${r.fecha}</td>
      <td>${tagFor(r)}</td>
      <td><strong style="color:var(--ink)">${dias(r)}</strong></td>
    </tr>`).join('');

    const opt = arr => arr.map(o => `<option>${o}</option>`).join('');

    return `
      <div class="grid grid--kpi">
        ${kpi('Total de registros', D.INCAP.length, '', 'health', false, 'Periodo mayo 2026')}
        ${kpi('Días de incapacidad', D.T_INC, 'días', 'health', false, `${delta('2.0%', 'up')} médicas`)}
        ${kpi('Permisos personales', D.T_PERM, 'días', 'cal', true, 'Autorizados')}
        ${kpi('Faltas injustificadas', D.T_FALTA, 'días', 'users', false, `${delta('+1', 'up')} requiere atención`)}
      </div>

      <div class="grid grid--1-3 mt" style="align-items:start">
        <div class="card">
          <div class="card__head"><div><h3>Nuevo registro</h3><div class="sub">Captura de ausencia</div></div></div>
          <div class="card__body">
            <form class="form-grid" onsubmit="return SANCHIA_APP.fakeSubmit(event)">
              <div class="field" style="grid-column:1/-1"><label>Empleado</label><select>${opt([''].concat(D.EMPLEADOS))}</select></div>
              <div class="field"><label>Grupo</label><select>${opt(['', 'A', 'B', 'C'])}</select></div>
              <div class="field"><label>Fecha</label><input type="date" value="2026-06-03"></div>
              <div class="field" style="grid-column:1/-1"><label>Supervisor</label><select>${opt([''].concat(D.SUPERVISORES))}</select></div>
              <div class="section-label">Tipo de ausencia</div>
              <div class="field field--inline"><div class="field" style="gap:6px"><label>Incapacidad</label><select>${opt(['No', 'Sí'])}</select></div><div class="field" style="gap:6px"><label>Días</label><input type="number" min="0" value="0"></div></div>
              <div class="field field--inline"><div class="field" style="gap:6px"><label>Permiso</label><select>${opt(['No', 'Sí'])}</select></div><div class="field" style="gap:6px"><label>Días</label><input type="number" min="0" value="0"></div></div>
              <div class="field field--inline" style="grid-column:1/-1"><div class="field" style="gap:6px"><label>Falta injustificada</label><select>${opt(['No', 'Sí'])}</select></div><div class="field" style="gap:6px"><label>Días</label><input type="number" min="0" value="0"></div></div>
              <button class="btn btn--gold" type="submit" style="grid-column:1/-1;justify-content:center;margin-top:4px">${I.plus} Guardar registro</button>
            </form>
          </div>
        </div>

        <div style="display:flex;flex-direction:column;gap:18px">
          <div class="card">
            <div class="card__head">
              <div><h3>Ausentismo por supervisor</h3><div class="sub">Días por tipo · mayo 2026</div></div>
              ${legend(supSeries.map(s => ({ label: s.label, color: s.color })))}
            </div>
            <div class="card__body">${CH.stackedBar(supData, supSeries, { xkey: 'name' })}</div>
          </div>
        </div>
      </div>

      <div class="card mt">
        <div class="card__head"><div><h3>Detalle de registros</h3><div class="sub">${D.INCAP.length} registros · mayo 2026</div></div>
          <button class="chip">${I.down} Exportar CSV</button>
        </div>
        <div class="card__body">
          <div class="table-wrap"><table class="data">
            <thead><tr><th>Empleado</th><th style="text-align:left">Grupo</th><th style="text-align:left">Supervisor</th><th style="text-align:left">Fecha</th><th style="text-align:left">Tipo</th><th>Días</th></tr></thead>
            <tbody>${rows}</tbody>
          </table></div>
        </div>
      </div>`;
  }

  /* ============================================================
     Nav + header
     ============================================================ */
  const VIEWS = {
    resumen: { title: 'Resumen General', sub: 'Panel ejecutivo · Operación y personal', render: viewResumen },
    tiempos: { title: 'Tiempos de Arranque', sub: 'Análisis del proceso de arranque por máquina', render: viewTiempos },
    incap: { title: 'Registro de Incapacidades', sub: 'Control de incapacidades, permisos y faltas', render: viewIncap },
  };

  function go(key) {
    const v = VIEWS[key];
    document.querySelectorAll('.nav__item').forEach(b => b.classList.toggle('is-active', b.dataset.view === key));
    document.getElementById('pageTitle').textContent = v.title;
    document.getElementById('pageSub').textContent = v.sub;
    document.getElementById('content').innerHTML = v.render();
    document.querySelector('.main').scrollTo({ top: 0 });
    window.scrollTo({ top: 0 });
    history.replaceState(null, '', '#' + key);
  }

  function fakeSubmit(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type=submit]');
    const old = btn.innerHTML;
    btn.innerHTML = '✓ Registro guardado';
    btn.style.background = 'var(--moss)';
    setTimeout(() => { btn.innerHTML = old; btn.style.background = ''; e.target.reset(); }, 1600);
    return false;
  }

  window.SANCHIA_APP = { go, fakeSubmit };
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav__item').forEach(b => b.addEventListener('click', () => go(b.dataset.view)));
    const start = (location.hash || '').replace('#', '');
    go(VIEWS[start] ? start : 'resumen');
  });
})();
