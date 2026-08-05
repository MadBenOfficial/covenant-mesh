<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import { ArrowUpRight, Fingerprint } from "lucide-vue-next";
defineProps({ busy: Boolean, error: String });
defineEmits(["connect"]);
const canvas = ref(null);
let frame;
onMounted(() => {
  const el = canvas.value;
  const ctx = el.getContext("2d");
  const pointer = { x: -1000, y: -1000 };
  const threads = Array.from({ length: 34 }, (_, i) => ({ phase: i * .71, y: (i + 1) / 35, tone: i % 5 }));
  const resize = () => {
    const ratio = Math.min(devicePixelRatio || 1, 2);
    el.width = innerWidth * ratio; el.height = innerHeight * ratio;
    el.style.width = `${innerWidth}px`; el.style.height = `${innerHeight}px`;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  };
  const move = (e) => { pointer.x = e.clientX; pointer.y = e.clientY; };
  addEventListener("resize", resize); addEventListener("pointermove", move); resize();
  const draw = (time) => {
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    threads.forEach((t, i) => {
      const baseY = t.y * innerHeight;
      const pull = Math.max(0, 1 - Math.abs(pointer.y - baseY) / 190);
      ctx.beginPath();
      for (let x = -20; x <= innerWidth + 20; x += 24) {
        const y = baseY + Math.sin(x * .006 + time * .00035 + t.phase) * 7 +
          pull * 34 * Math.exp(-Math.pow((x - pointer.x) / 240, 2)) * Math.sin(i * .9);
        x === -20 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.strokeStyle = ["#151515", "#2658ff", "#ff315b", "#7f8b84", "#00a878"][t.tone];
      ctx.globalAlpha = t.tone === 0 ? .2 : .14; ctx.lineWidth = t.tone === 0 ? 1 : 1.5; ctx.stroke();
    });
    ctx.globalAlpha = 1; frame = requestAnimationFrame(draw);
  };
  frame = requestAnimationFrame(draw);
  onBeforeUnmount(() => {
    cancelAnimationFrame(frame); removeEventListener("resize", resize); removeEventListener("pointermove", move);
  });
});
</script>

<template>
  <main class="landing">
    <canvas ref="canvas" class="landing-canvas" aria-hidden="true"></canvas>
    <header class="landing-head">
      <a class="landing-mark" href="#" aria-label="Covenant Mesh home"><span>CM</span><strong>Covenant Mesh</strong></a>
      <div class="landing-actions"><div class="network-label"><i></i> StudioNet / live</div><button :disabled="busy" @click="$emit('connect')">{{ busy ? "Connecting" : "Connect wallet" }}<ArrowUpRight :size="17" /></button></div>
    </header>
    <section class="landing-statement">
      <p class="kicker">Collective data rights / enforced by intelligent consensus</p>
      <h1>Permission should<br>travel with the data.</h1>
      <div class="landing-copy">
        <p>A living permission layer where communities publish enforceable covenants, researchers earn bounded access, and every use remains accountable.</p>
        <span>06 collections<br>02 issued permits<br>60 units allocated</span>
      </div>
    </section>
    <div class="landing-notes" aria-hidden="true">
      <span style="--x:8%;--y:27%">PURPOSE</span><span style="--x:79%;--y:31%">RETENTION</span>
      <span style="--x:61%;--y:69%">REMEDIATION</span><span style="--x:13%;--y:73%">AUDIT</span>
    </div>
    <footer class="signature-rail">
      <div><Fingerprint :size="28" /><p><strong>Enter by signature</strong><br>Wallet access persists on this device.</p></div>
      <p v-if="error" class="landing-error">{{ error }}</p>
      <span class="landing-enter">ACCOUNTABLE ACCESS / PERSISTENT SESSION</span>
    </footer>
  </main>
</template>
