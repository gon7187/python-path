const view = document.querySelector('#view');
let dashboard = null;
const MODULE_COLLAPSE_KEY = 'python-path-module-collapse';
const sandboxHistory = [];
const sandboxSamples = [
  { label: 'Вывод текста', code: "print('Привет, Python!')\n", inputs: [] },
  { label: 'Небольшой расчёт', code: 'price = 120\ncount = 3\nprint(price * count)\n', inputs: [] },
  { label: 'Ввод имени', code: "name = input('Имя: ')\nprint(f'Привет, {name}!')\n", inputs: ['Аня'] },
];

const esc = (value = '') => String(value)
  .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
const rich = (value = '') => esc(value).replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

function moduleCollapseStates() {
  try { return JSON.parse(localStorage.getItem(MODULE_COLLAPSE_KEY) || '{}'); }
  catch { return {}; }
}

function isModuleCollapsed(module) {
  if (module.completed !== module.total) return false;
  const states = moduleCollapseStates();
  return states[module.id] ?? true;
}

function saveModuleCollapsed(moduleId, collapsed) {
  const states = moduleCollapseStates();
  states[moduleId] = collapsed;
  localStorage.setItem(MODULE_COLLAPSE_KEY, JSON.stringify(states));
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || 'Сервис временно недоступен.');
  return payload;
}

function toast(message) {
  document.querySelector('.toast')?.remove();
  const node = document.createElement('div');
  node.className = 'toast';
  node.textContent = message;
  document.body.append(node);
  setTimeout(() => node.remove(), 3300);
}

async function refreshDashboard() {
  dashboard = await api('/api/dashboard');
  document.querySelector('#xp').textContent = dashboard.profile.xp;
  document.querySelector('#streak').textContent = dashboard.profile.streak;
  return dashboard;
}

function route() {
  return location.hash.slice(1) || '/';
}

function setActiveNavigation(current) {
  const active = current.startsWith('/sandbox') ? '/sandbox' : current.startsWith('/projects') ? '/projects' : current.startsWith('/practice') ? '/practice' : '/';
  document.querySelectorAll('[data-nav]').forEach((node) => node.classList.toggle('active', node.dataset.nav === active));
}

function loading() {
  view.innerHTML = '<div class="loading"><i></i><i></i><i></i> Загружаем путь…</div>';
}

function renderDashboard(data) {
  const next = data.next_lesson;
  const heroAction = next
    ? `<a class="button light" href="#/lesson/${next.id}">Продолжить <span>→</span></a>`
    : '<a class="button light" href="#/practice">Закрепить знания <span>→</span></a>';
  const moduleHtml = data.course.map(renderModule).join('');
  const badgeHtml = data.achievements.map((item) => `
    <div class="badge ${item.unlocked ? '' : 'locked'}">
      <span class="badge-icon">${item.icon}</span><strong>${esc(item.title)}</strong><small>${esc(item.description)}</small>
    </div>`).join('');
  view.innerHTML = `
    <section class="hero">
      <p class="eyebrow">Твой Python-тренажёр</p>
      <h1>${next ? `Следующий шаг: ${esc(next.title)}` : 'Ты прошёл весь путь!'}</h1>
      <p class="lead">${next ? 'Небольшие уроки, практика и честная обратная связь — чтобы Python действительно запоминался.' : 'Все разделы открыты. Продолжай практиковаться, чтобы знания стали автоматическими.'}</p>
      <div class="hero-actions">${heroAction}<span class="pill">${data.progress_percent}% курса</span></div>
    </section>
    <section class="stats-grid" aria-label="Статистика">
      <div class="stat-card"><span class="stat-icon">⚡</span><span class="stat-label">Всего опыта</span><div class="stat-number">${data.profile.xp} XP</div></div>
      <div class="stat-card"><span class="stat-icon">🔥</span><span class="stat-label">Текущая серия</span><div class="stat-number">${data.profile.streak} дн.</div></div>
      <div class="stat-card"><span class="stat-icon">📚</span><span class="stat-label">Уроков пройдено</span><div class="stat-number">${data.completed_lessons} / ${data.total_lessons}</div></div>
    </section>
    <div class="section-heading"><div><h2>Твой маршрут</h2><p>Каждый урок открывает следующий.</p></div><span class="pill" style="background:#eff3f8;color:#73809a">${data.completed_lessons}/${data.total_lessons}</span></div>
    ${moduleHtml}
    <div class="section-heading"><div><h2>Коллекция достижений</h2><p>Маленькие победы поддерживают ритм.</p></div></div>
    <section class="badges">${badgeHtml}</section>`;
  view.querySelectorAll('[data-module-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const module = button.closest('.module');
      const body = module.querySelector('[data-module-body]');
      const collapsed = !body.hidden;
      body.hidden = collapsed;
      button.setAttribute('aria-expanded', String(!collapsed));
      button.querySelector('.module-collapse').textContent = collapsed ? 'Развернуть ▾' : 'Свернуть ▴';
      saveModuleCollapsed(button.dataset.moduleToggle, collapsed);
    });
  });
}

