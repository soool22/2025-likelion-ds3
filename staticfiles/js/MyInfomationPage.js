document.addEventListener("DOMContentLoaded", () => {
  const achievementBoxes = document.querySelectorAll(".achievementBox");

  achievementBoxes.forEach(box => {
    const nowScoreEl = box.querySelector(".nowScore");
    const totalScoreEl = box.querySelector(".totalScore");
    const achievementEl = box.querySelector(".achievement");

    if (nowScoreEl && totalScoreEl && achievementEl) {
      // 문자열에서 숫자만 추출 (/3 같은 경우 대비)
      const now = parseInt(nowScoreEl.textContent.trim());
      const total = parseInt(totalScoreEl.textContent.replace("/", "").trim());

      if (!isNaN(now) && !isNaN(total) && total > 0) {
        const percent = (now / total) * 100;
        achievementEl.style.width = percent + "%";
      }
    }
  });
});