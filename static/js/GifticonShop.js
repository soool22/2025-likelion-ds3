document.addEventListener("DOMContentLoaded", () => {
    const checkModal = document.getElementById("check-modal");
    const failModal = document.getElementById("fail-modal");

    const modalBoxCheck = checkModal.querySelector(".modal-box.check");
    const modalTitle = modalBoxCheck.querySelector(".modal-title");
    const modalSubtitle = modalBoxCheck.querySelector(".modal-subtitle");
    const modalDesc = modalBoxCheck.querySelector(".modal-desc");
    const confirmBtn = modalBoxCheck.querySelector(".confirm-btn");
    const cancelBtn = modalBoxCheck.querySelector(".cancel-btn");

    const modalBoxFail = failModal.querySelector(".modal-box.fail");
    const closeFailBtn = failModal.querySelector(".close-fail");

    let targetUrl = null;

    // ✅ 구매 가능 → 구매 확인 모달
    document.querySelectorAll(".buy-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();

            const name = btn.dataset.name;
            const cost = btn.dataset.cost;
            const remain = btn.dataset.remaining;

            modalTitle.innerHTML = `정말 기프티콘을 구매하시겠습니까?<br>가격: ${cost}P`;
            modalSubtitle.textContent = name;
            modalDesc.textContent = `(구매 후 잔여 포인트: ${remain}P)`;

            targetUrl = btn.href;

            checkModal.classList.remove("hidden");
            modalBoxCheck.classList.remove("hidden");
        });
    });

    confirmBtn.addEventListener("click", () => {
        if (targetUrl) {
            window.location.href = targetUrl;
        }
    });

    cancelBtn.addEventListener("click", () => {
        checkModal.classList.add("hidden");
        modalBoxCheck.classList.add("hidden");
    });

    checkModal.addEventListener("click", (e) => {
        if (e.target.classList.contains("modal-overlay")) {
            checkModal.classList.add("hidden");
            modalBoxCheck.classList.add("hidden");
        }
    });

    // ❌ 포인트 부족 → 실패 모달
    document.querySelectorAll(".not-enough").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();

            failModal.classList.remove("hidden");
            modalBoxFail.classList.remove("hidden");
        });
    });

    closeFailBtn.addEventListener("click", () => {
        failModal.classList.add("hidden");
        modalBoxFail.classList.add("hidden");
    });

    failModal.addEventListener("click", (e) => {
        if (e.target.classList.contains("modal-overlay")) {
            failModal.classList.add("hidden");
            modalBoxFail.classList.add("hidden");
        }
    });
});
