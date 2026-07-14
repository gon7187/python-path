const view = document.querySelector('#view');
let dashboard = null;

const esc = (value = '') => String(value)
  .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
const rich = (value = '') => esc(value).replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

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
  const active = current.startsWith('/practice') ? '/practice' : '/';
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
  return `<section class="module card">
    <div class="module-title ${module.color}"><div><h2>${module.icon} ${esc(module.title)}</h2><p>${esc(module.description)}</p></div><span class="module-progress">${module.completed} из ${module.total}<br>уроков</span></div>
    <div class="lesson-list">${lessons}</div>
    <div class="exam-row"><div><strong>🏆 ${module.id === 'realworld' ? 'Финальный экзамен' : 'Мини-экзамен раздела'}</strong><p>${exam.available ? 'Проверь раздел и получи +50 XP.' : 'Откроется после всех уроков раздела.'}</p></div>${examMarkup}</div>
  </section>`;
}

function questionTemplate(question, number, stageLabel = '') {
  const stages = ['Разминка: узнай идею', 'Повтори с опорой', 'Сделай сам, но по плану'];
  const label = stageLabel || stages[number - 1] || `Задание ${number}`;
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
  } else {
    const exampleInputs = (question.input_example || []).join('\n');
    field = `<textarea class="code-editor" data-answer-q="${question.id}" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false">${esc(question.starter)}</textarea>
      <details class="code-input-panel" ${exampleInputs ? 'open' : ''}><summary>⌨️ Данные для input() <small>необязательно</small></summary><p>Одна строка — один ответ. Они подставятся по порядку при запуске.</p><textarea class="code-stdin" data-input-q="${question.id}" placeholder="Например: Аня" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false">${esc(exampleInputs)}</textarea></details>
      <div class="code-actions"><button class="button ghost" type="button" data-run-code="${question.id}">▷ Запустить</button><button class="button blue" type="button" data-check-code="${question.id}">✓ Проверить по заданию</button></div>
      <details class="hint"><summary>Нужна подсказка?</summary><p>${esc(question.hint)}</p></details>`;
  }
  return `<article class="question-card card" data-question="${question.id}">${head}${guide}${field}<div class="inline-result" id="result-${question.id}"></div></article>`;
}

