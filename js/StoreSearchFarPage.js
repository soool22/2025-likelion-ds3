// var container = document.getElementById('map');
// 		var options = {
// 			center: new kakao.maps.LatLng(33.450701, 126.570667),
// 			level: 3
// 		};

// 		var map = new kakao.maps.Map(container, options);


(() => {
  const sheet  = document.getElementById('sheet');
  const handle = document.getElementById('sheetHandle');
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

  function onPointerDown(e) {
    dragging = true;
    startY = e.clientY;
    startYPos = currentY;
    body.style.pointerEvents = 'none';
    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp, { once: true });
  }

  function onPointerMove(e) {
    if (!dragging) return;
    const dy = e.clientY - startY;
    setY(startYPos + dy);
  }

  function onPointerUp() {
    dragging = false;
    body.style.pointerEvents = '';
    window.removeEventListener('pointermove', onPointerMove);
    snap();
  }

  function init() {
    const { maxY } = bounds();
    setY(maxY, false);
  }

  handle.addEventListener('pointerdown', onPointerDown);

  window.addEventListener('resize', () => {
    const { minY, maxY } = bounds();
    const mid = (minY + maxY) / 2;
    setY(currentY < mid ? minY : maxY, false);
  });

  body.style.webkitOverflowScrolling = 'touch';

  init();
})();