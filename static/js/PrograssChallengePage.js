document.addEventListener('DOMContentLoaded', () => {
  const COLOR_ON  = '#FFB635';
  const COLOR_OFF = '#d9d9d9';

  document.querySelectorAll('.prograssChallengeBox').forEach(box => {
    const nowEl   = box.querySelector('.nowScore');
    const totalEl = box.querySelector('.totalScore');
    const barEl   = box.querySelector('.prograss');
    const dots    = box.querySelectorAll('.circleBox .circle'); // [start, middle, end]

    if (!nowEl || !totalEl || !barEl || dots.length < 3) return;

    const now   = Math.max(0, parseInt(nowEl.textContent.trim(), 10) || 0);
    const total = Math.max(1, parseInt(totalEl.textContent.replace('/', '').trim(), 10) || 1);

    // 스냅 단계: 시작점은 기본 채움이므로 now-1 단계로 본다.
    const steps   = Math.max(1, total - 1);                 // (예: 3 → 2단계)
    const stepIdx = Math.min(steps, Math.max(0, now - 1));  // 0..steps

    // 바 길이를 점 위치에 '스냅' (0%, 50%, 100% …)
    const snappedPercent = (stepIdx / steps) * 100;         // 0, 50, 100
    barEl.style.width = snappedPercent + '%';

    // 점 색상: 시작점은 항상 ON, 그 외는 진행단계와 비교
    dots[0].style.backgroundColor = COLOR_ON;                     // start
    dots[1].style.backgroundColor = (stepIdx >= 1) ? COLOR_ON : COLOR_OFF; // middle
    dots[2].style.backgroundColor = (stepIdx >= 2) ? COLOR_ON : COLOR_OFF; // end
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const containerBodyTop = document.querySelector('#containerBodyTop .containerBodyContent');

  document.querySelectorAll('.joinBtn').forEach(button => {
    button.addEventListener('click', e => {
      e.preventDefault(); // form submit 방지

      // 버튼이 속한 joinChallengeBox 가져오기
      const joinBox = button.closest('.joinChallengeBox');
      if (!joinBox) return;

      // 버튼 영역을 프로그래스바로 교체
      const challengeLastBox = joinBox.querySelector('.challengeLastBox');
      challengeLastBox.innerHTML = `
        <div class="prograssBar">
          <div class="prograss"></div>
          <div class="circleBox">
            <div class="circle start"></div>
            <div class="circle middle"></div>
            <div class="circle end"></div>
          </div>
        </div>
        <div class="scoreBigBox">
          <div class="scoreBox">
            <p class="nowScore">1</p>
            <p class="totalScore">/3</p>
          </div>
          <img class="stampIcon" src="../img/stamp.svg"/>
        </div>
      `;

      // box의 클래스도 prograssChallengeBox 로 바꿔줌
      joinBox.classList.remove('joinChallengeBox');
      joinBox.classList.add('prograssChallengeBox');

      // "내가 참여 중인 챌린지" 영역으로 이동
      containerBodyTop.appendChild(joinBox);

      // 프로그래스 초기화 함수 호출 (앞에서 만든 js)
      updateProgressBars();
    });
  });
});

// 앞에서 만들었던 프로그래스바 색/길이 업데이트 함수
function updateProgressBars() {
  const COLOR_ON  = '#FFB635';
  const COLOR_OFF = '#d9d9d9';

  document.querySelectorAll('.prograssChallengeBox').forEach(box => {
    const nowEl   = box.querySelector('.nowScore');
    const totalEl = box.querySelector('.totalScore');
    const barEl   = box.querySelector('.prograss');
    const dots    = box.querySelectorAll('.circleBox .circle');

    if (!nowEl || !totalEl || !barEl || dots.length < 3) return;

    const now   = Math.max(0, parseInt(nowEl.textContent.trim(), 10) || 0);
    const total = Math.max(1, parseInt(totalEl.textContent.replace('/', '').trim(), 10) || 1);

    const steps   = Math.max(1, total - 1);
    const stepIdx = Math.min(steps, Math.max(0, now - 1));

    const snappedPercent = (stepIdx / steps) * 100;
    barEl.style.width = snappedPercent + '%';

    dots[0].style.backgroundColor = COLOR_ON;
    dots[1].style.backgroundColor = (stepIdx >= 1) ? COLOR_ON : COLOR_OFF;
    dots[2].style.backgroundColor = (stepIdx >= 2) ? COLOR_ON : COLOR_OFF;
  });
}
