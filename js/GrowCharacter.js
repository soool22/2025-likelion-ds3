(() => {
  const TOTAL = 4; // 전체 아이템 개수 = 4 (각 25%)
  const slots = [
    document.getElementById('hat'),
    document.getElementById('pot'),
    document.getElementById('chair')
    // 네 번째 아이템은 아직 없으니까 제외됨
  ];
  const cards = Array.from(document.querySelectorAll('#bar .card')).filter((_, i) => i < slots.length);

  // 초기엔 슬롯 숨김
  slots.forEach(el => { if (el) el.style.display = 'none'; });

  // 꾸밈지수 UI 참조
  const barEl   = document.getElementById('achievement');
  const labelEl = document.getElementById('percent');

  // 꾸밈지수 갱신
  function updateDecorationScore(){
    const equippedCount = cards.filter(c => c.classList.contains('on')).length;
    const pct = Math.round((equippedCount / TOTAL) * 100); // 전체 대비 %
    if (barEl)   barEl.style.width = pct + '%';
    if (labelEl) labelEl.textContent = pct + '%';
  }

  // 카드 토글
  function toggleByIndex(i){
    const slot = slots[i];
    const card = cards[i];
    if (!slot || !card) return;

    const on = card.classList.toggle('on');
    slot.style.display = on ? 'block' : 'none';
    updateDecorationScore();
  }

  // 클릭 바인딩
  cards.forEach((card, i) => {
    card.style.cursor = 'pointer';
    card.addEventListener('click', () => toggleByIndex(i));
  });

  // 최초 1회 계산
  updateDecorationScore();
})();