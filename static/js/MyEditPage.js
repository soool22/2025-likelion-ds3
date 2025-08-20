document.addEventListener("DOMContentLoaded", () => {
  // 🔹 열기 버튼들
  document.querySelector(".account-arrow1")?.addEventListener("click", () => {
    document.querySelector(".nick-name")?.classList.remove("hidden");
  });

  document.querySelector(".account-arrow2")?.addEventListener("click", () => {
    document.querySelector(".email")?.classList.remove("hidden");
  });

  document.querySelector(".account-arrow3")?.addEventListener("click", () => {
    document.querySelector(".certification")?.classList.remove("hidden");
  });

  document.querySelector(".account-arrow4")?.addEventListener("click", () => {
    document.querySelector(".password")?.classList.remove("hidden");
  });

  // 🔹 닫기 버튼들 (X, back)
  // 1) 모든 팝업 안에 있는 X 이미지
  document.querySelectorAll(".nick-name .nick-name-tittle img, .certification .certification-tittle img").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.closest(".nick-name, .certification")?.classList.add("hidden");
    });
  });

  // 2) 이메일 팝업, 비밀번호 팝업의 back 버튼
  document.querySelectorAll(".email .back, .password .back").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.closest(".email, .password")?.classList.add("hidden");
    });
  });
});



document.addEventListener("DOMContentLoaded", () => {
  // ✅ 인증하기 버튼 클릭 이벤트
  const passwordBtn = document.querySelector(".password-btn");
  const passwordCheckBtn = document.querySelector(".password-check-btn");

  if (passwordBtn && passwordCheckBtn) {
    passwordBtn.addEventListener("click", () => {
      // 🔹 여기에 실제 인증 성공 로직이 들어가야 함
      const isSuccess = true; // 지금은 테스트용으로 무조건 성공

      if (isSuccess) {
        // 클래스 추가해서 색상 변경
        passwordCheckBtn.classList.add("active");
      }
    });
  }
  document.querySelectorAll(".password-check-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.closest(".password")?.classList.add("hidden");
    });
  });
});