function renderModule(module) {
  const lessons = module.lessons.map((item) => {
    const state = item.completed ? 'done' : item.unlocked ? 'current' : 'locked';
    const node = item.completed ? '✓' : item.unlocked ? '▶' : '🔒';
    const stars = item.completed ? `<span class="stars">${'★'.repeat(item.stars)}${'☆'.repeat(3 - item.stars)}</span>` : '';
    const content = `<span class="lesson-node">${node}</span><span class="lesson-info"><strong>${esc(item.title)}</strong><span>${esc(item.subtitle)} · ${item.duration} мин</span></span>${stars}<span class="lesson-xp">+${item.xp} XP</span>`;
    return item.unlocked
      ? `<div class="lesson-row ${state}"><a class="lesson-link" href="#/lesson/${item.id}">${content}</a></div>`
      : `<div class="lesson-row ${state}">${content}</div>`;
  }).join('');
  const exam = module.exam;
  const examMarkup = exam.available
    ? `<a class="button ${exam.passed ? 'ghost' : 'blue'}" href="#/exam/${module.id}">${exam.passed ? `Сдан: ${exam.score} б.` : 'Пройти'}</a>`
    : '<button class="button ghost" disabled>🔒 Закрыт</button>';
  const collapsed = isModuleCollapsed(module);
  const title = `<div><h2>${module.icon} ${esc(module.title)}</h2><p>${esc(module.description)}</p></div><span class="module-progress">${module.completed} из ${module.total}<br>уроков</span>`;
  const header = module.completed === module.total
    ? `<button class="module-title ${module.color} module-toggle" type="button" data-module-toggle="${module.id}" aria-expanded="${String(!collapsed)}">${title}<span class="module-collapse">${collapsed ? 'Развернуть ▾' : 'Свернуть ▴'}</span></button>`
    : `<div class="module-title ${module.color}">${title}</div>`;
  return `<section class="module card">
    ${header}
    <div data-module-body ${collapsed ? 'hidden' : ''}><div class="lesson-list">${lessons}</div>
    <div class="exam-row"><div><strong>🏆 ${module.id === 'realworld' ? 'Финальный экзамен' : 'Мини-экзамен раздела'}</strong><p>${exam.available ? 'Проверь раздел и получи +50 XP.' : 'Откроется после всех уроков раздела.'}</p></div>${examMarkup}</div></div>
  </section>`;
}

function questionTemplate(question, number, stageLabel = '') {
  const stages = {
    choice: 'Проверь понимание',
    input: 'Вспомни без вариантов',
    parsons: 'Собери и проследи код',
    code: ['spaced_retrieval', 'cumulative_transfer'].includes(question.purpose) ? 'Накопительное повторение' : 'Примени самостоятельно',
  };
  const label = stageLabel || stages[question.kind] || `Задание ${number}`;
  const badge = question.badge ? `<span class="question-badge">${esc(question.badge)}</span>` : '';
  const head = `<div class="question-number">${label}${badge}</div><div class="question-prompt">${rich(question.prompt)}</div>`;
  const guide = question.guide
    ? `<aside class="task-guide"><strong>🧭 Как подойти</strong><p>${rich(question.guide)}</p></aside>`
    : '';
  let field = '';
  if (question.kind === 'choice') {
    field = `<div class="options">${question.options.map((option) => `<button type="button" class="option" data-choice-q="${question.id}" data-value="${esc(option)}">${esc(option)}</button>`).join('')}</div>`;
  } else if (question.kind === 'input') {
    field = `<input class="answer-input" data-answer-q="${question.id}" placeholder="${esc(question.placeholder || 'Введите ответ')}" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" />`;
  } else if (question.kind === 'parsons') {
    field = `<div class="parsons-help">Перемещай строки стрелками. На телефоне это надёжнее перетаскивания.</div><div class="parsons-list" data-parsons-q="${question.id}">${question.blocks.map((block, index) => `<div class="parsons-block" data-parsons-block="${esc(block.id)}"><span class="parsons-grip">${index + 1}</span><pre>${esc(block.text || ' ')}</pre><div class="parsons-actions"><button type="button" aria-label="Поднять строку" data-parsons-move="up">↑</button><button type="button" aria-label="Опустить строку" data-parsons-move="down">↓</button></div></div>`).join('')}</div>`;
  } else {
    const exampleInputs = (question.input_example || []).join('\n');
    field = `<textarea class="code-editor" data-answer-q="${question.id}" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false">${esc(question.starter)}</textarea>
      <details class="code-input-panel" ${exampleInputs ? 'open' : ''}><summary>⌨️ Данные для input() <small>необязательно</small></summary><p>Одна строка — один ответ. Они подставятся по порядку при запуске.</p><textarea class="code-stdin" data-input-q="${question.id}" placeholder="Например: Аня" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false">${esc(exampleInputs)}</textarea></details>
      <div class="code-actions"><button class="button ghost" type="button" data-run-code="${question.id}">▷ Запустить</button><button class="button blue" type="button" data-check-code="${question.id}">✓ Проверить по заданию</button><a class="button ghost sandbox-link" href="#/sandbox">⌨️ Песочница</a></div>
      <div class="progressive-hints">${(question.hints || [question.hint]).filter(Boolean).map((hint, index) => `<details class="hint"><summary>Подсказка ${index + 1}${index === 0 ? ' · направление' : index === 1 ? ' · план' : ' · почти решение'}</summary><p>${esc(hint)}</p></details>`).join('')}</div>`;
  }
  return `<article class="question-card card" data-question="${question.id}">${head}${guide}${field}<div class="inline-result" id="result-${question.id}"></div></article>`;
}

