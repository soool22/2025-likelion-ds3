document.addEventListener('DOMContentLoaded', () => {
  initProgressBars();   // 현재 진행형 카드들 퍼센트 표시
  bindJoinButtons();    // 참여하기 → 진행형으로 전환
});

function initProgressBars() {
  document.querySelectorAll('.prograssChallengeBox').forEach(box => renderPercentBar(box));
}

/**
 * box 안의 상태를 읽어 진행바/퍼센트 갱신
 * - 우측 nowScore 가 "50%" 처럼 퍼센트를 이미 갖고 있으면 그걸 사용
 * - 아니면 숨겨진 now/total 숫자를 읽어 퍼센트를 계산
 */
function renderPercentBar(box) {
  const lastRow = box.querySelector('.challengeLastBox');
  const barEl   = box.querySelector('.prograss');
  if (!lastRow || !barEl) return;

  // 우측에 표시되는 텍스트
  let nowScoreLabel = lastRow.querySelector('.nowScore');

  // 숨김 계산용(있을 수도, 없을 수도)
  const nowNumEl   = box.querySelector('.scoreBigBox .nowScoreCount');
  const totalNumEl = box.querySelector('.scoreBigBox .totalScoreCount');

  let pct = 0;

  // 1) 라벨이 "50%" 형태면 그대로 사용
  if (nowScoreLabel && /%$/.test(nowScoreLabel.textContent.trim())) {
    pct = Math.max(0, Math.min(100,
      parseInt(nowScoreLabel.textContent.trim().replace('%',''), 10) || 0
    ));
  }
  // 2) 아니면 숨김 숫자(now/total)로 계산
  else if (nowNumEl && totalNumEl) {
    const now   = Math.max(0, parseInt(nowNumEl.textContent.trim(), 10) || 0);
    const total = Math.max(1, parseInt(totalNumEl.textContent.trim(), 10) || 1);
    pct = Math.max(0, Math.min(100, Math.round((now / total) * 100)));

    // 표시용 nowScore 라벨이 없으면 만들어 오른쪽에 붙임
    if (!nowScoreLabel) {
      nowScoreLabel = document.createElement('p');
      nowScoreLabel.className = 'nowScore';
      lastRow.appendChild(nowScoreLabel);
    }
    nowScoreLabel.textContent = pct + '%';
  }
  // 3) 어떤 정보도 없으면 0%
  else {
    if (!nowScoreLabel) {
      nowScoreLabel = document.createElement('p');
      nowScoreLabel.className = 'nowScore';
      lastRow.appendChild(nowScoreLabel);
    }
    nowScoreLabel.textContent = '0%';
    pct = 0;
  }

  // 진행 바 적용
  barEl.style.width = pct + '%';
}

/** 참여하기 버튼 → 진행형 카드로 변환하고 상단 섹션으로 이동 */
function bindJoinButtons() {
  const topContainer = document.querySelector('#containerBodyTop .containerBodyContent');

  document.querySelectorAll('.joinBtn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault(); // 폼 제출 방지

      const joinBox = btn.closest('.joinChallengeBox');
      if (!joinBox || !topContainer) return;

      const lastRow = joinBox.querySelector('.challengeLastBox');

      // 진행형 UI로 교체: 좌측 바 + 우측 퍼센트(nowScore),
      //   계산용 now/total 은 숨김으로 보관(필요 시 서버 데이터 넣기)
      lastRow.innerHTML = `
        <div class="prograssBar">
          <div class="prograss"></div>
        </div>
        <div class="scoreBigBox" style="display:none;">
          <p class="nowScoreCount">1</p>
          <p class="totalScoreCount">3</p>
        </div>
        <p class="nowScore">0%</p>
      `;

      // 카드 타입 변경 및 상단으로 이동
      joinBox.classList.remove('joinChallengeBox');
      joinBox.classList.add('prograssChallengeBox');
      topContainer.appendChild(joinBox);

      // 퍼센트/바 렌더
      renderPercentBar(joinBox);
    });
  });
}

/** 참여하기 버튼 → 진행형 카드로 변환하고 상단 섹션으로 이동 */
function bindJoinButtons() {
  const topContainer = document.querySelector('#containerBodyTop .containerBodyContent');

  document.querySelectorAll('.joinBtn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();

      const joinBox = btn.closest('.joinChallengeBox');
      if (!joinBox || !topContainer) return;

      // ✅ 상태 배지 업데이트 (참여가능 → 진행중)
      const stateEl = joinBox.querySelector('.challengeMiddleSmallBox .state');
      if (stateEl) {
        stateEl.textContent = '진행중';
        stateEl.classList.remove('yet');
      }

      const lastRow = joinBox.querySelector('.challengeLastBox');
      lastRow.innerHTML = `
        <div class="prograssBar">
          <div class="prograss"></div>
        </div>
        <div class="scoreBigBox" style="display:none;">
          <p class="nowScoreCount">1</p>
          <p class="totalScoreCount">3</p>
        </div>
        <p class="nowScore">0%</p>
      `;

      joinBox.classList.remove('joinChallengeBox');
      joinBox.classList.add('prograssChallengeBox');
      topContainer.appendChild(joinBox);

      renderPercentBar(joinBox);
    });
  });
}
