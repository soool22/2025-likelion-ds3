document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.checkboxStyle').forEach(labelEl => {
    const inputEl = labelEl.nextElementSibling;
    if (!inputEl || !inputEl.classList.contains('realCheckBox')) return;

    // name/value를 data-*에서 보정 (만약 템플릿에 빠져있어도 안전)
    if (!inputEl.name && labelEl.dataset.name) inputEl.name = labelEl.dataset.name;
    if (!inputEl.value && labelEl.dataset.value) inputEl.value = labelEl.dataset.value;

    // 초기 상태 반영
    syncPicked(labelEl, inputEl);

    // 클릭으로 토글
    labelEl.addEventListener('click', (e) => {
      e.preventDefault();
      inputEl.checked = !inputEl.checked;
      syncPicked(labelEl, inputEl);
    });

    // 키보드 접근성
    labelEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        inputEl.checked = !inputEl.checked;
        syncPicked(labelEl, inputEl);
      }
    });

    // 실제 체크박스를 클릭해도 스타일 동기화
    inputEl.addEventListener('change', () => syncPicked(labelEl, inputEl));
  });

  function syncPicked(labelEl, inputEl) {
    labelEl.classList.toggle('picked', !!inputEl.checked);
  }
});