function getAnswers(scope, questions) {
  return questions.map((question) => {
    let answer = '';
    if (question.kind === 'choice') answer = scope.querySelector(`[data-choice-q="${question.id}"].selected`)?.dataset.value || '';
    else if (question.kind === 'parsons') answer = JSON.stringify([...scope.querySelectorAll(`[data-parsons-q="${question.id}"] [data-parsons-block]`)].map((item) => item.dataset.parsonsBlock));
    else answer = scope.querySelector(`[data-answer-q="${question.id}"]`)?.value || '';
    return { question_id: question.id, answer };
  });
}

function bindQuestionControls(scope) {
  scope.querySelectorAll('[data-choice-q]').forEach((button) => {
    button.addEventListener('click', () => {
      const id = button.dataset.choiceQ;
      scope.querySelectorAll(`[data-choice-q="${id}"]`).forEach((item) => item.classList.remove('selected'));
      button.classList.add('selected');
    });
  });
  scope.querySelectorAll('[data-check-code]').forEach((button) => {
    button.addEventListener('click', async () => {
      const questionId = button.dataset.checkCode;
      const editor = scope.querySelector(`[data-answer-q="${questionId}"]`);
      button.disabled = true;
      button.textContent = 'Проверяем…';
      try {
        const result = await api('/api/code/check', { method: 'POST', body: JSON.stringify({ question_id: questionId, answer: editor.value }) });
        showInline(questionId, result.correct, result.message, result.checks, result.output);
      } catch (error) { showInline(questionId, false, error.message); }
      button.disabled = false;
      button.textContent = '✓ Проверить по заданию';
    });
  });
  scope.querySelectorAll('[data-parsons-move]').forEach((button) => {
    button.addEventListener('click', () => {
      const block = button.closest('[data-parsons-block]');
      if (button.dataset.parsonsMove === 'up' && block.previousElementSibling) {
        block.parentElement.insertBefore(block, block.previousElementSibling);
      } else if (button.dataset.parsonsMove === 'down' && block.nextElementSibling) {
        block.parentElement.insertBefore(block.nextElementSibling, block);
      }
      [...block.parentElement.children].forEach((item, index) => { item.querySelector('.parsons-grip').textContent = index + 1; });
    });
  });
  scope.querySelectorAll('[data-run-code]').forEach((button) => {
    button.addEventListener('click', async () => {
      const questionId = button.dataset.runCode;
      const editor = scope.querySelector(`[data-answer-q="${questionId}"]`);
      button.disabled = true;
      button.textContent = 'Запускаем…';
      try {
        const result = await api('/api/code/run', { method: 'POST', body: JSON.stringify({ question_id: questionId, answer: editor.value, inputs: getCodeInputs(scope, questionId) }) });
        showInline(questionId, result.correct, result.message, result.checks, result.output);
      } catch (error) { showInline(questionId, false, error.message); }
      button.disabled = false;
      button.textContent = '▷ Запустить';
    });
  });
}

