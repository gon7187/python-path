const view = document.querySelector('#view');
let dashboard = null;
let lessonState = null;

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

function questionTemplate(question, number, options = {}) {
  const lessonMode = Boolean(options.lessonId);
  const head = `<div class="question-number">Задание ${number}</div><div class="question-prompt">${rich(question.prompt)}</div>`;
  let field = '';
  if (question.kind === 'choice') {
    field = `<div class="options">${question.options.map((option) => `<button type="button" class="option" data-choice-q="${question.id}" data-value="${esc(option)}">${esc(option)}</button>`).join('')}</div>`;
  } else if (question.kind === 'input') {
    field = `<input class="answer-input" data-answer-q="${question.id}" placeholder="${esc(question.placeholder || 'Введите ответ')}" autocomplete="off" />`;
  } else {
    const checkCode = lessonMode ? '' : `<button class="button blue" type="button" data-check-code="${question.id}">▷ Проверить код</button>`;
    field = `<textarea class="code-editor" data-answer-q="${question.id}" spellcheck="false">${esc(question.starter)}</textarea>
      <div class="code-actions">${checkCode}<button class="button ghost" type="button" data-run-code="${question.id}">▶ Запустить</button></div>
      <section class="code-output" aria-live="polite"><b>Вывод</b><pre id="output-${question.id}">—</pre></section>
      <details class="hint"><summary>Нужна подсказка?</summary><p>${esc(question.hint)}</p></details>`;
  }
  return `<article class="question-card card${lessonMode ? ' step-question-card' : ''}" data-question="${question.id}">${head}${field}<div class="inline-result" id="result-${question.id}"></div></article>`;
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
        showInline(questionId, result.correct, result.message, result.checks, result.error_hint);
      } catch (error) { showInline(questionId, false, error.message); }
      button.disabled = false;
      button.textContent = '▷ Проверить код';
    });
  });
  scope.querySelectorAll('[data-run-code]').forEach((button) => {
    button.addEventListener('click', async () => {
      const questionId = button.dataset.runCode;
      const editor = scope.querySelector(`[data-answer-q="${questionId}"]`);
      button.disabled = true;
      button.textContent = 'Запускаем…';
      try {
        showCodeOutput(questionId, await api('/api/code/run', { method: 'POST', body: JSON.stringify({ question_id: questionId, code: editor.value }) }));
      } catch (error) { showCodeOutput(questionId, { error: error.message }); }
      button.disabled = false;
      button.textContent = '▶ Запустить';
    });
  });
}

function formatRunOutput(result) {
  const output = [
    result.stdout,
    result.stderr,
    result.error,
    result.timed_out && 'Превышено время выполнения.',
  ].filter(Boolean);
  return output.join('\n') || 'Нет вывода.';
}

function showCodeOutput(questionId, result) {
  const node = document.querySelector(`#output-${questionId}`);
  if (!node) return;
  node.textContent = formatRunOutput(result);
}

function showInline(questionId, correct, message, checks = [], errorHint = null) {
  const node = document.querySelector(`#result-${questionId}`);
  if (!node) return;
  const details = checks.length && !correct ? ` <small>(${checks.filter((item) => !item.passed).map((item) => `ожидалось ${esc(item.expected)}, получено ${esc(item.actual)}`).join('; ')})</small>` : '';
  node.className = `inline-result visible ${correct ? 'ok' : 'no'}`;
  const hint = errorHint
    ? `<div class="error-hint"><strong>${esc(errorHint.title)}</strong><span>${esc(errorHint.hint)}</span></div><small class="raw-error">${esc(errorHint.original)}</small>`
    : `${correct ? '✓' : '↺'} ${esc(message)}`;
  node.innerHTML = `${hint}${details}`;
}

function showVerdict(questionId, result) {
  const node = document.querySelector(`#result-${questionId}`);
  if (!node) return;
  if (result.correct) {
    node.className = 'inline-result visible ok';
    node.innerHTML = `<p class="verdict-title">✓ Верно</p><p>${rich(result.explanation || result.message || '')}</p>`;
    return;
  }
  const message = result.message || '';
  const explanation = result.explanation && result.explanation !== message ? `<p>${rich(result.explanation)}</p>` : '';
  const hint = result.error_hint
    ? `<div class="error-hint"><strong>${esc(result.error_hint.title)}</strong><span>${esc(result.error_hint.hint)}</span></div><small class="raw-error">${esc(result.error_hint.original)}</small>`
    : '';
  const checks = (result.checks || []).length
    ? `<ul class="check-list">${result.checks.map((item) => `<li>${item.passed ? '✓' : '✗'} Ожидалось ${esc(item.expected)}, получено ${esc(item.actual)}</li>`).join('')}</ul>`
    : '';
  node.className = 'inline-result visible no';
  node.innerHTML = `<p class="verdict-title">↺ Пока неверно</p>${message ? `<p>${rich(message)}</p>` : ''}${explanation}${hint}${checks}`;
}

