// var container = document.getElementById('map');
// 		var options = {
// 			center: new kakao.maps.LatLng(33.450701, 126.570667),
// 			level: 3
// 		};

// 		var map = new kakao.maps.Map(container, options);


(() => {
  const sheet  = document.getElementById('sheet');
  const handle = document.getElementById('sheetHandle'); // 있어도 무방
  const body   = sheet.querySelector('.sheet-body');

  const vh = () => window.innerHeight;
  const COLLAPSED_VISIBLE = 120;
  const TOP_GAP_RATIO = 0.18;

  let currentY = 0;
  let dragging = false;
  let startY = 0;
  let startYPos = 0;

  function bounds() {
    const h = sheet.getBoundingClientRect().height;
    const topGap = Math.round(vh() * TOP_GAP_RATIO);
    const visibleWhenExpanded = Math.max(vh() - topGap, 0);
    const minY = Math.max(h - visibleWhenExpanded, 0);
    const maxY = Math.max(h - COLLAPSED_VISIBLE, 0);
    return { minY, maxY };
  }

  function setY(y, withTransition = false) {
    const { minY, maxY } = bounds();
    currentY = Math.min(Math.max(y, minY), maxY);
    if (withTransition) sheet.style.transition = 'transform .22s ease-out';
    sheet.style.transform = `translateY(${currentY}px)`;
    if (withTransition) setTimeout(() => (sheet.style.transition = ''), 240);
  }

  function snap() {
    const { minY, maxY } = bounds();
    const mid = (minY + maxY) / 2;
    setY(currentY < mid ? minY : maxY, true);
  }

  function shouldStartDragFrom(target) {
    // 시트 안에서 시작했는지
    if (!sheet.contains(target)) return false;

    // sheet-body 위에서 시작했고, 내용이 스크롤 가능하며 현재 스크롤이 위가 아니면 드래그 시작하지 않음
    const inBody = target.closest('.sheet-body');
    if (inBody) {
      const canScroll = body.scrollHeight > body.clientHeight;
      if (canScroll && body.scrollTop > 0) return false;
    }
    // 버튼/입력 등 드래그 비활성화하고 싶으면 data-no-drag로 예외 처리 가능
    if (target.closest('[data-no-drag]')) return false;

    return true;
  }

  function onPointerDown(e) {
    if (!shouldStartDragFrom(e.target)) return;

    dragging = true;
    startY = e.clientY;
    startYPos = currentY;

    // 드래그 동안 내부 스크롤/클릭 막기
    body.style.pointerEvents = 'none';
    sheet.setPointerCapture?.(e.pointerId);

    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp, { once: true });
  }

  function onPointerMove(e) {
    if (!dragging) return;
    const dy = e.clientY - startY;
    setY(startYPos + dy);
  }

  function onPointerUp(e) {
    dragging = false;
    body.style.pointerEvents = '';
    sheet.releasePointerCapture?.(e.pointerId);
    window.removeEventListener('pointermove', onPointerMove);
    snap();
  }

  function init() {
    const { maxY } = bounds();
    setY(maxY, false);
  }

  // ✅ 핸들이 아니라 시트 전체에서 드래그 시작
  sheet.addEventListener('pointerdown', onPointerDown);

  window.addEventListener('resize', () => {
    const { minY, maxY } = bounds();
    const mid = (minY + maxY) / 2;
    setY(currentY < mid ? minY : maxY, false);
  });

  body.style.webkitOverflowScrolling = 'touch';
  init();
})();


const starIcon = document.getElementById("starIcon");

  starIcon.addEventListener("click", () => {
    if (starIcon.src.includes("star.svg")) {
      starIcon.src = "../img/starpicked.svg"; // 클릭 시 선택된 별로 변경
    } else {
      starIcon.src = "../img/star.svg"; // 다시 클릭하면 원래 별로 변경
    }
  });

  document.addEventListener('DOMContentLoaded', function() {
  const searchIcon = document.getElementById('searchIcon');
  const searchBtn = document.getElementById('searchBtn');

  if (searchIcon && searchBtn) {
    searchIcon.addEventListener('click', () => {
      searchBtn.click();   // 아이콘 누르면 버튼 클릭 이벤트 실행
    });
  }
});