function showInline(questionId, correct, message, checks = [], output = null) {
  const node = document.querySelector(`#result-${questionId}`);
  if (!node) return;
  const details = checks.length && !correct ? ` <small>(${checks.filter((item) => !item.passed).map((item) => `ожидалось ${esc(item.expected)}, получено ${esc(item.actual)}`).join('; ')})</small>` : '';
  const consoleOutput = output === null ? '' : `<pre class="code-output">${esc(output || '— программа ничего не вывела —')}</pre>`;
  node.className = `inline-result visible ${correct ? 'ok' : 'no'}`;
  node.innerHTML = `${correct ? '✓' : '↺'} ${esc(message)}${details}${consoleOutput}`;
}

function executionPanel(executions, title = 'Код в действии') {
  if (!executions.length) return '';
  const cards = executions.map((item) => `<article class="execution-card"><strong>${item.correct ? '✓ Результат прошёл проверку' : '🖥️ Результат этого запуска'}</strong>${item.source ? `<pre class="execution-source">${esc(item.source)}</pre>` : ''}${item.checks?.length ? `<div class="execution-checks">${item.checks.map((check) => `<p><b>${check.passed ? '✓' : '↺'}</b> ожидалось <code>${esc(check.expected)}</code>, получилось <code>${esc(check.actual)}</code></p>`).join('')}</div>` : ''}<span>Вывод в консоли</span><pre class="code-output">${esc(item.output || '— программа ничего не вывела —')}</pre></article>`).join('');
  return `<section class="execution-panel card"><h2>🖥️ ${title}</h2><p>Смотри на вывод: так Python прошёл код строка за строкой.</p>${cards}</section>`;
}

function submissionResult(result, retryText = 'Попробовать ещё раз', answers = []) {
  const items = result.results.map((item) => `<div class="result-item ${item.correct ? 'ok' : 'no'}"><b>${item.correct ? '✓ Верно' : '↺ Повтори'}</b> ${esc(item.explanation || item.message || '')}</div>`).join('');
  const answerById = Object.fromEntries(answers.map((item) => [item.question_id, item.answer]));
  const executions = result.results.filter((item) => Object.prototype.hasOwnProperty.call(item, 'output')).map((item) => ({ correct: item.correct, output: item.output, source: answerById[item.question_id] || '', checks: item.checks || [] }));
  const action = result.passed
    ? '<a class="button blue" href="#/">К маршруту</a>'
    : `<button class="button" type="button" onclick="location.reload()">${retryText}</button>`;
  return `<section class="result-panel ${result.passed ? '' : 'fail'}" id="submission-result"><h2>${result.passed ? 'Отличная работа! 🎉' : 'Ещё один подход — и получится'}</h2><p>${esc(result.message)}${result.xp_gained ? ` +${result.xp_gained} XP.` : ''}</p><div class="result-list">${items}</div><div class="code-actions">${action}</div></section>${executionPanel(executions)}`;
}

async function renderLesson(id) {
  loading();
  const lesson = await api(`/api/lessons/${id}`);
  const theoryCards = lesson.theory.map((card, index) => `<article class="theory-card card">
    <p class="theory-step">Шаг ${index + 1} из ${lesson.theory.length}</p><h2>${esc(card.title)}</h2><p>${esc(card.text)}</p>
    <p class="example-label">${card.language && card.language !== 'python' ? `Разберём формат · ${esc(card.language)}` : 'Разберём пример'}</p><pre class="code-example"><code>${esc(card.example)}</code></pre>${card.output !== undefined ? `<div class="example-output"><strong>Что увидим после запуска</strong><pre class="code-output">${esc(card.output || '— программа ничего не вывела —')}</pre></div>` : ''}${card.tip ? `<div class="tip">${esc(card.tip)}</div>` : ''}
  </article>`).join('');
  view.innerHTML = `<section>
    <a class="back-link" href="#/">← К маршруту</a>
    <div class="lesson-head"><div><p class="eyebrow">Урок ${lesson.order} · ${lesson.duration} минут</p><h1>${esc(lesson.title)}</h1><p class="lead">${esc(lesson.subtitle)}</p><p class="lesson-meta"><span>⚡ ${lesson.xp} XP</span><span>🧩 ${lesson.questions.length} задания</span></p></div></div>
    <aside class="learning-roadmap"><strong>Без спешки</strong><span>1. Прочитай объяснение</span><span>2. Разбери пример</span><span>3. Выполни шаги в задаче</span><p>Не надо держать всё в голове: примеры и подсказки можно открывать во время решения.</p></aside>
    <section>${theoryCards}</section>
    <h2 class="practice-title">От опоры к самостоятельности</h2><p class="lead">У каждой задачи есть план. Код можно запускать сколько угодно раз. Для прохождения нужно решить обязательные практические этапы — одних вариантов ответа недостаточно.</p>
    <form id="lesson-form">${lesson.questions.map((question, index) => questionTemplate(question, index + 1)).join('')}<div class="submit-row"><button class="button" type="submit">Проверить урок <span>→</span></button><span class="submit-note">Проверяй код отдельно, прежде чем сдавать.</span></div></form>
  </section>`;
  const form = document.querySelector('#lesson-form');
  bindQuestionControls(form);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('[type="submit"]');
    button.disabled = true; button.textContent = 'Проверяем…';
    try {
      const answers = getAnswers(form, lesson.questions);
      const result = await api(`/api/lessons/${id}/submit`, { method: 'POST', body: JSON.stringify({ answers }) });
      document.querySelector('#submission-result')?.remove();
      form.nextElementSibling?.classList?.contains('execution-panel') && form.nextElementSibling.remove();
      form.insertAdjacentHTML('afterend', submissionResult(result, 'Попробовать ещё раз', answers));
      result.results.forEach((item) => showInline(item.question_id, item.correct, item.message, item.checks, item.output));
      await refreshDashboard();
      if (result.passed) toast(`+${result.xp_gained} XP — урок пройден!`);
    } catch (error) { toast(error.message); }
    button.disabled = false; button.innerHTML = 'Проверить урок <span>→</span>';
  });
}