function applyVerdictUi(questionId, result) {
  showVerdict(questionId, result);
  const check = document.querySelector('[data-lesson-check]');
  if (check) check.hidden = Boolean(result.correct);
  const next = document.querySelector('[data-step-next]');
  if (next) next.hidden = !result.correct;
}

function submissionResult(result, retryText = 'Попробовать ещё раз') {
  const items = result.results.map((item) => `<div class="result-item ${item.correct ? 'ok' : 'no'}"><b>${item.correct ? '✓ Верно' : '↺ Повтори'}</b> ${esc(item.explanation || item.message || '')}</div>`).join('');
  const action = result.passed
    ? '<a class="button blue" href="#/">К маршруту</a>'
    : `<button class="button" type="button" onclick="location.reload()">${retryText}</button>`;
  return `<section class="result-panel ${result.passed ? '' : 'fail'}" id="submission-result"><h2>${result.passed ? 'Отличная работа! 🎉' : 'Ещё один подход — и получится'}</h2><p>${esc(result.message)}${result.xp_gained ? ` +${result.xp_gained} XP.` : ''}</p><div class="result-list">${items}</div><div class="code-actions">${action}</div></section>`;
}

function buildLessonSteps(lesson) {
  const steps = [];
  const total = Math.max(lesson.theory.length, lesson.questions.length);
  for (let index = 0; index < total; index += 1) {
    if (lesson.theory[index]) steps.push({ kind: 'card', card: lesson.theory[index], cardIndex: index });
    if (lesson.questions[index]) steps.push({ kind: 'question', question: lesson.questions[index], questionIndex: index });
  }
  return steps;
}

async function renderLesson(id) {
  loading();
  const lesson = await api(`/api/lessons/${id}`);
  startLesson(lesson);
}

function startLesson(lesson) {
  lessonState = {
    lesson,
    steps: buildLessonSteps(lesson),
    index: 0,
    answers: {},
    verdicts: {},
    checkTokens: {},
    submitting: false,
    summary: null,
  };
  lesson.questions.forEach((question) => {
    lessonState.answers[question.id] = question.kind === 'code' ? (question.starter || '') : '';
  });
  renderStep();
}

function cardStepTemplate(step) {
  const state = lessonState;
  const card = step.card;
  const canRun = Boolean(card.example) && card.run !== false;
  const back = state.index > 0 ? '<button class="button ghost" type="button" data-step-back>← Назад</button>' : '';
  const runPanel = canRun
    ? `<div class="code-actions"><button class="button blue" type="button" data-run-example="${step.cardIndex}">▶ Запустить пример</button></div>
      <section class="code-output example-output" aria-live="polite" id="example-output-${step.cardIndex}"><b>Вывод</b><pre>—</pre></section>`
    : '';
  return `<article class="theory-card card step-card">
    <p class="step-kicker">Теория</p>
    <h2>${rich(card.title)}</h2>
    <p>${rich(card.text)}</p>
    <pre class="code-example"><code>${esc(card.example)}</code></pre>
    ${runPanel}
    ${card.tip ? `<div class="tip">${rich(card.tip)}</div>` : ''}
  </article>
  <div class="step-nav">${back}<div class="step-actions"><button class="button" type="button" data-step-next>Дальше</button></div></div>`;
}

function questionStepTemplate(step) {
  const state = lessonState;
  const question = step.question;
  const verdict = state.verdicts[question.id];
  const correct = Boolean(verdict && verdict.correct);
  const back = state.index > 0 ? '<button class="button ghost" type="button" data-step-back>← Назад</button>' : '';
  return `<section class="step step-question">
    ${questionTemplate(question, step.questionIndex + 1, { lessonId: state.lesson.id })}
    <div class="step-nav">${back}<div class="step-actions">
      <button class="button step-check" type="button" data-lesson-check="${question.id}"${correct ? ' hidden' : ''}>Проверить</button>
      <button class="button step-next" type="button" data-step-next${correct ? '' : ' hidden'}>Дальше</button>
    </div></div>
  </section>`;
}

