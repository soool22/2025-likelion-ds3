document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const btn  = document.getElementById('btn');

  const titleInput   = document.getElementById('id_title');
  const descInput    = document.getElementById('id_description');
  const missionType  = document.getElementById('id_mission_type');
  const targetValue  = document.getElementById('id_target_value');

  const rewardType   = document.getElementById('id_reward_type');
  const rewardPoints = document.getElementById('id_reward_points');
  const rewardDesc   = document.getElementById('id_reward_description');

  const startDate    = document.getElementById('id_start_date');
  const endDate      = document.getElementById('id_end_date');

  const hasValue = (el) => !!el && String(el.value).trim() !== '';
  const closestBox = (el) => el ? el.closest('.box') : null;
  const markActive = (el, on) => {
    if (!el) return;
    el.classList.toggle('active', !!on);
    const b = closestBox(el);
    if (b) b.classList.toggle('active', !!on);
  };
  const keepDigits = (el) => {
    if (!el) return;
    const before = el.value;
    let digits = before.replace(/[^\d]/g, '');
    if (digits.length > 1) digits = String(parseInt(digits, 10) || '');
    if (before !== digits) el.value = digits;
  };

  /* === 여기만 핵심 수정 === */
  function syncRewardFields() {
    const t = rewardType.value; // '', 'POINT', 'CUSTOM'

    // 1) 전송되도록 둘 다 disabled 해제 (숨길 때는 CSS로)
    rewardPoints.disabled = false;
    rewardDesc.disabled   = false;

    if (t === 'POINT') {
      // 포인트 입력만 필수
      rewardPoints.required = true;
      rewardDesc.required   = false;

      // 직접입력값은 비워두고 숨김
      rewardDesc.value = '';
      rewardDesc.parentElement.style.display = '';   // 보이고싶으면 ''
      rewardDesc.style.display = 'none';            // 숨김
      rewardPoints.style.display = '';              // 표시

    } else if (t === 'CUSTOM') {
      // 직접입력만 필수
      rewardPoints.required = false;
      rewardDesc.required   = true;

      // 포인트는 0으로 전송되게 하고 숨김
      rewardPoints.value = '0';
      rewardPoints.style.display = 'none';          // 숨김
      rewardDesc.style.display = '';                // 표시

    } else {
      // 미선택일 때는 둘 다 보이게만 두고 필수 해제
      rewardPoints.required = false;
      rewardDesc.required   = false;
      rewardPoints.style.display = '';
      rewardDesc.style.display = '';
    }

    // 액티브 표시 갱신
    markActive(rewardPoints, hasValue(rewardPoints));
    markActive(rewardDesc, hasValue(rewardDesc));
    updateButton();
  }

  function updateButton() {
    const baseOk =
      hasValue(titleInput) &&
      hasValue(descInput) &&
      hasValue(targetValue) &&
      hasValue(startDate) &&
      hasValue(endDate) &&
      missionType.value !== '' &&
      rewardType.value  !== '';

    let rewardOk = false;
    if (rewardType.value === 'POINT') {
      rewardOk = hasValue(rewardPoints);
    } else if (rewardType.value === 'CUSTOM') {
      rewardOk = hasValue(rewardDesc);
    }

    const ok = baseOk && rewardOk;
    btn.classList.toggle('active', ok);
    btn.dataset.enabled = ok ? '1' : '0';
  }

  [titleInput, descInput].forEach(el => {
    el.addEventListener('input', () => { markActive(el, hasValue(el)); updateButton(); });
    markActive(el, hasValue(el));
  });
  missionType.addEventListener('change', () => { markActive(missionType, hasValue(missionType)); updateButton(); });
  targetValue.addEventListener('input', () => { keepDigits(targetValue); markActive(targetValue, hasValue(targetValue)); updateButton(); });

  rewardType.addEventListener('change', syncRewardFields);
  rewardPoints.addEventListener('input', () => { keepDigits(rewardPoints); markActive(rewardPoints, hasValue(rewardPoints)); updateButton(); });
  rewardDesc.addEventListener('input', () => { markActive(rewardDesc, hasValue(rewardDesc)); updateButton(); });

  [startDate, endDate].forEach(el => {
    el.addEventListener('input', () => { markActive(el, hasValue(el)); updateButton(); });
    markActive(el, hasValue(el));
  });

  // 초기 세팅
  syncRewardFields();
  updateButton();

  btn.addEventListener('click', (e) => {
    if (btn.dataset.enabled !== '1') {
      e.preventDefault();
      alert('필수 항목을 입력/선택해 주세요.');
      return;
    }
    // 최종 안전장치: CUSTOM이면 reward_points가 꼭 '0' 전송되게
    if (rewardType.value === 'CUSTOM' && (!rewardPoints.value || rewardPoints.value === '')) {
      rewardPoints.value = '0';
    }
    form.submit();
  });
});