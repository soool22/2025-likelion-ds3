const CERT_DONE_KEY = 'store_cert_done';

document.addEventListener('DOMContentLoaded', () => {
  // 1) 요소 참조
  // const certBtn  = document.getElementById('certificationBtn');
  // const reviewBtn = document.getElementById('reviewBtn');
  const aiBtn    = document.getElementById('aiBtn');
  const aiReview = document.getElementById('aiReview');

//   // 2) 인증/리뷰 버튼 UI 적용 (요소가 있을 때만)
//   function applyCertificationUI() {
//     const done = sessionStorage.getItem(CERT_DONE_KEY) === '1';
//     if (!certBtn || !reviewBtn) return; // 요소 없으면 그냥 종료

//     if (done) {
//       certBtn.style.display = 'none';
//       reviewBtn.style.display = 'flex';
//     } else {
//       certBtn.style.display = 'flex';
//       reviewBtn.style.display = 'none';
//     }
//   }
//   applyCertificationUI();

//   // 3) 인증 버튼 클릭 시 이동 (요소가 있을 때만)
//   if (certBtn) {
//   certBtn.addEventListener('click', () => {
//     if (window.CERT_PAGE_URL) window.location.href = window.CERT_PAGE_URL;
//   });
// }


  // 4) AI 요약 토글
  if (aiBtn && aiReview) {
    aiBtn.addEventListener('click', () => {
      aiBtn.style.display = 'none';
      aiReview.style.display = 'flex';
      aiReview.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }
});