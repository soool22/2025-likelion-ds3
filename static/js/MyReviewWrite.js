function setupStarRating(containerSelector, count, normalClass, yellowClass, hiddenInputId) {
    const container = document.querySelector(containerSelector);
    const hiddenInput = document.getElementById(hiddenInputId); // ⭐ 값 저장용 hidden input

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
        hiddenInput.value = index;  // ⭐ 해당 카테고리 점수 저장
        updateTotalRating();        // 합산 갱신
    }
}

function updateTotalRating() {
    const foodRating = parseInt(document.getElementById("food-rating").value) || 0;
    const serviceRating = parseInt(document.getElementById("service-rating").value) || 0;

    let total = 0;

    if (foodRating > 0 && serviceRating > 0) {
        total = (foodRating + serviceRating) / 2;   // ⭐ 평균
    } else if (foodRating > 0) {
        total = foodRating;   // 하나만 선택된 경우
    } else if (serviceRating > 0) {
        total = serviceRating;
    }

    document.getElementById("rating-input").value = Math.round(total); // 반올림 정수
}