async function renderPractice(mode = 'guided', moduleId = '') {
  loading();
  const params = new URLSearchParams({ mode });
  if (moduleId) params.set('module_id', moduleId);
  const session = await api(`/api/practice/session?${params}`);
  let index = 0;
  let correctCount = 0;
  const executions = [];

  const modeButton = (id, label, caption) => `<button class="practice-mode ${session.mode === id ? 'active' : ''}" type="button" data-practice-mode="${id}"><strong>${label}</strong><small>${caption}</small></button>`;
  const moduleOptions = session.available_modules.map((module) => `<option value="${esc(module.id)}" ${moduleId === module.id ? 'selected' : ''}>${esc(module.icon)} ${esc(module.title)}</option>`).join('');
  view.innerHTML = `<section class="practice-wrap"><a class="back-link" href="#/">← К маршруту</a>
    <article class="practice-hero card"><p class="eyebrow">Практика без прыжков</p><h1>${esc(session.title)}</h1><p class="lead">${esc(session.description)}</p>
      <div class="practice-modes">
        ${modeButton('guided', '🌱 Последняя тема', 'От воспоминания к самостоятельному коду')}
        ${modeButton('review', '🎯 Ошибки', session.weak_count ? `${session.weak_count} слабых мест` : 'Пока ошибок нет')}
        ${modeButton('mixed', '🧩 Смешанная', 'Повтор уже открытых тем')}
      </div>
      <label class="practice-select"><span>Или выбери тему</span><select id="practice-module"><option value="">Выбрать открытую тему</option>${moduleOptions}</select></label>
    </article>
    <aside class="practice-brief"><strong>🧠 Перед началом</strong><p>${esc(session.tip)}</p></aside>
    <div id="practice-session"></div>
  </section>`;

  document.querySelectorAll('[data-practice-mode]').forEach((button) => {
    button.addEventListener('click', () => renderPractice(button.dataset.practiceMode));
  });
  document.querySelector('#practice-module').addEventListener('change', (event) => {
    const selected = event.target.value;
    if (selected) renderPractice('module', selected);
  });

  const sessionNode = document.querySelector('#practice-session');
  const renderSummary = () => {
    const total = session.questions.length;
    const message = correctCount === total
      ? 'Отличная серия: все задания решены. Можно переходить к следующему шагу.'
      : `Верно ${correctCount} из ${total}. Ошибки уже добавлены в режим «Ошибки» — вернись к ним после небольшой паузы.`;
    sessionNode.innerHTML = `<section class="practice-summary card"><span class="practice-summary-icon">${correctCount === total ? '🏆' : '🔁'}</span><h2>Серия завершена</h2><p>${esc(message)}</p><div class="code-actions"><button class="button" type="button" data-practice-again>Ещё серия <span>→</span></button><a class="button ghost" href="#/">К маршруту</a></div></section>${executionPanel(executions, 'Код в действии: практика')}`;
    sessionNode.querySelector('[data-practice-again]').addEventListener('click', () => renderPractice(mode, moduleId));
  };

  const renderStep = () => {
    const question = session.questions[index];
    const total = session.questions.length;
    const percent = Math.round((index / total) * 100);
    sessionNode.innerHTML = `<section class="practice-progress" aria-label="Прогресс серии"><div><strong>Серия: ${index + 1} из ${total}</strong><span>Тема: ${esc(question.lesson_title)}</span></div><div class="practice-progress-track"><i style="width:${percent}%"></i></div></section>
      <form id="practice-form">${questionTemplate(question, index + 1, `Шаг серии ${index + 1}`)}<div class="submit-row"><button class="button" type="submit">Проверить <span>→</span></button><span class="submit-note">Сначала прочитай план — он не уменьшает ценность ответа.</span></div></form>`;
    const form = document.querySelector('#practice-form');
    bindQuestionControls(form);
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const button = form.querySelector('[type="submit"]');
      button.disabled = true;
      try {
        const answer = getAnswers(form, [question])[0];
        const result = await api('/api/practice/submit', { method: 'POST', body: JSON.stringify(answer) });
        if (question.kind === 'code') executions.push({ correct: result.correct, output: result.output, source: answer.answer, checks: result.checks || [] });
        if (result.correct) correctCount += 1;
        showInline(question.id, result.correct, result.message, result.checks, result.output);
        await refreshDashboard();
        if (result.correct) toast(`Верно! +${result.xp_gained} XP`);
        const isLast = index + 1 === total;
        form.querySelector('.submit-row').innerHTML = `<button class="button ${isLast ? 'blue' : ''}" type="button" data-practice-next>${isLast ? 'Завершить серию' : 'Следующее задание'} <span>→</span></button>`;
        form.querySelector('[data-practice-next]').addEventListener('click', () => {
          index += 1;
          if (index >= total) renderSummary();
          else renderStep();
        });
      } catch (error) {
        toast(error.message);
        button.disabled = false;
      }
    });
  };

  renderStep();
}