function getAnswers(scope, questions) {
  return questions.map((question) => {
    let answer = '';
    if (question.kind === 'choice') answer = scope.querySelector(`[data-choice-q="${question.id}"].selected`)?.dataset.value || '';
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

function submissionResult(result, retryText = 'Попробовать ещё раз') {
  const items = result.results.map((item) => `<div class="result-item ${item.correct ? 'ok' : 'no'}"><b>${item.correct ? '✓ Верно' : '↺ Повтори'}</b> ${esc(item.explanation || item.message || '')}</div>`).join('');
  const action = result.passed
    ? '<a class="button blue" href="#/">К маршруту</a>'
    : `<button class="button" type="button" onclick="location.reload()">${retryText}</button>`;
  return `<section class="result-panel ${result.passed ? '' : 'fail'}" id="submission-result"><h2>${result.passed ? 'Отличная работа! 🎉' : 'Ещё один подход — и получится'}</h2><p>${esc(result.message)}${result.xp_gained ? ` +${result.xp_gained} XP.` : ''}</p><div class="result-list">${items}</div><div class="code-actions">${action}</div></section>`;
}

async function renderLesson(id) {
  loading();
  const lesson = await api(`/api/lessons/${id}`);
  const theoryCards = lesson.theory.map((card, index) => `<article class="theory-card card">
    <p class="theory-step">Шаг ${index + 1} из ${lesson.theory.length}</p><h2>${esc(card.title)}</h2><p>${esc(card.text)}</p>
    <p class="example-label">Разберём пример</p><pre class="code-example"><code>${esc(card.example)}</code></pre>${card.tip ? `<div class="tip">${esc(card.tip)}</div>` : ''}
  </article>`).join('');
  view.innerHTML = `<section>
    <a class="back-link" href="#/">← К маршруту</a>
    <div class="lesson-head"><div><p class="eyebrow">Урок ${lesson.order} · ${lesson.duration} минут</p><h1>${esc(lesson.title)}</h1><p class="lead">${esc(lesson.subtitle)}</p><p class="lesson-meta"><span>⚡ ${lesson.xp} XP</span><span>🧩 ${lesson.questions.length} задания</span></p></div></div>
    <aside class="learning-roadmap"><strong>Без спешки</strong><span>1. Прочитай объяснение</span><span>2. Разбери пример</span><span>3. Выполни шаги в задаче</span><p>Не надо держать всё в голове: примеры и подсказки можно открывать во время решения.</p></aside>
    <section>${theoryCards}</section>
    <h2 class="practice-title">Сделаем вместе</h2><p class="lead">У каждой задачи есть план. Код можно проверять сколько угодно раз; для прохождения достаточно 2 правильных ответов.</p>
    <form id="lesson-form">${lesson.questions.map(questionTemplate).join('')}<div class="submit-row"><button class="button" type="submit">Проверить урок <span>→</span></button><span class="submit-note">Проверяй код отдельно, прежде чем сдавать.</span></div></form>
  </section>`;
  const form = document.querySelector('#lesson-form');
  bindQuestionControls(form);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('[type="submit"]');
    button.disabled = true; button.textContent = 'Проверяем…';
    try {
      const result = await api(`/api/lessons/${id}/submit`, { method: 'POST', body: JSON.stringify({ answers: getAnswers(form, lesson.questions) }) });
      document.querySelector('#submission-result')?.remove();
      form.insertAdjacentHTML('afterend', submissionResult(result));
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

  const modeButton = (id, label, caption) => `<button class="practice-mode ${session.mode === id ? 'active' : ''}" type="button" data-practice-mode="${id}"><strong>${label}</strong><small>${caption}</small></button>`;
  const moduleOptions = session.available_modules.map((module) => `<option value="${esc(module.id)}" ${moduleId === module.id ? 'selected' : ''}>${esc(module.icon)} ${esc(module.title)}</option>`).join('');
  view.innerHTML = `<section class="practice-wrap"><a class="back-link" href="#/">← К маршруту</a>
    <article class="practice-hero card"><p class="eyebrow">Практика без прыжков</p><h1>${esc(session.title)}</h1><p class="lead">${esc(session.description)}</p>
      <div class="practice-modes">
        ${modeButton('guided', '🌱 Текущий шаг', 'Одна тема, три понятных шага')}
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
    sessionNode.innerHTML = `<section class="practice-summary card"><span class="practice-summary-icon">${correctCount === total ? '🏆' : '🔁'}</span><h2>Серия завершена</h2><p>${esc(message)}</p><div class="code-actions"><button class="button" type="button" data-practice-again>Ещё серия <span>→</span></button><a class="button ghost" href="#/">К маршруту</a></div></section>`;
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

function getCodeInputs(scope, questionId) {
  const value = scope.querySelector(`[data-input-q="${questionId}"]`)?.value || '';
  return value ? value.replaceAll('\r\n', '\n').split('\n') : [];
}

async function renderExam(moduleId) {
  loading();
  const exam = await api(`/api/exams/${moduleId}`);
  view.innerHTML = `<section class="exam-wrap"><a class="back-link" href="#/">← К маршруту</a><article class="exam-hero card"><p class="eyebrow">Контрольная точка</p><h1>${esc(exam.title)}</h1><p class="lead">${esc(exam.description)} Для зачёта нужно 70% правильных ответов. Награда — 50 XP.</p></article><form id="exam-form">${exam.questions.map(questionTemplate).join('')}<div class="submit-row"><button class="button blue" type="submit">Сдать экзамен <span>🏁</span></button></div></form></section>`;
  const form = document.querySelector('#exam-form');
  bindQuestionControls(form);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('[type="submit"]'); button.disabled = true;
    try {
      const result = await api(`/api/exams/${moduleId}/submit`, { method: 'POST', body: JSON.stringify({ answers: getAnswers(form, exam.questions) }) });
      document.querySelector('#submission-result')?.remove();
      form.insertAdjacentHTML('afterend', submissionResult(result, 'Пересдать экзамен'));
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
