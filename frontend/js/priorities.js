(function () {
  const state = {
    q: '',
    category: 'All',
    priority: 'All',
    status: 'All',
    sort: 'academy_first',
  };

  function options(values, selected, allLabel) {
    const head = allLabel ? `<option value="All"${selected === 'All' ? ' selected' : ''}>${allLabel}</option>` : '';
    return head + values.map((value) => (
      `<option value="${AMB.escape(value)}"${value === selected ? ' selected' : ''}>${AMB.escape(value)}</option>`
    )).join('');
  }

  function row(task) {
    const done = task.status === 'Completed';
    const academy = task.category === 'University Coursework';
    return `
      <article class="task${done ? ' done' : ''}">
        <button type="button" class="check" data-action="toggle" data-id="${task.id}" aria-label="${done ? 'Reopen priority' : 'Mark complete'}">${done ? '✓' : ''}</button>
        <div>
          <div class="task-title">${AMB.escape(task.title)}</div>
          <div class="task-meta">
            ${academy ? '<span class="pill pill-academy">Academy #1</span>' : `<span class="pill">${AMB.escape(task.category)}</span>`}
            <span class="pill${task.priority === 'High' ? ' pill-high' : ''}">${AMB.escape(task.priority)}</span>
            <span>${AMB.escape(task.status)}</span>
            <span>Due ${AMB.escape(AMB.formatLong(task.due_date))}</span>
          </div>
          ${task.description ? `<p class="task-dod">${AMB.escape(task.description)}</p>` : ''}
        </div>
        <div class="task-actions">
          <button type="button" class="linkish" data-action="edit" data-id="${task.id}">Edit</button>
          <button type="button" class="linkish danger" data-action="delete" data-id="${task.id}">Delete</button>
        </div>
      </article>`;
  }

  function openModal(task) {
    const current = task || {
      title: '',
      description: '',
      category: 'University Coursework',
      priority: 'High',
      due_date: '',
      status: 'Pending',
    };
    AMB.modal(`
      <h2 id="dialog-title">${task ? 'Edit priority' : 'Add priority'}</h2>
      <form>
        <div class="form-grid">
          <label class="field wide">Title
            <input name="title" required value="${AMB.escape(current.title)}">
          </label>
          <label class="field wide">Standard of completion
            <span class="hint">What must be true when this is done.</span>
            <textarea name="description">${AMB.escape(current.description || '')}</textarea>
          </label>
          <label class="field">Category
            <select name="category">${options(AMB.CATEGORIES, current.category)}</select>
          </label>
          <label class="field">Priority
            <select name="priority">${options(AMB.PRIORITIES, current.priority)}</select>
          </label>
          <label class="field">Due date
            <input type="date" name="due_date" value="${AMB.escape(current.due_date || '')}">
          </label>
          <label class="field">Status
            <select name="status">${options(AMB.STATUSES, current.status)}</select>
          </label>
        </div>
        <p class="error-text"></p>
        <div class="actions">
          <button class="btn" type="submit">Save priority</button>
          <button class="btn secondary" type="button" data-close>Cancel</button>
        </div>
      </form>`, (root) => {
      const dialog = root.querySelector('.modal');
      dialog.setAttribute('aria-labelledby', 'dialog-title');
      root.querySelector('input[name="title"]').focus();
      root.querySelector('form').addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = new FormData(event.target);
        const payload = {
          title: String(form.get('title') || '').trim(),
          description: String(form.get('description') || '').trim(),
          category: form.get('category'),
          priority: form.get('priority'),
          due_date: form.get('due_date') || null,
          status: form.get('status'),
        };
        const button = event.target.querySelector('[type="submit"]');
        button.disabled = true;
        try {
          await AMB.saveTask(payload, task && task.id);
          AMB.closeModal();
          AMB.toast(task ? 'Priority updated.' : 'Priority added.');
          await App.show('priorities', true);
        } catch (err) {
          root.querySelector('.error-text').textContent = err.message;
          button.disabled = false;
        }
      });
    });
  }

  async function render(root, alive) {
    const tasks = await AMB.getTasks();
    if (!alive()) return;
    const matches = (task) => {
      if (state.category !== 'All' && task.category !== state.category) return false;
      if (state.priority !== 'All' && task.priority !== state.priority) return false;
      if (state.status !== 'All' && task.status !== state.status) return false;
      if (state.q) {
        const hay = `${task.title} ${task.description || ''}`.toLowerCase();
        if (!hay.includes(state.q.toLowerCase())) return false;
      }
      return true;
    };

    root.innerHTML = `
      <div class="page-head">
        <div>
          <h1>My Priorities</h1>
          <p class="lede">University coursework sorts ahead of research and side work.</p>
        </div>
        <button type="button" class="btn" id="add-task">Add priority</button>
      </div>
      <div class="filters">
        <input id="q" type="search" placeholder="Search title or standard" value="${AMB.escape(state.q)}">
        <select id="category">${options(AMB.CATEGORIES, state.category, 'All categories')}</select>
        <select id="priority">${options(AMB.PRIORITIES, state.priority, 'All priorities')}</select>
        <select id="status">${options(AMB.STATUSES, state.status, 'All statuses')}</select>
        <select id="sort">
          <option value="academy_first"${state.sort === 'academy_first' ? ' selected' : ''}>Academy first</option>
          <option value="due_date"${state.sort === 'due_date' ? ' selected' : ''}>Due date</option>
          <option value="priority"${state.sort === 'priority' ? ' selected' : ''}>Priority</option>
          <option value="status"${state.sort === 'status' ? ' selected' : ''}>Status</option>
        </select>
      </div>
      <section class="card">
        <div class="task-list" id="task-list"></div>
      </section>`;

    const listEl = root.querySelector('#task-list');
    const paint = () => {
      const visible = AMB.sortTasks(tasks.filter(matches), state.sort);
      const empty = tasks.length ? 'Nothing matches these filters.' : 'The queue is empty. Add the first priority.';
      listEl.innerHTML = visible.length ? visible.map(row).join('') : `<p class="empty">${empty}</p>`;
    };
    const read = () => {
      state.q = root.querySelector('#q').value;
      state.category = root.querySelector('#category').value;
      state.priority = root.querySelector('#priority').value;
      state.status = root.querySelector('#status').value;
      state.sort = root.querySelector('#sort').value;
      paint();
    };
    paint();
    AMB.bind(root, 'input', (event) => {
      if (event.target.id === 'q') read();
    });
    AMB.bind(root, 'change', (event) => {
      if (event.target.matches('select')) read();
    });
    AMB.bind(root, 'click', async (event) => {
      if (event.target.id === 'add-task') {
        openModal(null);
        return;
      }
      const button = event.target.closest('[data-action]');
      if (!button) return;
      const id = Number(button.dataset.id);
      const task = tasks.find((item) => item.id === id);
      if (button.dataset.action === 'edit' && task) {
        openModal(task);
        return;
      }
      try {
        if (button.dataset.action === 'delete') {
          if (!window.confirm('Delete this priority?')) return;
          await AMB.deleteTask(id);
          AMB.toast('Priority deleted.');
          await App.show('priorities', true);
          return;
        }
        if (button.dataset.action === 'toggle') {
          button.disabled = true;
          await AMB.toggleTask(id);
          await App.show('priorities', true);
        }
      } catch (err) {
        AMB.toast(err.message);
      }
    });
  }

  window.Priorities = { render };
})();
