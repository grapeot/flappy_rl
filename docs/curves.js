// 训练曲线绘制 —— 从 metrics.json 在一张 Canvas 上画两条线：
//   - reward（被优化的东西，滑动平均）
//   - score = 过管数（task metric，我们真正想要的东西，滑动平均）
//
// 把两者画在一起，是为了直观看出它们是否同步上升。若 reward 涨而 score 不涨，
// 就是 reward hacking 的 signature（见 docs/concepts.md）。两条线用各自的 y 轴量纲，
// 但都归一化到画布高度，只看"形状是否一致"。

(function () {
  "use strict";

  function movingAvg(arr, win) {
    const out = [];
    let sum = 0;
    const q = [];
    for (const v of arr) {
      q.push(v);
      sum += v;
      if (q.length > win) sum -= q.shift();
      out.push(sum / q.length);
    }
    return out;
  }

  function drawLine(ctx, xs, ys, x0, y0, w, h, vmin, vmax, color) {
    const tmin = xs[0], tmax = xs[xs.length - 1] || 1;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < xs.length; i++) {
      const px = x0 + ((xs[i] - tmin) / (tmax - tmin || 1)) * w;
      const py = y0 + h - ((ys[i] - vmin) / (vmax - vmin || 1)) * h;
      i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
    }
    ctx.stroke();
  }

  // 在给定 canvas 上画一份 metrics 的双线图
  window.drawCurves = function (canvas, metrics) {
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    const pad = { l: 44, r: 16, t: 16, b: 28 };
    const w = W - pad.l - pad.r, h = H - pad.t - pad.b;

    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, W, H);

    const eps = metrics.episodes;
    if (!eps || !eps.length) return;

    const ts = eps.map((e) => e.t);
    const win = Math.max(5, Math.floor(eps.length / 40));
    const rewardMA = movingAvg(eps.map((e) => e.reward), win);
    const scoreMA = movingAvg(eps.map((e) => e.score), win);

    // 坐标轴框
    ctx.strokeStyle = "#e3e8ee";
    ctx.lineWidth = 1;
    ctx.strokeRect(pad.l, pad.t, w, h);

    const rMin = Math.min(...rewardMA), rMax = Math.max(...rewardMA);
    const sMin = 0, sMax = Math.max(50, Math.max(...scoreMA));

    drawLine(ctx, ts, scoreMA, pad.l, pad.t, w, h, sMin, sMax, "#2b8a96");   // task metric
    drawLine(ctx, ts, rewardMA, pad.l, pad.t, w, h, rMin, rMax, "#e06666");  // reward

    // 图例
    ctx.font = "12px system-ui, sans-serif";
    ctx.textAlign = "left";
    ctx.fillStyle = "#2b8a96";
    ctx.fillText("过管数 score（task metric）", pad.l + 8, pad.t + 16);
    ctx.fillStyle = "#e06666";
    ctx.fillText("reward（滑动平均）", pad.l + 8, pad.t + 34);

    // x 轴标注
    ctx.fillStyle = "#66727f";
    ctx.textAlign = "center";
    ctx.fillText("timesteps →", pad.l + w / 2, H - 8);
    ctx.textAlign = "right";
    ctx.fillText(String(ts[ts.length - 1].toLocaleString()), W - pad.r, H - 8);
  };
})();
