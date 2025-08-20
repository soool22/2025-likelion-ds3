document.querySelectorAll('.stop-icon').forEach((wrap) => {
  const offBtn = wrap.querySelector('.switchBtn:not(.picked)');
  const onBtn  = wrap.querySelector('.switchBtn.picked');

  function show(on) {
    onBtn.style.display  = on ? 'flex' : 'none';
    offBtn.style.display = on ? 'none' : 'flex';
  }

  show(getComputedStyle(onBtn).display !== 'none');

  function toggle() {
    show(getComputedStyle(onBtn).display === 'none');
  }

  offBtn.addEventListener('click', toggle);
  onBtn.addEventListener('click', toggle);
});

//창 화면 전환
document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".bar .my-review");
  const storeInfo = document.querySelector(".store-info");
  const storeStatistics = document.querySelector(".store-statistics");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      // 1. 모든 탭 picked 해제
      tabs.forEach((t) => t.classList.remove("picked"));

      // 2. 클릭된 탭 picked 추가
      tab.classList.add("picked");

      // 3. 탭 텍스트로 구분해서 해당 영역 보여주기
      if (tab.textContent.trim() === "매장 정보") {
        storeInfo.style.display = "block";
        storeStatistics.style.display = "none";
      } else if (tab.textContent.trim() === "매장 통계") {
        storeInfo.style.display = "none";
        storeStatistics.style.display = "block";
      }
    });
  });
});

//range값 달라지는거
let rates = [70, 40, 90]; // %

  // 각각 적용
  document.querySelector('.yellow-range1').style.width = rates[0] + "%";
  document.querySelector('.yellow-range2').style.width = rates[1] + "%";
  document.querySelector('.yellow-range3').style.width = rates[2] + "%";