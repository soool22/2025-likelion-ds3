const idInput = document.getElementById('id');
const emailInput = document.getElementById('email');
const nicknameInput = document.getElementById('nickname');
const pwInput = document.getElementById('repassword');   // "비밀번호 입력"
const pwConfirmInput = document.getElementById('password'); // "비밀번호 확인"
const btn = document.getElementById('btn');
const form = document.querySelector('form'); // 필요 시 사용

function toggleInputActive(el) {
  el.classList.toggle('active', el.value.trim().length > 0);
}

function isEmailValid() {
  // type="email"의 내장 검사 사용
  return emailInput.value.trim().length > 0 && emailInput.checkValidity();
}

function isIdValid() { return idInput.value.trim().length >= 1; }
function isNicknameValid() { return nicknameInput.value.trim().length >= 1; }
function isPwValid() { return pwInput.value.length >= 8; }
function isPwMatch() {
  return pwConfirmInput.value.length > 0 && pwConfirmInput.value === pwInput.value;
}

function updateUI() {
  // 입력 유무에 따라 각 인풋에 .active 토글
  [idInput, emailInput, nicknameInput, pwInput, pwConfirmInput].forEach(toggleInputActive);

  // 전체 유효성
  const allValid = isIdValid() && isEmailValid() && isNicknameValid() && isPwValid() && isPwMatch();

  // 버튼 상태
  btn.classList.toggle('active', allValid);
  btn.disabled = !allValid;
}

// 입력 이벤트 바인딩
[idInput, emailInput, nicknameInput, pwInput, pwConfirmInput].forEach(el => {
  el.addEventListener('input', updateUI);
});

// 초기 상태 반영
updateUI();