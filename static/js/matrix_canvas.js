/**
 * Matrix-style canvas animation — падающие 0 и 1
 * Очень сдержанно, opacity ~0.1–0.15
 */
(function () {
  const canvas = document.getElementById("matrix-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const chars = "01";
  const fontSize = 14;
  const columns = Math.ceil(window.innerWidth / fontSize);
  const drops = Array(columns).fill(1);

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function draw() {
    ctx.fillStyle = "rgba(35, 40, 45, 0.08)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "rgba(255, 255, 255, 0.12)";
    ctx.font = `${fontSize}px monospace`;

    for (let i = 0; i < drops.length; i++) {
      const char = chars[Math.floor(Math.random() * chars.length)];
      const x = i * fontSize;
      const y = drops[i] * fontSize;

      ctx.fillText(char, x, y);

      if (y > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i] += 0.5;
    }
  }

  resize();
  window.addEventListener("resize", resize);

  setInterval(draw, 80);
})();
