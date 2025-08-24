// 안전한 변수명으로 변경
const usernameInput = document.getElementById("id_username");
const passwordInput = document.getElementById("id_password");
const btn = document.getElementById("btn");

function check_idpw() {
  const IDlength = usernameInput.value.length;
  const pwlength = passwordInput.value.length;

  // 버튼 활성화/비활성
  if (IDlength >= 1 && pwlength >= 8) {
    btn.classList.add("active");
  } else {
    btn.classList.remove("active");
  }

  // 아이디 inputBox 활성화 여부
  if (IDlength >= 1) {
    usernameInput.classList.add("active");
  } else {
    usernameInput.classList.remove("active");
  }

  // 비밀번호 inputBox 활성화 여부
  if (pwlength >= 1) {
    passwordInput.classList.add("active");
  } else {
    passwordInput.classList.remove("active");
  }
}

// 입력 변화에 반응
usernameInput.addEventListener("input", check_idpw);
passwordInput.addEventListener("input", check_idpw);

// 초기 상태 세팅
check_idpw();