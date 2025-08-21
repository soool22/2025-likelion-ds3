const CERT_DONE_KEY = 'store_cert_done';

document.addEventListener('DOMContentLoaded', () => {
  // 1) 요소 참조
  const certBtn  = document.getElementById('certificationBtn');
  const reviewBtn = document.getElementById('reviewBtn');
  const aiBtn    = document.getElementById('aiBtn');
  const aiReview = document.getElementById('aiReview');

  // 2) 인증/리뷰 버튼 UI 적용 (요소가 있을 때만)
  function applyCertificationUI() {
    const done = sessionStorage.getItem(CERT_DONE_KEY) === '1';
    if (!certBtn || !reviewBtn) return; // 요소 없으면 그냥 종료

    if (done) {
      certBtn.style.display = 'none';
      reviewBtn.style.display = 'flex';
    } else {
      certBtn.style.display = 'flex';
      reviewBtn.style.display = 'none';
    }
  }
  applyCertificationUI();

  // 3) 인증 버튼 클릭 시 이동 (요소가 있을 때만)
  if (certBtn) {
    certBtn.addEventListener('click', () => {
      // 실제 경로로 교체하세요 (Django URL이면 템플릿에서 data-로 넘겨도 좋음)
      const CERT_PAGE_URL = '../html/CertificationPage.html';
      window.location.href = CERT_PAGE_URL;
      // 돌아왔을 때 review로 바꾸고 싶다면, 인증 완료 시점에 아래 값을 '1'로 저장하도록 구현
      // sessionStorage.setItem(CERT_DONE_KEY, '1');
    });
  }

  // 4) AI 요약 토글
  if (aiBtn && aiReview) {
    aiBtn.addEventListener('click', () => {
      aiBtn.style.display = 'none';
      aiReview.style.display = 'flex';
      aiReview.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }
});