// ============================================================
// chatbot-widget.js — nút chat nổi góc phải, gọi ChatbotApi.ask()
// Yêu cầu: đã load js/api.js trước.
// ============================================================
(function () {
  function buildWidget() {
    const toggle = document.createElement("button");
    toggle.className = "chat-toggle";
    toggle.setAttribute("aria-label", "Trợ lý AI");
    toggle.innerHTML = "&#128172;";

    const panel = document.createElement("div");
    panel.className = "chat-panel";
    panel.innerHTML = `
      <div class="chat-panel-head">
        <span>Trợ lý Studio Phim</span>
        <button type="button" id="chat-close" aria-label="Đóng">&times;</button>
      </div>
      <div class="chat-messages" id="chat-messages">
        <div class="chat-msg bot">Chào bạn! Mình có thể gợi ý phòng, thiết bị hoặc gói dịch vụ phù hợp — cứ hỏi thoải mái nhé.</div>
      </div>
      <div class="chat-input-row">
        <input type="text" id="chat-input" placeholder="Nhập câu hỏi..." />
        <button type="button" id="chat-send">Gửi</button>
      </div>
    `;

    document.body.appendChild(toggle);
    document.body.appendChild(panel);

    const messages = panel.querySelector("#chat-messages");
    const input = panel.querySelector("#chat-input");
    const sendBtn = panel.querySelector("#chat-send");
    const closeBtn = panel.querySelector("#chat-close");

    function addMessage(text, who) {
      const div = document.createElement("div");
      div.className = `chat-msg ${who}`;
      div.textContent = text;
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
    }

    async function send() {
      const text = input.value.trim();
      if (!text) return;
      addMessage(text, "user");
      input.value = "";
      sendBtn.disabled = true;
      try {
        const res = await ChatbotApi.ask(text);
        addMessage(res.answer || "Xin lỗi, mình chưa có câu trả lời phù hợp.", "bot");
      } catch (err) {
        addMessage("Không kết nối được trợ lý lúc này, vui lòng thử lại sau.", "bot");
      } finally {
        sendBtn.disabled = false;
      }
    }

    toggle.addEventListener("click", () => panel.classList.toggle("open"));
    closeBtn.addEventListener("click", () => panel.classList.remove("open"));
    sendBtn.addEventListener("click", send);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") send();
    });
  }

  document.addEventListener("DOMContentLoaded", buildWidget);
})();
