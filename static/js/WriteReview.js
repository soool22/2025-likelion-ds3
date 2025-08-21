document.addEventListener("DOMContentLoaded", () => {
    // 음식 평가 별점
    setupStarRating(".evaluation-food-star", 5, "star", "y-star");
    // 서비스 평가 별점
    setupStarRating(".evaluation-service-star", 5, "s-star", "s-y-star");
});

/**
 * 별점 클릭 기능
 * @param {string} containerSelector - 별들이 들어있는 부모 div
 * @param {number} count - 별 개수
 * @param {string} normalClass - 흰 별 class prefix
 * @param {string} yellowClass - 노란 별 class prefix
 */
function setupStarRating(containerSelector, count, normalClass, yellowClass) {
    const container = document.querySelector(containerSelector);

    for (let i = 1; i <= count; i++) {
        const normalStar = container.querySelector(`.${normalClass}${i}`);
        const yellowStar = container.querySelector(`.${yellowClass}${i}`);

        normalStar.addEventListener("click", () => updateStars(i));
        yellowStar.addEventListener("click", () => updateStars(i));
    }

    function updateStars(index) {
        for (let i = 1; i <= count; i++) {
            const normalStar = container.querySelector(`.${normalClass}${i}`);
            const yellowStar = container.querySelector(`.${yellowClass}${i}`);

            if (i <= index) {
                normalStar.style.display = "none";
                yellowStar.style.display = "inline-block";
            } else {
                normalStar.style.display = "inline-block";
                yellowStar.style.display = "none";
            }
        }
    }
}
