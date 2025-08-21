document.addEventListener("DOMContentLoaded", () => {
    // review-box 안의 모든 a태그 가져오기
    const reviewLinks = document.querySelectorAll(".review-link");

    reviewLinks.forEach(link => {
        const btn = link.querySelector(".review-btn");

        // 처음에 disable이면 href 제거
        if (btn.classList.contains("disable")) {
            link.removeAttribute("href");
        }

        // 3초 뒤 조건 충족 시 (테스트용)
        setTimeout(() => {
            if (btn.classList.contains("disable")) {
                btn.classList.remove("disable");
                btn.classList.add("able");
                link.setAttribute("href", "./WriteReview.html");
            }
        }, 3000);
    });
});
