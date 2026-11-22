from flask import Flask, request, jsonify, render_template_string
import os

import requests

API_URL = "https://api.siputzx.my.id/api/ai/deepseekr1"
DEFAULT_SYSTEM = "gunakan bahasa Indonesia"

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tanya AI</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 680px; margin: 40px auto; padding: 0 16px; }
    h1 { font-size: 1.5rem; }
    textarea { width: 100%; height: 100px; padding: 8px; box-sizing: border-box; }
    button { margin-top: 8px; padding: 8px 16px; cursor: pointer; }
    #answer { white-space: pre-wrap; margin-top: 20px; padding: 12px; background: #f4f4f4; border-radius: 8px; min-height: 40px; }
  </style>
</head>
<body>
  <h1>Tanya AI</h1>
  <textarea id="prompt" placeholder="Tulis pertanyaanmu..."></textarea>
  <br>
  <button id="send">Kirim</button>
  <div id="answer"></div>

  <script>
    const btn = document.getElementById("send");
    const promptEl = document.getElementById("prompt");
    const answerEl = document.getElementById("answer");

    btn.addEventListener("click", async () => {
      const prompt = promptEl.value.trim();
      if (!prompt) return;
      btn.disabled = true;
      answerEl.textContent = "Sedang berpikir...";
      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt })
        });
        const data = await res.json();
        answerEl.textContent = data.answer || ("Error: " + (data.error || "tidak diketahui"));
      } catch (e) {
        answerEl.textContent = "Gagal menghubungi server.";
      } finally {
        btn.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True) or {}
    prompt = (body.get("prompt") or "").strip()
    if not prompt:
        return jsonify(error="Prompt tidak boleh kosong"), 400

    try:
        r = requests.get(
            API_URL,
            params={"prompt": prompt, "system": DEFAULT_SYSTEM, "temperature": 0.7},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("status"):
            return jsonify(error="Layanan AI mengembalikan error"), 502
        return jsonify(answer=data["data"]["response"])
    except requests.RequestException:
        return jsonify(error="Gagal terhubung ke layanan AI"), 502
    except (ValueError, KeyError):
        return jsonify(error="Format respons tidak valid"), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
