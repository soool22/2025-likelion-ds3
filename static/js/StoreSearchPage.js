// var container = document.getElementById('map');
// 		var options = {
// 			center: new kakao.maps.LatLng(33.450701, 126.570667),
// 			level: 3
// 		};

// 		var map = new kakao.maps.Map(container, options);


(() => {
  const sheet  = document.getElementById('sheet');
  const body   = sheet.querySelector('.sheet-body');

  const vh = () => window.innerHeight;
  const COLLAPSED_VISIBLE = 120;
  const TOP_GAP_RATIO = 0.18;

  let currentY = 0;

  // 👇 추가: 드래그 임계치
  const DRAG_THRESHOLD = 8;     // px
  let dragging = false;         // 실제 드래그 중인지
  let maybeDrag = false;        // 드래그 후보 상태
  let startY = 0;
  let startYPos = 0;
  let lastPointerId = null;
  let moved = false;            // 포인터가 움직였는지(클릭 구분용)

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

  function canStartFrom(target) {
    if (!sheet.contains(target)) return false;
    const inBody = target.closest('.sheet-body');
    // body 안에서 시작했고 스크롤이 위가 아니면(= 스크롤 우선) 드래그 시작 안 함
    if (inBody) {
      const canScroll = body.scrollHeight > body.clientHeight;
      if (canScroll && body.scrollTop > 0) return false;
    }
    // 드래그 금지 영역
    if (target.closest('a, button, input, textarea, [data-no-drag]')) return false;
    return true;
  }

  function onPointerDown(e) {
    if (!canStartFrom(e.target)) {
      dragging = false;
      maybeDrag = false;
      return;
    }
    maybeDrag = true;   // 아직 ‘클릭’일 수도, ‘드래그’일 수도
    dragging = false;
    moved = false;
    startY = e.clientY;
    startYPos = currentY;
    lastPointerId = e.pointerId;
    // ❌ 여기서 pointerEvents를 끄지 않습니다(클릭 살리기)
    sheet.addEventListener('pointermove', onPointerMove);
    sheet.addEventListener('pointerup', onPointerUp, { once: true });
  }

  function onPointerMove(e) {
    moved = true;
    if (!maybeDrag && !dragging) return;

    const dy = e.clientY - startY;

    // 임계치 넘기 전이면 클릭으로 놔둠
    if (!dragging) {
      if (Math.abs(dy) < DRAG_THRESHOLD) return;

      // 👉 여기서부터 ‘진짜 드래그’ 시작
      dragging = true;
      // 드래그 중에만 내부 클릭/스크롤 차단
      body.style.pointerEvents = 'none';
      sheet.setPointerCapture?.(lastPointerId ?? e.pointerId);
    }

    setY(startYPos + dy);
  }

  function onPointerUp(e) {
    // 드래그 중이면 스냅 + 차단 해제
    if (dragging) {
      dragging = false;
      body.style.pointerEvents = '';
      sheet.releasePointerCapture?.(lastPointerId ?? e.pointerId);
      snap();

      // 드래그가 있었으면 아래 클릭을 막아 클릭-탭 오작동 방지
      sheet.addEventListener(
        'click',
        (ev) => ev.stopPropagation(),
        { capture: true, once: true }
      );
    }

    maybeDrag = false;
    sheet.removeEventListener('pointermove', onPointerMove);
  }

  function init() {
    const { maxY } = bounds();
    setY(maxY, false);
  }

  // ✅ 이제 시트 전체에서 제스처 시작
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