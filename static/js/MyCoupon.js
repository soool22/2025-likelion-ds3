// 조건 값 ("able", "disable", "confirmation" 중 하나)
let couponStatus = "confirmation"; // 테스트용

// 버튼 요소들
const otherBtns = document.querySelectorAll(".other-btn");

// 모달 부모 (오버레이)
const modalOverlay = document.querySelector(".modal-overlay");

// 모든 모달 요소
const modalAble = document.querySelector(".modal-box.able");
const modalDisable = document.querySelector(".modal-box.disable");
const modalConfirmation = document.querySelector(".modal-box.confirmation");

// 닫기 버튼들 (공통)
const modalBtns = document.querySelectorAll(".modal-btn");

// "쿠폰 사용하기" 버튼 눌렀을 때
otherBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        // 오버레이 열기
        modalOverlay.classList.remove("hidden");

        // 조건에 맞는 모달 열기
        if (couponStatus === "able") {
            modalAble.classList.remove("hidden");
        } else if (couponStatus === "disable") {
            modalDisable.classList.remove("hidden");
        } else if (couponStatus === "confirmation") {
            modalConfirmation.classList.remove("hidden");
        }
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


//range값 달라지는거
let rates = [70, 40, 90]; // %

  // 각각 적용
  document.querySelector('.yellow-range').style.width = rates[0] + "%";