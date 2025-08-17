(() => {
  const tabs = document.querySelectorAll(
    '.recommendstoreBox, .topBox, .reviewbestBox'
  );

  function setActiveTab(selected) {
    tabs.forEach(tab => {
      // active 제거
      tab.classList.remove('active');

      // 아이콘 src 원상복구
      const img = tab.querySelector('img');
      const originalSrc = img.getAttribute('src').replace('picked', '');
      img.setAttribute('src', originalSrc);
    });

    // 클릭된 탭만 active
    selected.classList.add('active');

    // 아이콘 src를 picked 버전으로 교체
    const icon = selected.querySelector('img');
    if (!icon.getAttribute('src').includes('picked')) {
      const pickedSrc = icon.getAttribute('src').replace('.svg', 'picked.svg');
      icon.setAttribute('src', pickedSrc);
    }
  }

  // 초기값: 첫 번째 탭 선택
  setActiveTab(tabs[0]);

  // 클릭 이벤트 등록
  tabs.forEach(tab => {
    tab.addEventListener('click', () => setActiveTab(tab));
  });
})();
    