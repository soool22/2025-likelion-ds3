document.addEventListener("DOMContentLoaded", () => {
  // 🔹 열기 버튼들
  document.querySelector(".account-arrow1")?.addEventListener("click", () => {
    document.querySelector(".nick-name")?.classList.remove("hidden");
  });

  document.querySelector(".account-arrow2")?.addEventListener("click", () => {
    document.querySelector(".email")?.classList.remove("hidden");
  });

  document.querySelector(".account-arrow3")?.addEventListener("click", () => {
    document.querySelector(".num")?.classList.remove("hidden");
  });

  document.querySelector(".account-arrow4")?.addEventListener("click", () => {
    document.querySelector(".password")?.classList.remove("hidden");
  });

  // 🔹 닫기 버튼들 (X, back)
  // 1) 모든 팝업 안에 있는 X 이미지
  document.querySelectorAll(".nick-name .nick-name-tittle img, .num .num-tittle img").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.closest(".nick-name, .num")?.classList.add("hidden");
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
  const passwordInput = document.querySelector('input[name="password"]');
  const passwordCheckInput = document.querySelector('input[name="passwordcheck"]');
  const passwordCheckBtn = document.querySelector(".password-check-btn");

  function validatePasswordMatch() {
    if (passwordInput && passwordCheckInput && passwordCheckBtn) {
      if (passwordInput.value && passwordInput.value === passwordCheckInput.value) {
        passwordCheckBtn.style.display = "block"; // 버튼 보이기
      } else {
        passwordCheckBtn.style.display = "none";  // 버튼 숨기기
      }
    }
  }

  if (passwordInput && passwordCheckInput) {
    passwordInput.addEventListener("input", validatePasswordMatch);
    passwordCheckInput.addEventListener("input", validatePasswordMatch);
  }

  // ✅ "비밀번호 설정 완료" 버튼 클릭 시 팝업 닫기
  document.querySelectorAll(".password-check-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.closest(".password")?.classList.add("hidden");
    });
  });

  // 시작할 때 버튼 숨겨두기
  if (passwordCheckBtn) {
    passwordCheckBtn.style.display = "none";
  }
});


// 모든 toggle-btn에 이벤트 달기 (비밀번호 보이기/숨기기)
document.querySelectorAll(".toggle-btn").forEach(btn => {
  btn.addEventListener("click", function() {
    const input = this.parentElement.querySelector("input");
    if (input) {
      if (input.type === "password") {
        input.type = "text";   // 보이게
      } else {
        input.type = "password"; // 숨기기
      }
    }
  });
});