function renderStep() {
  const state = lessonState;
  if (!state) return;
  const step = state.steps[state.index];
  const total = state.steps.length;
  const progress = state.steps.map((item, index) => {
    const stateClass = index < state.index ? 'done' : index === state.index ? 'current' : '';
    return `<span class="progress-seg ${stateClass}"></span>`;
  }).join('');
  const body = step.kind === 'card' ? cardStepTemplate(step) : questionStepTemplate(step);
  view.innerHTML = `<section class="lesson-wrap">
    <a class="back-link" href="#/">← К маршруту</a>
    <div class="lesson-head"><div><p class="eyebrow">Урок ${state.lesson.order} · ${state.lesson.duration} минут</p><h1>${esc(state.lesson.title)}</h1><p class="lead">${esc(state.lesson.subtitle)}</p><p class="lesson-meta"><span>⚡ ${state.lesson.xp} XP</span><span>🧩 ${state.lesson.questions.length} задания</span></p></div></div>
    <div class="lesson-progress-block">
      <div class="lesson-progress" role="progressbar" aria-label="Прогресс урока" aria-valuemin="1" aria-valuemax="${total}" aria-valuenow="${state.index + 1}">${progress}</div>
      <p class="step-caption">Шаг ${state.index + 1} из ${total}</p>
    </div>
    ${body}
  </section>`;
  bindStep(step);
}

function syncAnswer(questionId, value) {
  const state = lessonState;
  if (!state) return;
  if (state.answers[questionId] === value) return;
  state.answers[questionId] = value;
  clearVerdict(questionId);
}

function clearVerdict(questionId) {
  const state = lessonState;
  if (!state || !state.verdicts[questionId]) return;
  delete state.verdicts[questionId];
  const result = document.querySelector(`#result-${questionId}`);
  if (result) {
    result.className = 'inline-result';
    result.innerHTML = '';
  }
  const check = document.querySelector('[data-lesson-check]');
  if (check) check.hidden = false;
  const next = document.querySelector('[data-step-next]');
  if (next) next.hidden = true;
}

function setAnswerLocked(questionId, locked) {
  const scope = document.querySelector('.step-question');
  if (!scope) return;
  scope.querySelectorAll(`[data-answer-q="${questionId}"]`).forEach((node) => {
    node.readOnly = locked;
  });
  scope.querySelectorAll(`[data-choice-q="${questionId}"]`).forEach((node) => {
    node.disabled = locked;
  });
}

function captureCurrentAnswer() {
  const state = lessonState;
  if (!state) return;
  const step = state.steps[state.index];
  if (!step || step.kind !== 'question') return;
  const field = document.querySelector(`[data-answer-q="${step.question.id}"]`);
  if (field) state.answers[step.question.id] = field.value;
}

function bindStep(step) {
  const state = lessonState;
  if (step.kind === 'card') {
    document.querySelector('[data-step-next]')?.addEventListener('click', goNext);
    document.querySelector('[data-step-back]')?.addEventListener('click', goBack);
    document.querySelector('[data-run-example]')?.addEventListener('click', runExample);
    return;
  }
  const scope = document.querySelector('.step-question');
  bindQuestionControls(scope);
  const question = step.question;
  const field = scope.querySelector(`[data-answer-q="${question.id}"]`);
  if (field) {
    field.value = state.answers[question.id] ?? field.value;
    const sync = () => syncAnswer(question.id, field.value);
    field.addEventListener('input', sync);
    field.addEventListener('keyup', sync);
  }
  scope.querySelectorAll(`[data-choice-q="${question.id}"]`).forEach((button) => {
    if (state.answers[question.id] === button.dataset.value) button.classList.add('selected');
    button.addEventListener('click', () => syncAnswer(question.id, button.dataset.value));
  });
  if (state.verdicts[question.id]) applyVerdictUi(question.id, state.verdicts[question.id]);
  document.querySelector('[data-lesson-check]')?.addEventListener('click', (event) => checkStep(question.id, event.currentTarget));
  document.querySelector('[data-step-next]')?.addEventListener('click', goNext);
  document.querySelector('[data-step-back]')?.addEventListener('click', goBack);
}

