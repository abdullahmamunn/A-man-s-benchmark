(function () {
  let weekStart = null;

  function inWeek(isoDate, start) {
    if (!isoDate) return false;
    const end = AMB.addDaysIso(start, 6);
    const day = isoDate.slice(0, 10);
    return day >= start && day <= end;
  }

  function field(name, label, value, hint) {
    return `
      <label class="field">
        ${label}
        ${hint ? `<span class="hint">${hint}</span>` : ''}
        <textarea name="${name}">${AMB.escape(value || '')}</textarea>
      </label>`;
  }

  async function render(root, alive) {
    if (!weekStart) weekStart = AMB.monday(0);
    const [reviews, tasks, sessions, scores] = await Promise.all([
      AMB.getReviews(),
      AMB.getTasks(),
      AMB.getSessions(),
      AMB.getWeeklyScores(weekStart),
    ]);
    if (!alive()) return;
    const current = reviews.find((review) => review.week_start === weekStart) || {
      accomplishments: '',
      failures: '',
      distractions: '',
      lessons_learned: '',
      next_week_improvements: '',
      non_negotiable_1: '',
      non_negotiable_2: '',
      non_negotiable_3: '',
    };
    const completed = tasks.filter((task) => task.status === 'Completed' && inWeek(AMB.dateInZone(task.completed_at), weekStart)).length;
    const minutes = sessions
      .filter((session) => inWeek(session.date, weekStart))
      .reduce((total, session) => total + Number(session.duration_minutes || 0), 0);
    const average = scores.length
      ? (scores.reduce((total, score) => total + Number(score.rating), 0) / scores.length).toFixed(1)
      : '—';
    const archive = [...reviews].sort((a, b) => b.week_start.localeCompare(a.week_start));

    root.innerHTML = `
      <div class="page-head">
        <div>
          <h1>Weekly Reflection</h1>
          <p class="lede">Priority #1 is reserved for academy standing. Write what happened, not how it felt.</p>
        </div>
        <div class="week-switch">
          <button type="button" class="btn secondary small" id="prev-week">Previous</button>
          <strong>Week of ${AMB.escape(AMB.formatLong(weekStart))}</strong>
          <button type="button" class="btn secondary small" id="next-week">Next</button>
        </div>
      </div>
      <div class="summary-strip">
        <article class="card"><h3>Tasks completed</h3><strong class="metric">${completed}</strong></article>
        <article class="card"><h3>Logged hours</h3><strong class="metric">${(minutes / 60).toFixed(1)}</strong></article>
        <article class="card"><h3>Scoreboard avg</h3><strong class="metric">${average}</strong></article>
      </div>
      <div class="layout-main">
        <form class="card stack" id="review-form">
          ${field('accomplishments', 'Accomplishments', current.accomplishments)}
          ${field('failures', 'Failures and shortcomings', current.failures)}
          ${field('distractions', 'Distractions and energy leaks', current.distractions)}
          ${field('lessons_learned', 'Lessons learned', current.lessons_learned)}
          ${field('next_week_improvements', 'Next week', current.next_week_improvements)}
          <label class="field">Non-negotiable #1
            <span class="hint">Academy standing. This one is required.</span>
            <input name="non_negotiable_1" required value="${AMB.escape(current.non_negotiable_1 || '')}">
          </label>
          <label class="field">Non-negotiable #2
            <input name="non_negotiable_2" value="${AMB.escape(current.non_negotiable_2 || '')}">
          </label>
          <label class="field">Non-negotiable #3
            <input name="non_negotiable_3" value="${AMB.escape(current.non_negotiable_3 || '')}">
          </label>
          <p class="error-text"></p>
          <div><button class="btn" type="submit">Save reflection</button></div>
        </form>
        <aside class="card">
          <h2>Archive</h2>
          <div class="archive">
            ${archive.length ? archive.map((review) => `
              <button type="button" data-week="${AMB.escape(review.week_start)}" class="${review.week_start === weekStart ? 'active' : ''}">
                <span class="when">${AMB.escape(AMB.formatLong(review.week_start))}</span>
                <span class="snip">${AMB.escape(review.non_negotiable_1 || 'No priority #1')}</span>
              </button>`).join('') : '<p class="empty">No reflections filed yet.</p>'}
          </div>
        </aside>
      </div>`;

    AMB.bind(root, 'click', (event) => {
      if (event.target.id === 'prev-week' || event.target.id === 'next-week') {
        weekStart = AMB.addDaysIso(weekStart, event.target.id === 'next-week' ? 7 : -7);
        render(root, alive);
        return;
      }
      const archived = event.target.closest('[data-week]');
      if (!archived) return;
      weekStart = archived.dataset.week;
      render(root, alive);
    });
    AMB.bind(root, 'submit', async (event) => {
      if (event.target.id !== 'review-form') return;
      event.preventDefault();
      const form = new FormData(event.target);
      const payload = { week_start: weekStart };
      ['accomplishments', 'failures', 'distractions', 'lessons_learned', 'next_week_improvements', 'non_negotiable_1', 'non_negotiable_2', 'non_negotiable_3']
        .forEach((key) => { payload[key] = String(form.get(key) || '').trim(); });
      const button = event.target.querySelector('[type="submit"]');
      button.disabled = true;
      try {
        await AMB.saveReview(payload);
        AMB.toast('Reflection saved.');
        await render(root, alive);
      } catch (err) {
        event.target.querySelector('.error-text').textContent = err.message;
        button.disabled = false;
      }
    });
  }

  window.Reflection = { render };
})();