function renderSandboxHistory() {
  const node = document.querySelector('#sandbox-history');
  if (!node) return;
  if (!sandboxHistory.length) {
    node.innerHTML = '<p class="sandbox-empty">Запуски появятся здесь. Не бойся менять код и запускать снова.</p>';
    return;
  }
  node.innerHTML = sandboxHistory.map((item, index) => `<article class="sandbox-run ${item.correct ? '' : 'failed'}"><div><strong>Запуск ${sandboxHistory.length - index}</strong><span>${item.correct ? 'Код выполнился' : esc(item.message)}</span></div><pre class="execution-source">${esc(item.source)}</pre><span>Консоль</span><pre class="code-output">${esc(item.output || '— программа ничего не вывела —')}</pre></article>`).join('');
}

function renderSandbox() {
  const sample = sandboxSamples[2];
  view.innerHTML = `<section class="sandbox-wrap"><a class="back-link" href="#/">← К маршруту</a><article class="sandbox-hero card"><p class="eyebrow">Свободная практика</p><h1>Песочница Python</h1><p class="lead">Пиши обычный код, меняй его и запускай сколько угодно раз. Здесь нет оценки и нет единственного правильного ответа — есть код, консоль и эксперимент.</p></article><aside class="learning-roadmap"><strong>Рабочий цикл</strong><span>1. Напиши идею</span><span>2. Запусти код</span><span>3. Прочитай вывод</span><p>Можно использовать базовые функции Python, условия, циклы, функции и input(). Импорты, файлы и системные команды остаются закрыты для безопасности.</p></aside><section class="sandbox-card card"><div class="sandbox-toolbar"><strong>Быстрый старт</strong><div>${sandboxSamples.map((item, index) => `<button class="sandbox-sample" type="button" data-sandbox-sample="${index}">${esc(item.label)}</button>`).join('')}</div></div><textarea id="sandbox-code" class="code-editor sandbox-editor" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false">${esc(sample.code)}</textarea><details class="code-input-panel" open><summary>⌨️ Данные для input() <small>необязательно</small></summary><p>Одна строка — один ответ. Если код вызывает input() дважды, напиши два ответа в разных строках.</p><textarea id="sandbox-input" class="code-stdin" placeholder="Например: Аня" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false">${esc(sample.inputs.join('\n'))}</textarea></details><div class="code-actions"><button class="button blue" type="button" id="sandbox-run">▷ Запустить код</button><button class="button ghost" type="button" id="sandbox-reset">↺ Очистить</button></div></section><section class="sandbox-console card"><div class="sandbox-console-head"><div><p class="eyebrow">История</p><h2>Консоль запусков</h2></div><span>Каждый запуск сохраняется, пока открыта страница</span></div><div id="sandbox-history"></div></section></section>`;
  const code = document.querySelector('#sandbox-code');
  const input = document.querySelector('#sandbox-input');
  const runButton = document.querySelector('#sandbox-run');
  document.querySelectorAll('[data-sandbox-sample]').forEach((button) => {
    button.addEventListener('click', () => {
      const selected = sandboxSamples[Number(button.dataset.sandboxSample)];
      code.value = selected.code;
      input.value = selected.inputs.join('\n');
      code.focus();
    });
  });
  document.querySelector('#sandbox-reset').addEventListener('click', () => {
    code.value = '# Здесь можно писать и запускать любой учебный код\n';
    input.value = '';
    sandboxHistory.length = 0;
    renderSandboxHistory();
    code.focus();
  });
  runButton.addEventListener('click', async () => {
    runButton.disabled = true;
    runButton.textContent = 'Запускаем…';
    try {
      const result = await api('/api/sandbox/run', { method: 'POST', body: JSON.stringify({ answer: code.value, inputs: input.value ? input.value.replaceAll('\r\n', '\n').split('\n') : [] }) });
      sandboxHistory.unshift({ source: code.value, output: result.output, correct: result.correct, message: result.message });
      renderSandboxHistory();
    } catch (error) {
      sandboxHistory.unshift({ source: code.value, output: '', correct: false, message: error.message });
      renderSandboxHistory();
    }
    runButton.disabled = false;
    runButton.textContent = '▷ Запустить код';
  });
  renderSandboxHistory();
}

