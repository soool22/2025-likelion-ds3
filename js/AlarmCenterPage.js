document.querySelectorAll('#alarmChoose').forEach((wrap) => {
  const offBtn = wrap.querySelector('.switchBtn:not(.picked)');
  const onBtn  = wrap.querySelector('.switchBtn.picked');

  function show(on) {
    onBtn.style.display  = on ? 'flex' : 'none';
    offBtn.style.display = on ? 'none' : 'flex';
  }

  show(getComputedStyle(onBtn).display !== 'none');

  function toggle() {
    show(getComputedStyle(onBtn).display === 'none');
  }

  offBtn.addEventListener('click', toggle);
  onBtn.addEventListener('click', toggle);
});