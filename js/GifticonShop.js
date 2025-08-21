// 버튼 요소들
const otherBtns = document.querySelectorAll(".gifticon-back");

// 모달 부모 (오버레이)
const modalOverlay = document.querySelector(".modal-overlay");

// 모든 모달 요소
const modalAble = document.querySelector(".modal-box.able");


// 닫기 버튼들 (공통)
const modalBtns = document.querySelectorAll(".modal-btn");

// "쿠폰 사용하기" 버튼 눌렀을 때
otherBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        // 오버레이 열기
        modalOverlay.classList.remove("hidden");

        
        modalAble.classList.remove("hidden");
    });
});

// 모달 내부 "확인" 버튼 누르면 닫기
modalBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        modalOverlay.classList.add("hidden");
        modalAble.classList.add("hidden");
        modalDisable.classList.add("hidden");
        modalConfirmation.classList.add("hidden");
    });
});