async function renderProjects() {
  loading();
  const data = await api('/api/projects');
  const cards = data.projects.map((project) => {
    const state = project.completed ? 'done' : project.unlocked ? 'open' : 'locked';
    const action = project.unlocked
      ? `<a class="button ${project.completed ? 'ghost' : 'blue'}" href="#/projects/${project.id}">${project.completed ? 'Открыть снова' : 'Начать проект'} <span>→</span></a>`
      : `<span class="project-lock">🔒 Сначала: ${esc(project.missing_prerequisites.join(', ') || 'предыдущий проект')}</span>`;
    return `<article class="project-card card ${state}"><div class="project-icon">${project.icon}</div><div class="project-info"><p class="eyebrow">Проект ${project.order} · ${esc(project.level)}</p><h2>${esc(project.title)}</h2><p>${esc(project.subtitle)}</p><div class="project-skills">${project.skills.map((skill) => `<span>${esc(skill)}</span>`).join('')}</div></div><div class="project-action">${action}<small>⚡ ${project.xp} XP</small></div></article>`;
  }).join('');
  view.innerHTML = `<section class="projects-wrap"><a class="back-link" href="#/">← К маршруту</a><article class="projects-hero card"><p class="eyebrow">Мастерская</p><h1>Проекты: от идеи к инструменту</h1><p class="lead">Здесь ты собираешь маленькие работающие программы. Проект открывается только после конкретных нужных навыков, а не по случайному числу уроков.</p></article><aside class="practice-brief"><strong>🧰 Как проходить проект</strong><p>Сначала запусти заготовку, затем меняй одну часть за раз. Итоговая проверка запускает несколько входных сценариев, поэтому программа должна действительно работать с данными.</p></aside><section class="project-list">${cards}</section></section>`;
}

async function renderProject(id) {
  loading();
  const project = await api(`/api/projects/${id}`);
  const domId = `project-${project.id}`;
  const exampleInputs = (project.input_example || []).join('\n');
  view.innerHTML = `<section class="project-workspace"><a class="back-link" href="#/projects">← Ко всем проектам</a><article class="project-hero card"><div class="project-icon">${project.icon}</div><div><p class="eyebrow">Проект ${project.order} · ${esc(project.level)} · ⚡ ${project.xp} XP</p><h1>${esc(project.title)}</h1><p class="lead">${esc(project.description)}</p></div></article><section class="project-plan card"><div><h2>Что соберём</h2><ul>${project.checklist.map((item) => `<li>${esc(item)}</li>`).join('')}</ul></div><div><h2>Инструменты</h2><div class="project-skills">${project.skills.map((skill) => `<span>${esc(skill)}</span>`).join('')}</div></div></section><aside class="learning-roadmap"><strong>Без спешки</strong><span>1. Запусти заготовку</span><span>2. Измени один шаг</span><span>3. Проверь проект</span><p>Подсказки можно открывать в любой момент. Консоль ниже показывает, что действительно произошло.</p></aside><section class="project-editor card"><p class="eyebrow">Редактор проекта</p><textarea class="code-editor" data-answer-q="${domId}" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false">${esc(project.starter)}</textarea><details class="code-input-panel" ${exampleInputs ? 'open' : ''}><summary>⌨️ Данные для input() <small>необязательно</small></summary><p>Одна строка — один ответ. Меняй их и нажимай «Запустить», чтобы увидеть другой сценарий.</p><textarea class="code-stdin" data-input-q="${domId}" placeholder="Данные для запуска" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false">${esc(exampleInputs)}</textarea></details><div class="code-actions"><button class="button ghost" type="button" data-project-run>▷ Запустить</button><button class="button blue" type="button" data-project-submit>✓ Проверить проект</button></div><div class="project-hints">${project.hints.map((hint, index) => `<details class="hint"><summary>Подсказка ${index + 1}</summary><p>${esc(hint)}</p></details>`).join('')}</div><div class="inline-result" id="result-${domId}"></div></section></section>`;
  const editor = view.querySelector(`[data-answer-q="${domId}"]`);
  const runButton = view.querySelector('[data-project-run]');
  const submitButton = view.querySelector('[data-project-submit]');
  runButton.addEventListener('click', async () => {
    runButton.disabled = true; runButton.textContent = 'Запускаем…';
    try {
      const result = await api(`/api/projects/${id}/run`, { method: 'POST', body: JSON.stringify({ answer: editor.value, inputs: getCodeInputs(view, domId) }) });
      showInline(domId, result.correct, result.message, result.checks, result.output);
    } catch (error) { showInline(domId, false, error.message); }
    runButton.disabled = false; runButton.textContent = '▷ Запустить';
  });
  submitButton.addEventListener('click', async () => {
    submitButton.disabled = true; submitButton.textContent = 'Проверяем…';
    try {
      const result = await api(`/api/projects/${id}/submit`, { method: 'POST', body: JSON.stringify({ answer: editor.value }) });
      showInline(domId, result.correct, result.message, result.checks, result.output);
      if (result.correct) {
        await refreshDashboard();
        toast(result.xp_gained ? `Проект завершён! +${result.xp_gained} XP` : 'Проект уже был завершён — можно улучшать решение.');
      }
    } catch (error) { showInline(domId, false, error.message); }
    submitButton.disabled = false; submitButton.textContent = '✓ Проверить проект';
  });
}

