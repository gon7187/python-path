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

function questionTemplate(question, number) {
  const head = `<div class="question-number">Задание ${number}</div><div class="question-prompt">${rich(question.prompt)}</div>`;
  let field = '';
  if (question.kind === 'choice') {
    field = `<div class="options">${question.options.map((option) => `<button type="button" class="option" data-choice-q="${question.id}" data-value="${esc(option)}">${esc(option)}</button>`).join('')}</div>`;
  } else if (question.kind === 'input') {
    field = `<input class="answer-input" data-answer-q="${question.id}" placeholder="${esc(question.placeholder || 'Введите ответ')}" autocomplete="off" />`;
  } else {
    field = `<textarea class="code-editor" data-answer-q="${question.id}" spellcheck="false">${esc(question.starter)}</textarea>
      <div class="code-actions"><button class="button blue" type="button" data-check-code="${question.id}">▷ Проверить код</button></div>
      <details class="hint"><summary>Нужна подсказка?</summary><p>${esc(question.hint)}</p></details>`;
  }
  return `<article class="question-card card" data-question="${question.id}">${head}${field}<div class="inline-result" id="result-${question.id}"></div></article>`;
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
        showInline(questionId, result.correct, result.message, result.checks);
      } catch (error) { showInline(questionId, false, error.message); }
      button.disabled = false;
      button.textContent = '▷ Проверить код';
    });
  });
}

function showInline(questionId, correct, message, checks = []) {
  const node = document.querySelector(`#result-${questionId}`);
  if (!node) return;
  const details = checks.length && !correct ? ` <small>(${checks.filter((item) => !item.passed).map((item) => `ожидалось ${esc(item.expected)}, получено ${esc(item.actual)}`).join('; ')})</small>` : '';
  node.className = `inline-result visible ${correct ? 'ok' : 'no'}`;
  node.innerHTML = `${correct ? '✓' : '↺'} ${esc(message)}${details}`;
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
  view.innerHTML = `<section>
    <a class="back-link" href="#/">← К маршруту</a>
    <div class="lesson-head"><div><p class="eyebrow">Урок ${lesson.order} · ${lesson.duration} минут</p><h1>${esc(lesson.title)}</h1><p class="lead">${esc(lesson.subtitle)}</p><p class="lesson-meta"><span>⚡ ${lesson.xp} XP</span><span>🧩 3 задания</span></p></div></div>
    <section>${lesson.theory.map((card) => `<article class="theory-card card"><h2>${esc(card.title)}</h2><p>${esc(card.text)}</p><pre class="code-example"><code>${esc(card.example)}</code></pre>${card.tip ? `<div class="tip">${esc(card.tip)}</div>` : ''}</article>`).join('')}</section>
    <h2 class="practice-title">Проверь себя</h2><p class="lead">Нужно минимум 2 правильных ответа, чтобы открыть следующий урок.</p>
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
      result.results.forEach((item) => showInline(item.question_id, item.correct, item.message, item.checks));
      await refreshDashboard();
      if (result.passed) toast(`+${result.xp_gained} XP — урок пройден!`);
    } catch (error) { toast(error.message); }
    button.disabled = false; button.innerHTML = 'Проверить урок <span>→</span>';
  });
}

async function renderPractice() {
  loading();
  const data = await api('/api/practice');
  const question = data.question;
  view.innerHTML = `<section class="practice-wrap"><a class="back-link" href="#/">← К маршруту</a><article class="practice-hero card"><p class="eyebrow">Тренировка</p><h1>${data.is_review ? 'Повторим слабое место' : 'Быстрая практика'}</h1><p class="lead">${data.is_review ? `Это задание из темы «${esc(data.lesson_title)}» стоит закрепить.` : `Небольшой повтор из темы «${esc(data.lesson_title)}».`}</p></article><form id="practice-form">${questionTemplate(question, 1)}<div class="submit-row"><button class="button" type="submit">Проверить <span>→</span></button><a class="button ghost" href="#/practice">Другое задание</a></div></form></section>`;
  const form = document.querySelector('#practice-form');
  bindQuestionControls(form);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const answer = getAnswers(form, [question])[0];
    try {
      const result = await api('/api/practice/submit', { method: 'POST', body: JSON.stringify(answer) });
      showInline(question.id, result.correct, result.message, result.checks);
      await refreshDashboard();
      if (result.correct) toast(`Верно! +${result.xp_gained} XP`);
    } catch (error) { toast(error.message); }
  });
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
      result.results.forEach((item) => showInline(item.question_id, item.correct, item.message, item.checks));
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
