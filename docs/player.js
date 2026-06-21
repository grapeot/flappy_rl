// Flappy Bird 回放播放器 —— 加载一个 episode JSON，用 Canvas 重演那一局。
//
// 这是一份固定的、所有局共用的播放器。数据（JSON artifact）和播放（本文件）解耦：
// JSON 的 schema 见 src/flappy_rl/recorder.py（version 1）。坐标系 y 向下、y=0 在顶部，
// 与物理内核一致，所以可以直接把 bird_y / gap_top / gap_bottom 当像素画。

(function () {
  "use strict";

  // ---- 渲染参数（纯视觉，不影响数据） ----
  const COL = {
    sky: "#4ec0ca",
    pipe: "#5aa02c",
    pipeEdge: "#3f7a1e",
    bird: "#f6d33c",
    birdEdge: "#d39e00",
    ground: "#ded895",
    text: "#ffffff",
  };

  class Player {
    constructor(canvas, hud) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.hud = hud; // { score, frame, outcome, slider, playBtn }
      this.episode = null;
      this.frameIdx = 0;
      this.playing = false;
      this.timer = null;
      this.fps = 30;
    }

    load(episode) {
      this.episode = episode;
      const cfg = episode.config;
      this.canvas.width = cfg.width;
      this.canvas.height = cfg.height;
      this.frameIdx = 0;
      this.pause();
      if (this.hud.slider) {
        this.hud.slider.max = episode.frames.length - 1;
        this.hud.slider.value = 0;
      }
      this.draw();
      this.updateHud();
    }

    draw() {
      const ep = this.episode;
      if (!ep) return;
      const ctx = this.ctx;
      const cfg = ep.config;
      const f = ep.frames[this.frameIdx];

      // 天空
      ctx.fillStyle = COL.sky;
      ctx.fillRect(0, 0, cfg.width, cfg.height);

      // 管道（上半截 = 缝隙上沿往上；下半截 = 缝隙下沿往下）
      for (const p of f.pipes) {
        ctx.fillStyle = COL.pipe;
        ctx.fillRect(p.x, 0, cfg.pipe_width, p.gap_top);
        ctx.fillRect(p.x, p.gap_bottom, cfg.pipe_width, cfg.height - p.gap_bottom);
        ctx.strokeStyle = COL.pipeEdge;
        ctx.lineWidth = 2;
        ctx.strokeRect(p.x, 0, cfg.pipe_width, p.gap_top);
        ctx.strokeRect(p.x, p.gap_bottom, cfg.pipe_width, cfg.height - p.gap_bottom);
      }

      // 小鸟（圆）；拍翅那一帧描一圈高亮，让动作可见
      ctx.beginPath();
      ctx.arc(cfg.bird_x, f.bird_y, cfg.bird_radius, 0, Math.PI * 2);
      ctx.fillStyle = COL.bird;
      ctx.fill();
      ctx.strokeStyle = f.action === 1 ? "#ff5252" : COL.birdEdge;
      ctx.lineWidth = f.action === 1 ? 3 : 2;
      ctx.stroke();

      // 角标得分
      ctx.fillStyle = COL.text;
      ctx.font = "bold 28px system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(String(f.score), cfg.width / 2, 44);
    }

    updateHud() {
      const ep = this.episode;
      if (!ep) return;
      const f = ep.frames[this.frameIdx];
      if (this.hud.score) this.hud.score.textContent = f.score;
      if (this.hud.frame)
        this.hud.frame.textContent = `${this.frameIdx + 1} / ${ep.frames.length}`;
      if (this.hud.outcome) {
        const o = ep.meta.outcome === "win" ? "过满上限 (win)" : "撞死 (crash)";
        this.hud.outcome.textContent = `${ep.meta.label} · seed ${ep.meta.seed} · ${o}`;
      }
      if (this.hud.slider) this.hud.slider.value = this.frameIdx;
    }

    seek(idx) {
      if (!this.episode) return;
      this.frameIdx = Math.max(0, Math.min(idx, this.episode.frames.length - 1));
      this.draw();
      this.updateHud();
    }

    play() {
      if (!this.episode || this.playing) return;
      // 已到末尾则从头播
      if (this.frameIdx >= this.episode.frames.length - 1) this.frameIdx = 0;
      this.playing = true;
      if (this.hud.playBtn) this.hud.playBtn.textContent = "暂停";
      this.timer = setInterval(() => {
        if (this.frameIdx >= this.episode.frames.length - 1) {
          this.pause();
          return;
        }
        this.frameIdx += 1;
        this.draw();
        this.updateHud();
      }, 1000 / this.fps);
    }

    pause() {
      this.playing = false;
      if (this.hud.playBtn) this.hud.playBtn.textContent = "播放";
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
    }

    toggle() {
      this.playing ? this.pause() : this.play();
    }
  }

  // 暴露到全局，供 index.html 使用
  window.FlappyPlayer = Player;

  // 便捷加载器：从 URL 拉一个 episode JSON
  window.loadEpisode = async function (url) {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`加载失败: ${url} (${resp.status})`);
    return resp.json();
  };
})();
