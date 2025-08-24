document.addEventListener('DOMContentLoaded', () => {
  fillRatingBars();
});

/**
 * #scoreBarBox 안의 각 .barBox 에서
 *  - 오른쪽 (20) 숫자를 읽어 총합을 구하고
 *  - 각 행 비율만큼 .achievement 의 width 를 설정
 */
function fillRatingBars() {
  const rows = Array.from(document.querySelectorAll('#scoreBarBox .barBox'));
  if (!rows.length) return;

  // 각 행의 "오른쪽 숫자(예: (20))"를 읽어 정수로 변환
  const counts = rows.map(row => {
    const numEls = row.querySelectorAll('.numStyle');
    const rightCountEl = numEls[numEls.length - 1]; // 마지막 numStyle이 오른쪽 개수
    const n = parseInt((rightCountEl.textContent || '').replace(/[^\d]/g, ''), 10);
    return Number.isNaN(n) ? 0 : n;
  });

  const total = counts.reduce((a, b) => a + b, 0);

  rows.forEach((row, i) => {
    const fill = row.querySelector('.achievement');
    if (!fill) return;

    const pct = total > 0 ? (counts[i] / total) * 100 : 0;
    fill.style.width = pct.toFixed(2) + '%';

    // 접근성/툴팁용
    fill.setAttribute('aria-valuenow', Math.round(pct));
    fill.setAttribute('aria-valuemin', 0);
    fill.setAttribute('aria-valuemax', 100);
    fill.title = `${counts[i]} / ${total} (${Math.round(pct)}%)`;
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const filledSrc = "{% static 'IMG/starpicked.svg' %}"; // 채운 별
  const emptySrc  = "{% static 'IMG/star.svg' %}";       // 빈 별 (원하면 바꾸세요)
  const MAX = 5;

  document.querySelectorAll('.review-star').forEach(el => {
    const raw = (el.textContent || '').trim();

    // 1) "★★★★☆" 같은 문자열이면 ★ 개수 세기
    let filled = (raw.match(/★/g) || []).length;

    // 2) 만약 숫자라면 숫자로 처리 (예: "4")
    if (!filled && /^\d+$/.test(raw)) {
      filled = parseInt(raw, 10) || 0;
    }

    filled = Math.max(0, Math.min(MAX, filled));
    const empty = MAX - filled;

    // 이미지로 교체
    const frag = document.createDocumentFragment();
    for (let i = 0; i < filled; i++) {
      const img = document.createElement('img');
      img.src = filledSrc;
      img.alt = '★';
      frag.appendChild(img);
    }
    for (let i = 0; i < empty; i++) {
      const img = document.createElement('img');
      img.src = emptySrc;
      img.alt = '☆';
      frag.appendChild(img);
    }

    el.textContent = '';   // 기존 ★ 텍스트 지우기
    el.appendChild(frag);  // 이미지 삽입
  });
});