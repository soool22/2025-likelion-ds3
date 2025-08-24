// (() => {
//   const tabs = document.querySelectorAll(
//     '.recommendstoreBox, .topBox, .reviewbestBox'
//   );

//   // 더보기 <a> 요소 (버튼을 감싸고 있는 앵커를 잡음)
//   const plusLink = document.getElementById('plusBtn')?.closest('a');

//   // 탭 → 이동할 페이지 매핑(파일명은 네 프로젝트에 맞게 바꿔줘)
//   const ROUTES = {
//     recommend: '../html/RecommendStorePage.html',
//     top: '../html/Top100Page.html',
//     review: '../html/ReviewBestPage.html',
//   };

//   function tabKey(el) {
//     if (el.classList.contains('recommendstoreBox')) return 'recommend';
//     if (el.classList.contains('topBox'))           return 'top';
//     return 'review'; // reviewbestBox
//   }

//   function setActiveTab(selected) {
//     tabs.forEach(tab => {
//       tab.classList.remove('active');
//       const img = tab.querySelector('img');
//       const originalSrc = img.getAttribute('src').replace('picked', '');
//       img.setAttribute('src', originalSrc);
//     });

//     selected.classList.add('active');

//     const icon = selected.querySelector('img');
//     if (!icon.getAttribute('src').includes('picked')) {
//       const pickedSrc = icon.getAttribute('src').replace('.svg', 'picked.svg');
//       icon.setAttribute('src', pickedSrc);
//     }

//     // 여기서 더보기 링크 갱신!
//     if (plusLink) {
//       const key = tabKey(selected);
//       plusLink.href = ROUTES[key] || '#';
//     }
//   }

//   // 초기값: 첫 번째 탭 선택 + 더보기 링크 세팅
//   setActiveTab(tabs[0]);

//   // 클릭 이벤트 등록
//   tabs.forEach(tab => {
//     tab.addEventListener('click', () => setActiveTab(tab));
//   });
// })();