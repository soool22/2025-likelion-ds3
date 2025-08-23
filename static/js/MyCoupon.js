document.addEventListener("DOMContentLoaded", function() {
    const overlay = document.querySelector(".modal-overlay");
    const secretModal = document.querySelector(".modal-box.secret");
    const ableModal = document.querySelector(".modal-box.able");
    const disableModal = document.querySelector(".modal-box.disable");
    const confirmationModal = document.querySelector(".modal-box.confirmation");
    const secretInput = document.getElementById("secretInput");

    const confirmBtn = secretModal.querySelector(".confirm-btn");
    const cancelBtn = secretModal.querySelector(".cancel-btn");

    let currentCouponId = null;

    function showModal(modal) {
        overlay.classList.remove("hidden");
        modal.classList.remove("hidden");
    }

    function closeModals() {
        overlay.classList.add("hidden");
        document.querySelectorAll(".modal-box").forEach(m => m.classList.add("hidden"));
        secretInput.value = "";
        currentCouponId = null;
    }

    

    // 닫기 버튼 이벤트
    cancelBtn.addEventListener("click", closeModals);
    document.querySelectorAll(".close-btn").forEach(btn => btn.addEventListener("click", closeModals));

    // ✅ 쿠폰 사용 버튼 이벤트 등록
    document.querySelectorAll("button.use-coupon-btn[data-id]").forEach(function(btn) {
        btn.addEventListener("click", function(e) {
            e.preventDefault(); // 새로고침 방지
            console.log("쿠폰 버튼 클릭됨", this.dataset.id); // 디버그 확인
            currentCouponId = this.dataset.id;
            showModal(secretModal);
        });
    });

    // ✅ 확인 버튼
    confirmBtn.addEventListener("click", function() {
        const secretCode = secretInput.value.trim();
        if (!secretCode || !currentCouponId) return;

        fetch("{% url 'coupons:use_coupon' %}", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": "{{ csrf_token }}"
            },
            body: JSON.stringify({ coupon_id: currentCouponId, secret_code: secretCode })
        })
        .then(res => res.json())
        .then(data => {
            closeModals();
            if (data.success) {
                showModal(ableModal);
                // 성공 시 해당 쿠폰 박스 삭제
                document.querySelector(`button.use-coupon-btn[data-id="${currentCouponId}"]`)
                        ?.closest(".box").remove();
            } else {
                showModal(disableModal);
            }
        })
        .catch(err => {
            closeModals();
            console.error("서버 오류:", err);
            alert("서버 통신 오류가 발생했습니다.");
        });
    });
});