function goNext() {
  const state = lessonState;
  if (!state || state.submitting) return;
  captureCurrentAnswer();
  if (state.index < state.steps.length - 1) {
    state.index += 1;
    renderStep();
    return;
  }
  submitLesson();
}

function goBack() {
  const state = lessonState;
  if (!state || state.index === 0) return;
  captureCurrentAnswer();
  state.index -= 1;
  renderStep();
}

async function checkStep(questionId, button) {
  const state = lessonState;
  if (!state) return;
  captureCurrentAnswer();
  const answer = state.answers[questionId] ?? '';
  const token = (state.checkTokens[questionId] || 0) + 1;
  state.checkTokens[questionId] = token;
  const label = button.textContent;
  button.disabled = true;
  button.textContent = 'Проверяем…';
  setAnswerLocked(questionId, true);
  try {
    const result = await api(`/api/lessons/${state.lesson.id}/check`, { method: 'POST', body: JSON.stringify({ question_id: questionId, answer }) });
    if (lessonState !== state || state.checkTokens[questionId] !== token) return;
    // Ответ мог измениться, пока шёл запрос: вердикт относится только к отправленному ответу.
    const field = document.querySelector(`[data-answer-q="${questionId}"]`);
    if (field && field.value !== answer) return;
    if ((state.answers[questionId] ?? '') !== answer) return;
    state.verdicts[questionId] = result;
    const step = state.steps[state.index];
    if (step && step.kind === 'question' && step.question.id === questionId) {
      applyVerdictUi(questionId, result);
    }
  } catch (error) {
    if (lessonState === state && state.checkTokens[questionId] === token) toast(error.message);
  } finally {
    if (lessonState === state && state.checkTokens[questionId] === token) {
      setAnswerLocked(questionId, false);
      button.disabled = false;
      button.textContent = label;
    }
  }
}

async function runExample(event) {
  const state = lessonState;
  if (!state) return;
  const button = event.currentTarget;
  const index = Number(button.dataset.runExample);
  const card = state.lesson.theory[index];
  const output = document.querySelector(`#example-output-${index} pre`);
  const label = button.textContent;
  button.disabled = true;
  button.textContent = 'Запускаем…';
  try {
    const result = await api('/api/code/run', { method: 'POST', body: JSON.stringify({ code: card.example }) });
    if (output) output.textContent = formatRunOutput(result);
  } catch (error) {
    if (output) output.textContent = error.message;
  }
  button.disabled = false;
  button.textContent = label;
}

async function submitLesson() {
  const state = lessonState;
  if (!state || state.submitting) return;
  state.submitting = true;
  const answers = state.lesson.questions.map((question) => ({ question_id: question.id, answer: state.answers[question.id] ?? '' }));
  try {
    const result = await api(`/api/lessons/${state.lesson.id}/submit`, { method: 'POST', body: JSON.stringify({ answers }) });
    state.summary = result;
    try { await refreshDashboard(); } catch (error) { /* итог важнее обновления шапки */ }
    if (result.passed) toast(`+${result.xp_gained} XP — урок пройден!`);
    renderSummary();
  } catch (error) {
    state.submitting = false;
    toast(error.message);
  }
}

function renderSummary() {
  const state = lessonState;
  if (!state || !state.summary) return;
  const result = state.summary;
  if (result.passed) {
    const next = dashboard?.next_lesson;
    view.innerHTML = `<section class="lesson-summary card summary-ok">
      <p class="step-kicker">Итог урока</p>
      <h1>Урок пройден</h1>
      <p class="summary-xp">+${result.xp_gained} XP</p>
      <p class="lead">${esc(result.message)}</p>
      <div class="step-actions summary-actions">
        ${next ? `<a class="button" href="#/lesson/${next.id}">Следующий урок</a>` : ''}
        <a class="button ghost" href="#/">К маршруту</a>
      </div>
    </section>`;
    return;
  }
  const missed = result.results.filter((item) => !item.correct).map((item) => {
    const number = state.lesson.questions.findIndex((question) => question.id === item.question_id) + 1;
    return `<li><b>Задание ${number}</b> — ${esc(item.message || 'ответ не засчитан')}</li>`;
  }).join('');
  view.innerHTML = `<section class="lesson-summary card summary-fail">
    <p class="step-kicker">Итог урока</p>
    <h1>Пока не всё засчитано</h1>
    <p class="lead">${esc(result.message)}</p>
    <ul class="missed-list">${missed || '<li>Проверь ответы и попробуй ещё раз.</li>'}</ul>
    <div class="step-actions summary-actions">
      <button class="button" type="button" data-lesson-restart>Пройти заново</button>
      <a class="button ghost" href="#/">К маршруту</a>
    </div>
  </section>`;
  document.querySelector('[data-lesson-restart]')?.addEventListener('click', () => startLesson(state.lesson));
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
      showInline(question.id, result.correct, result.message, result.checks, result.error_hint);
      await refreshDashboard();
      if (result.correct) toast(`Верно! +${result.xp_gained} XP`);
    } catch (error) { toast(error.message); }
  });
}

