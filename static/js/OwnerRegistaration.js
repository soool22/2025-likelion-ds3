document.addEventListener('DOMContentLoaded', () => {
  const form        = document.querySelector('form');
  const submitBtn   = document.getElementById('btn');

  // 필수 입력 요소들
  const nameInput   = document.querySelector('input.inputBox[placeholder="가게 이름"]');
  const addrInput   = document.querySelector('#searchBox .search'); // 주소
  const guInput     = document.querySelector('input.inputBox[placeholder="구 이름"]');
  const phoneInput  = document.querySelector('input.inputBox[placeholder="가게 전화"]');
  const ownerCode   = document.querySelector('input.inputBox[placeholder="점주 코드"]');
  const openBox     = document.querySelectorAll('.box')[1]; // 오픈 시간 box
  const closeBox    = document.querySelectorAll('.box')[2]; // 마감 시간 box
  const openTime    = openBox.querySelector('.timeStyle');
  const closeTime   = closeBox.querySelector('.timeStyle');
  const categoryBox = document.querySelectorAll('.box')[0]; // 카테고리 박스
  const categoryCbs = categoryBox.querySelectorAll('input[type="checkbox"]');

  // ---- 공통: 값 있으면 .active, 없으면 제거 ----
  function updateActiveClass(el, wrapperBox=null) {
    if (!el) return;
    const hasValue = (el.type === 'checkbox')
      ? el.checked
      : (el.value || '').trim().length > 0;

    if (hasValue) {
      el.classList.add('active');
      if (wrapperBox) wrapperBox.classList.add('active');
    } else {
      el.classList.remove('active');
      if (wrapperBox) {
        // wrapper 안의 모든 input이 비었을 때만 .active 해제
        const anyFilled = [...wrapperBox.querySelectorAll('input')].some(input => {
          if (input.type === 'checkbox') return input.checked;
          return input.value.trim() !== "";
        });
        if (!anyFilled) wrapperBox.classList.remove('active');
      }
    }
  }

  // ---- 이벤트 바인딩 ----
  [nameInput, addrInput, guInput, phoneInput, ownerCode].forEach(el => {
    if (!el) return;
    updateActiveClass(el, el.closest('.box'));
    el.addEventListener('input', () => { updateActiveClass(el, el.closest('.box')); updateSubmitState(); });
    el.addEventListener('focus', () => el.classList.add('active'));
    el.addEventListener('blur',  () => updateActiveClass(el, el.closest('.box')));
  });

  [ [openTime, openBox], [closeTime, closeBox] ].forEach(([el, box]) => {
    if (!el) return;
    updateActiveClass(el, box);
    el.addEventListener('change', () => { updateActiveClass(el, box); updateSubmitState(); });
  });

  categoryCbs.forEach(cb => {
    cb.addEventListener('change', () => {
      categoryCbs.forEach(c => updateActiveClass(c, categoryBox));
      updateSubmitState();
    });
    updateActiveClass(cb, categoryBox);
  });

  // ---- 유효성 검사 ----
  function isAnyCategoryChecked() {
    return Array.from(categoryCbs).some(cb => cb.checked);
  }

  function isFormValid() {
    return (
      nameInput.value.trim() &&
      addrInput.value.trim() &&
      guInput.value.trim() &&
      phoneInput.value.trim() &&
      ownerCode.value.trim() &&
      openTime.value &&
      closeTime.value &&
      isAnyCategoryChecked()
    );
  }

  // ---- 버튼 상태 ----
  function updateSubmitState() {
    if (isFormValid()) {
      submitBtn.classList.add('active');
      submitBtn.disabled = false;
    } else {
      submitBtn.classList.remove('active');
      submitBtn.disabled = true;
    }
  }
  updateSubmitState();

  // ---- 제출 처리 ----
  submitBtn.addEventListener('click', (e) => {
    e.preventDefault();
    if (!isFormValid()) {
      alert('필수 정보를 모두 입력해 주세요.');
      return;
    }
    form.submit();
  });
});
