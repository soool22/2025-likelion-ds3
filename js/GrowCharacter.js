(() => {
  // 미리 배치된 슬롯들(보이기/숨기기만 토글)
  const slots = [
    document.getElementById('hat'),   // 1번째 카드
    document.getElementById('pot'),   // 2번째 카드
    document.getElementById('chair')  // 3번째 카드
  ];

  // 카드들 (4번째 빈 카드는 자동으로 건너뜀)
  const cards = Array.from(document.querySelectorAll('#bar .card'))
    .filter((card, idx) => idx < slots.length); // 앞 3개만

  // 시작은 모두 숨김
  slots.forEach(el => { if (el) el.style.display = 'none'; });

  // 토글 함수
  function toggleByIndex(i) {
    const slot = slots[i];
    const card = cards[i];
    if (!slot || !card) return;

    const on = card.classList.toggle('on'); // 카드에 on 클래스 토글(선택 표시용)
    slot.style.display = on ? 'block' : 'none';
  }

  // 카드 클릭 이벤트
  cards.forEach((card, i) => {
    card.style.cursor = 'pointer';
    card.addEventListener('click', () => toggleByIndex(i));
  });
})();

(() => {
  const bar = document.getElementById('achievement'); // 노란 바
  const label = document.getElementById('percent');   // "50%" 텍스트

  // 달성률 설정 (0~100)
  function setAchievement(pct){
    const v = Math.max(0, Math.min(100, Number(pct) || 0));
    bar.style.width = v + '%';
    if (label) label.textContent = v + '%';
  }

  // 초기: 현재 텍스트(예: "50%")를 읽어 적용
  const initial = parseInt((label?.textContent || '0').replace('%',''), 10);
  setAchievement(initial);

  // 예시) 2초 뒤 80%로 바꾸고 싶다면:
  // setTimeout(() => setAchievement(80), 2000);

  // 전역에서 호출하고 싶으면 window로 내보내기(선택)
  window.setAchievement = setAchievement;
})();