console.log('[PrograssChallengePage] loaded');

document.addEventListener('DOMContentLoaded', () => {
  initProgressBars();        // 서버 렌더된 진행 카드 진행바 (% 텍스트 → width)
  restoreJoinedMissions();   // localStorage 기반으로 추천→진행 전환 및 이동
});

/* ---------- 상수 & 스토리지 ---------- */
const STORAGE_KEY = 'joinedMissions';

function getJoinedSet() {
  try {
    const arr = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    return new Set(arr.map(String));
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

/* ---------- DOM 헬퍼 ---------- */
function getTopContainer() {
  // 기본 구조(#containerBodyTop .containerBodyContent) + 폴백(#progressList)
  return (
    document.querySelector('#containerBodyTop .containerBodyContent') ||
    document.querySelector('#progressList')
  );
}

function getRecommendedContainer() {
  return (
    document.querySelector('#containerBodyBottom .containerBodyContent') ||
    document.querySelector('#recommendedList')
  );
}

function removeEmptyMsg() {
  const topContainer = getTopContainer();
  if (!topContainer) return;
  const emptyMsg = topContainer.querySelector('.emptyMsg');
  if (emptyMsg) emptyMsg.remove();
}

/* ---------- UI 전환 ---------- */
function toProgressMarkup(cardEl) {
  // 상태 배지: 참여가능 → 진행중
  const stateEl = cardEl.querySelector('.challengeMiddleSmallBox .state');
  if (stateEl) {
    stateEl.textContent = '진행중';
    stateEl.classList.remove('yet');
  }

  // 하단 영역: 버튼 → 진행바 + 퍼센트
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

  // 진행바 초기 렌더
  renderPercentBar(cardEl);
}

function moveToTopSection(cardEl) {
  const topContainer = getTopContainer();
  if (!topContainer) return;
  removeEmptyMsg();
  topContainer.appendChild(cardEl);
}

/* ---------- 초기 복원 ---------- */
function restoreJoinedMissions() {
  const joined = getJoinedSet();
  if (!joined.size) return;

  // 추천 영역에서 참여했던 카드들을 찾아 위로 이동
  document.querySelectorAll('.joinChallengeBox[data-mission-id]').forEach((card) => {
    const id = card.getAttribute('data-mission-id');
    if (id && joined.has(String(id))) {
      toProgressMarkup(card);
      moveToTopSection(card);
    }
  });

  // 존재하지 않는 id 정리(선택)
  const stillExists = new Set(
    [...document.querySelectorAll('[data-mission-id]')].map((el) => String(el.getAttribute('data-mission-id')))
  );
  let mutated = false;
  joined.forEach((id) => {
    if (!stillExists.has(String(id))) {
      joined.delete(String(id));
      mutated = true;
    }
  });
  if (mutated) saveJoinedSet(joined);
}

/* ---------- 참여 버튼: 이벤트 위임 ---------- */
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.joinBtn');
  if (!btn) return;

  e.preventDefault();

  const joinBox = btn.closest('.joinChallengeBox');
  if (!joinBox) return;

  const missionId = joinBox.getAttribute('data-mission-id');
  if (!missionId) {
    alert('mission id가 없습니다. data-mission-id를 넣어주세요.');
    return;
  }

  // 스토리지 기록
  addJoined(missionId);

  // UI 전환 + 상단 이동
  toProgressMarkup(joinBox);
  moveToTopSection(joinBox);
});

/* ---------- 진행바 렌더 ---------- */
function initProgressBars() {
  document.querySelectorAll('.prograssChallengeBox').forEach((box) => renderPercentBar(box));
}

function renderPercentBar(box) {
  const lastRow = box.querySelector('.challengeLastBox');
  const barEl = box.querySelector('.prograss');
  if (!lastRow || !barEl) return;

  let nowScoreLabel = lastRow.querySelector('.nowScore');
  const nowNumEl = box.querySelector('.scoreBigBox .nowScoreCount');
  const totalNumEl = box.querySelector('.scoreBigBox .totalScoreCount');
  let pct = 0;

  // 우선순위 1: 이미 퍼센트 텍스트가 있는 경우(서버에서 {{ progress.percent }}% 렌더)
  if (nowScoreLabel && /%$/.test(nowScoreLabel.textContent.trim())) {
    pct = Math.max(0, Math.min(100, parseInt(nowScoreLabel.textContent.trim().replace('%', ''), 10) || 0));
  }
  // 우선순위 2: 숫자(now/total) 기반으로 계산
  else if (nowNumEl && totalNumEl) {
    const now = Math.max(0, parseInt(nowNumEl.textContent.trim(), 10) || 0);
    const total = Math.max(1, parseInt(totalNumEl.textContent.trim(), 10) || 1);
    pct = Math.max(0, Math.min(100, Math.round((now / total) * 100)));

    if (!nowScoreLabel) {
      nowScoreLabel = document.createElement('p');
      nowScoreLabel.className = 'nowScore';
      lastRow.appendChild(nowScoreLabel);
    }
    nowScoreLabel.textContent = pct + '%';
  }
  // 기본값
  else {
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