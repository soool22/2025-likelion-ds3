// StoreDetailPage.js

const starImg = document.getElementById('star');
const keepBtn = document.getElementById('keep'); // 찜하기 버튼(화면에는 숨김)
const certBtn = document.getElementById('certificationBtn');
const reviewBtn = document.getElementById('reviewBtn');

// 이미지 경로
const STAR_DEFAULT_SRC = '../img/star.svg';
const STAR_PICKED_SRC  = '../img/starpicked.svg';

// ---------- 1) 별(찜) 토글 ----------
function setStarPicked(picked) {
  starImg.src = picked ? STAR_PICKED_SRC : STAR_DEFAULT_SRC;
  sessionStorage.setItem('store_star_picked', picked ? '1' : '0');

  // keep 버튼 눌림/해제 동작 실행
  try {
    keepBtn.dispatchEvent(new Event('click', { bubbles: true }));
  } catch {
    keepBtn.click();
  }
}

starImg.addEventListener('click', () => {
  const picked = sessionStorage.getItem('store_star_picked') === '1';
  // ⭐ 토글
  setStarPicked(!picked);
});

// ---------- 2) 인증 버튼 & 리뷰 버튼 ----------
const CERT_DONE_KEY = 'store_cert_done';

function applyCertificationUI() {
  const done = sessionStorage.getItem(CERT_DONE_KEY) === '1';
  if (done) {
    certBtn.style.display = 'none';
    reviewBtn.style.display = 'flex';
  } else {
    certBtn.style.display = 'flex';
    reviewBtn.style.display = 'none';
  }
}
applyCertificationUI();

certBtn.addEventListener('click', () => {
  // 실제 인증 페이지 경로로 바꿔야 함
  const CERT_PAGE_URL = '../html/CertificationPage.html';
  window.location.href = CERT_PAGE_URL;
});

// ---------- 3) 초기 별 상태 반영 ----------
(function initStarFromSession() {
  const saved = sessionStorage.getItem('store_star_picked');
  if (saved === null) {
    // ⭐ 기본은 항상 star.svg
    starImg.src = STAR_DEFAULT_SRC;
    sessionStorage.setItem('store_star_picked', '0');
  } else {
    const picked = saved === '1';
    starImg.src = picked ? STAR_PICKED_SRC : STAR_DEFAULT_SRC;
  }
})();