function getCodeInputs(scope, questionId) {
  const value = scope.querySelector(`[data-input-q="${questionId}"]`)?.value || '';
  return value ? value.replaceAll('\r\n', '\n').split('\n') : [];
}

async function renderExam(moduleId) {
  loading();
  const exam = await api(`/api/exams/${moduleId}`);
  view.innerHTML = `<section class="exam-wrap"><a class="back-link" href="#/">← К маршруту</a><article class="exam-hero card"><p class="eyebrow">Контрольная точка</p><h1>${esc(exam.title)}</h1><p class="lead">${esc(exam.description)} Для зачёта нужно 70% и обязательные практические задания. Одними вариантами ответа экзамен не сдать. Награда — 50 XP.</p></article><form id="exam-form">${exam.questions.map((question, index) => questionTemplate(question, index + 1)).join('')}<div class="submit-row"><button class="button blue" type="submit">Сдать экзамен <span>🏁</span></button></div></form></section>`;
  const form = document.querySelector('#exam-form');
  bindQuestionControls(form);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('[type="submit"]'); button.disabled = true;
    try {
      const answers = getAnswers(form, exam.questions);
      const result = await api(`/api/exams/${moduleId}/submit`, { method: 'POST', body: JSON.stringify({ answers }) });
      document.querySelector('#submission-result')?.remove();
      form.nextElementSibling?.classList?.contains('execution-panel') && form.nextElementSibling.remove();
      form.insertAdjacentHTML('afterend', submissionResult(result, 'Пересдать экзамен', answers));
      result.results.forEach((item) => showInline(item.question_id, item.correct, item.message, item.checks, item.output));
      await refreshDashboard();
      if (result.passed) toast(`Экзамен сдан! +${result.xp_gained} XP`);
    } catch (error) { toast(error.message); }
    button.disabled = false;
  });
}

async function render() {
  const current = route();
  setActiveNavigation(current);
  try {
    if (current === '/') { loading(); renderDashboard(await refreshDashboard()); }
    else if (current === '/practice') await renderPractice();
    else if (current === '/sandbox') renderSandbox();
    else if (current === '/projects') await renderProjects();
    else if (current.startsWith('/projects/')) await renderProject(current.split('/')[2]);
    else if (current.startsWith('/lesson/')) await renderLesson(current.split('/')[2]);
    else if (current.startsWith('/exam/')) await renderExam(current.split('/')[2]);
    else { location.hash = '#/'; }
  } catch (error) {
    view.innerHTML = `<section class="empty"><div class="empty-icon">🧭</div><h1>Сюда пока не пройти</h1><p>${esc(error.message)}</p><a class="button" href="#/">Вернуться к маршруту</a></section>`;
  }
}

document.querySelector('#reset-button').addEventListener('click', async () => {
  if (!confirm('Сбросить весь прогресс? Это действие нельзя отменить.')) return;
  await api('/api/reset', { method: 'POST' });
  toast('Прогресс сброшен. Начинаем с чистого листа!');
  location.hash = '#/';
  render();
});
window.addEventListener('hashchange', render);
render();
