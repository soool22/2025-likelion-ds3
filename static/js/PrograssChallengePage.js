document.addEventListener('DOMContentLoaded', () => {
  initProgressBars();        // 페이지 최초 렌더된 진행형 카드들 바/퍼센트 표시
  restoreJoinedMissions();   // localStorage 기반으로 '추천 → 진행중' 재배치
  bindJoinButtons();         // '참여하기' 클릭 시 처리
});

/* ---------- Storage helpers ---------- */
const STORAGE_KEY = 'joinedMissions';

function getJoinedSet() {
  try {
    const arr = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    return new Set(arr);
  } catch {
    return new Set();
  }
}

function saveJoinedSet(set) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
}

function addJoined(id) {
  const set = getJoinedSet();
  set.add(String(id));
  saveJoinedSet(set);
}

function removeJoined(id) {
  const set = getJoinedSet();
  set.delete(String(id));
  saveJoinedSet(set);
}

/* ---------- UI helpers ---------- */
function getTopContainer() {
  return document.querySelector('#containerBodyTop .containerBodyContent'); // #progressList도 OK
}

function removeEmptyMsg() {
  const topContainer = getTopContainer();
  if (!topContainer) return;
  const emptyMsg = topContainer.querySelector('.emptyMsg');
  if (emptyMsg) emptyMsg.remove();
}

function toProgressMarkup(cardEl) {
  // 상태 배지: 참여가능 → 진행중
  const stateEl = cardEl.querySelector('.challengeMiddleSmallBox .state');
  if (stateEl) {
    stateEl.textContent = '진행중';
    stateEl.classList.remove('yet');
  }

  // 하단 영역 교체(진행바 + 퍼센트)
  const lastRow = cardEl.querySelector('.challengeLastBox');
  if (lastRow) {
    lastRow.innerHTML = `
      <div class="prograssBar"><div class="prograss"></div></div>
      <div class="scoreBigBox" style="display:none;">
        <p class="nowScoreCount">1</p>
        <p class="totalScoreCount">3</p>
      </div>
      <p class="nowScore">0%</p>
    `;
  }

  // 클래스 전환
  cardEl.classList.remove('joinChallengeBox');
  cardEl.classList.add('prograssChallengeBox');

  // 진행바 렌더
  renderPercentBar(cardEl);
}

function moveToTopSection(cardEl) {
  const topContainer = getTopContainer();
  if (!topContainer) return;
  removeEmptyMsg();              // "챌린지가 없습니다." 제거
  topContainer.appendChild(cardEl);
}

/* ---------- 초기 복원 ---------- */
function restoreJoinedMissions() {
  const joined = getJoinedSet();
  if (!joined.size) return;

  // 1) 추천 영역에서 내가 참여했던 카드들을 찾아 위로 올림
  document.querySelectorAll('.joinChallengeBox[data-mission-id]').forEach(card => {
    const id = card.getAttribute('data-mission-id');
    if (joined.has(String(id))) {
      toProgressMarkup(card);
      moveToTopSection(card);
    }
  });

  // 2) 클린업(선택): 스토리지엔 있는데 DOM에 아예 없는 ID는 제거
  const stillExists = new Set(
    [...document.querySelectorAll('[data-mission-id]')].map(el => el.getAttribute('data-mission-id'))
  );
  let mutated = false;
  joined.forEach(id => {
    if (!stillExists.has(String(id))) {
      joined.delete(String(id));
      mutated = true;
    }
  });
  if (mutated) saveJoinedSet(joined);
}

/* ---------- 클릭 바인딩 ---------- */
function bindJoinButtons() {
  const topContainer = getTopContainer();

  document.querySelectorAll('.joinBtn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (!topContainer) return;

      const joinBox = btn.closest('.joinChallengeBox');
      if (!joinBox) return;

      const missionId = joinBox.getAttribute('data-mission-id');
      if (!missionId) {
        alert('mission id가 없습니다. data-mission-id를 넣어주세요.');
        return;
      }

      // 1) localStorage에 기록
      addJoined(missionId);

      // 2) UI 전환 + 이동
      toProgressMarkup(joinBox);
      moveToTopSection(joinBox);
    });
  });
}

/* ---------- 진행바 관련(기존 로직 유지) ---------- */
function initProgressBars() {
  document.querySelectorAll('.prograssChallengeBox').forEach(box => renderPercentBar(box));
}

function renderPercentBar(box) {
  const lastRow = box.querySelector('.challengeLastBox');
  const barEl   = box.querySelector('.prograss');
  if (!lastRow || !barEl) return;

  let nowScoreLabel = lastRow.querySelector('.nowScore');
  const nowNumEl   = box.querySelector('.scoreBigBox .nowScoreCount');
  const totalNumEl = box.querySelector('.scoreBigBox .totalScoreCount');
  let pct = 0;

  if (nowScoreLabel && /%$/.test(nowScoreLabel.textContent.trim())) {
    pct = Math.max(0, Math.min(100, parseInt(nowScoreLabel.textContent.trim().replace('%',''), 10) || 0));
  } else if (nowNumEl && totalNumEl) {
    const now   = Math.max(0, parseInt(nowNumEl.textContent.trim(), 10) || 0);
    const total = Math.max(1, parseInt(totalNumEl.textContent.trim(), 10) || 1);
    pct = Math.max(0, Math.min(100, Math.round((now / total) * 100)));
    if (!nowScoreLabel) {
      nowScoreLabel = document.createElement('p');
      nowScoreLabel.className = 'nowScore';
      lastRow.appendChild(nowScoreLabel);
    }
    nowScoreLabel.textContent = pct + '%';
  } else {
    if (!nowScoreLabel) {
      nowScoreLabel = document.createElement('p');
      nowScoreLabel.className = 'nowScore';
      lastRow.appendChild(nowScoreLabel);
    }
    nowScoreLabel.textContent = '0%';
    pct = 0;
  }

  barEl.style.width = pct + '%';
}

