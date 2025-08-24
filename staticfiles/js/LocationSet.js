document.addEventListener("DOMContentLoaded", () => {
  const searchIcon = document.getElementById("searchIcon");
  const realSearchBtn = document.querySelector(".realSearchBtn");

  if (searchIcon && realSearchBtn) {
    searchIcon.addEventListener("click", () => {
      realSearchBtn.click();   // 아이콘 클릭 → 숨겨진 버튼 클릭
    });
  }
});