async function renderExam(moduleId) {
  loading();
  const exam = await api(`/api/exams/${moduleId}`);
  view.innerHTML = `<section class="exam-wrap"><a class="back-link" href="#/">← К маршруту</a><article class="exam-hero card"><p class="eyebrow">Контрольная точка</p><h1>${esc(exam.title)}</h1><p class="lead">${esc(exam.description)} Для зачёта нужно 70% правильных ответов. Награда — 50 XP.</p></article><form id="exam-form">${exam.questions.map((question, index) => questionTemplate(question, index + 1)).join('')}<div class="submit-row"><button class="button blue" type="submit">Сдать экзамен <span>🏁</span></button></div></form></section>`;
  const form = document.querySelector('#exam-form');
  bindQuestionControls(form);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('[type="submit"]'); button.disabled = true;
    try {
      const result = await api(`/api/exams/${moduleId}/submit`, { method: 'POST', body: JSON.stringify({ answers: getAnswers(form, exam.questions) }) });
      document.querySelector('#submission-result')?.remove();
      form.insertAdjacentHTML('afterend', submissionResult(result, 'Пересдать экзамен'));
      result.results.forEach((item) => showInline(item.question_id, item.correct, item.message, item.checks, item.error_hint));
      await refreshDashboard();
      if (result.passed) toast(`Экзамен сдан! +${result.xp_gained} XP`);
    } catch (error) { toast(error.message); }
    button.disabled = false;
  });
}

async function render() {
  const current = route();
  if (!current.startsWith('/lesson/')) lessonState = null;
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

document.addEventListener('keydown', (event) => {
  const editor = event.target.closest('.code-editor');
  if (!editor || editor.readOnly || editor.disabled) return;
  const { value, selectionStart: start, selectionEnd: end } = editor;
  const lineStart = value.lastIndexOf('\n', start - 1) + 1;
  const lineEndIndex = value.indexOf('\n', Math.max(start, end - 1));
  const lineEnd = lineEndIndex < 0 ? value.length : lineEndIndex;

  if (event.key === 'Enter') {
    const line = value.slice(lineStart, lineEnd);
    const indent = (line.match(/^\s*/) || [''])[0] + (line.trimEnd().endsWith(':') ? '    ' : '');
    event.preventDefault();
    editor.setRangeText(`\n${indent}`, start, end, 'end');
    return;
  }

  if (event.key !== 'Tab') return;
  event.preventDefault();
  const selected = value.slice(lineStart, lineEnd);
  if (!event.shiftKey && !selected.includes('\n')) {
    editor.setRangeText('    ', start, end, 'end');
    return;
  }
  if (event.shiftKey) {
    const unindented = selected.replace(/^ {1,4}/gm, '');
    const removedBeforeCursor = Math.min(4, (value.slice(lineStart, start).match(/^ */) || [''])[0].length);
    editor.value = value.slice(0, lineStart) + unindented + value.slice(lineEnd);
    editor.setSelectionRange(start - removedBeforeCursor, end - (selected.length - unindented.length));
  } else {
    const indented = selected.replace(/^/gm, '    ');
    const lines = selected.split('\n').length;
    editor.value = value.slice(0, lineStart) + indented + value.slice(lineEnd);
    editor.setSelectionRange(start + 4, end + lines * 4);
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key !== 'Enter' || event.defaultPrevented) return;
  const state = lessonState;
  if (!state || state.summary || state.submitting) return;
  const step = state.steps[state.index];
  if (!step || step.kind !== 'card') return;
  const target = event.target;
  if (target instanceof Element && target.closest('button, a, input, textarea, select, summary')) return;
  event.preventDefault();
  goNext();
});

window.addEventListener('hashchange', render);
render();
