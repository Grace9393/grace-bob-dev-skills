---
name: finger-frame-lucy
description: >
  Build realtime AI video effects in the browser — live video-to-video restyling
  through Decart Lucy 2.5 over WebRTC, and MediaPipe hand tracking that masks the
  result to a quad the user frames with their fingers. Use when asked to build a
  live camera effect or AI filter, restyle a webcam feed in real time, swap a
  style prompt without reconnecting a stream, track a two-hand gesture into a
  stable on-screen shape, or reuse this project's tracking pipeline. Trigger on:
  "finger frame", "Decart", "Lucy 2.5", "realtime video to video", "live AI
  camera filter", "MediaPipe hand landmarker", "手勢追蹤", "即時 AI 濾鏡". Not for
  offline video editing, not for generating video from a prompt.
metadata:
  model: sonnet
  effort: high
  source: grace-skill-pack
  upstream: https://github.com/Grace9393/finger-frame-effect-lucy
  verified_against: main.js @ 576 lines, @decartai/sdk 0.1.17, tasks-vision 0.10.14
---

# Finger frame · live AI

<!-- grace-skill-pack: run this on **sonnet** at effort `high`. -->

A working reference for two things that are usually built separately, and are
**independently reusable**:

1. **Realtime video-to-video** — the camera stream goes to Decart Lucy 2.5 over
   WebRTC and comes back restyled at roughly frame rate, tens of milliseconds
   behind. Unlike offline generation, it moves *with* the subject.
2. **Two-hand gesture tracking** — MediaPipe Hand Landmarker resolved into a
   stable four-corner quad, with the jitter, dropout and mis-detection handling
   that a naive implementation lacks.

The app composites them: the restyled stream is clipped to the quad, so the
finger frame is a window into the AI world. Take either half on its own.

Everything below is read out of `main.js`; line counts and constants are the
shipped values, not defaults.

## Running it

```bash
python3 -m http.server 8125
```

Open `http://localhost:8125`, allow the camera. `?demo` runs a synthetic feed
with fake hands — tracking is exercised, AI is disabled. Useful on a machine
with no camera and no key.

No build step. `main.js` is an ES module loading its two dependencies from CDN:

```js
"https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14"
"https://esm.sh/@decartai/sdk@0.1.17"
```

Pin both. A silent minor bump on either CDN changes behaviour mid-demo.

## Half 1 — Decart Lucy 2.5 realtime

```js
const { createDecartClient, models } = await import(DECART_SDK_URL);
const client = createDecartClient({ apiKey });
const realtimeClient = await client.realtime.connect(cameraStream, {
  model: models.realtime("lucy-2.5"),
  initialState: { prompt: { text: currentPrompt(), enhance: true } },
  onRemoteStream: (stream) => { lucyVid.srcObject = stream; lucyVid.play(); },
});
```

You hand it a `MediaStream` and get one back via `onRemoteStream`. That is the
whole contract.

### Swapping style without reconnecting

The important capability, and the reason this is not just a video filter:

```js
await realtimeClient.set({ prompt: text, enhance: true });
```

The running session takes the new prompt live — no teardown, no reconnect, no
visible gap. Keys 1–6 in the app are exactly this.

**SDK shape drift:** the codebase tries `{prompt: text}` and falls back to
`{prompt: {text}}` in a nested `try`, because SDK versions disagree on which is
accepted. Keep that fallback if you upgrade the SDK; do not "clean it up."

### Prompt form

Decart's templates want a rewrite instruction, not a noun phrase. Every shipped
effect follows `"Change the style of the video to <description>: <concrete
visual specifics>."` — e.g. LEGO names the yellow minifigure, cylindrical head,
claw hands and *visible round studs on every surface*. Vague style words produce
vague restyling; naming physical detail is what makes the transform read.

`enhance: true` is set on both the initial state and every update.

### Degrading without a key

`applyEffect` checks `lucyLive && lucyVid.readyState >= 2`. If either is false
it falls back to a local canvas filter —
`hue-rotate(140deg) saturate(1.6) contrast(1.1)` — and paints a prompt to add a
key. **Copy this pattern.** A live-AI demo that shows a black rectangle when the
key is missing or the socket drops looks broken; one that keeps tracking and
shows a local effect looks intentional.

Keys come from `platform.decart.ai`, live in `localStorage`/`sessionStorage`,
and are used only for the WebRTC session. Never commit one, never put one in a
query string.

## Half 2 — the tracking pipeline

Five techniques, each solving a failure a naive implementation hits. Landmarks
used: `WRIST 0`, `THUMB_TIP 4`, `INDEX_MCP 5`, `INDEX_TIP 8`, `MIDDLE_MCP 9`.

### Anatomical corner ordering

Corners are `[left.index, right.index, right.thumb, left.thumb]`, with
left/right decided by on-screen wrist X. Each corner belongs to a *named
finger*, so the edge cycle is real geometry: two upright "L"s trace a rectangle,
and flipping one hand crosses the quad into a bowtie — which then **uncrosses by
itself**, because nothing in the ordering is stateful. Sorting corners by angle
instead would look fine and would never recover.

### Scale from the palm, not the fingers

Hand size is `dist(WRIST, MIDDLE_MCP)`. Finger-based measures foreshorten as the
hand rotates, so every threshold expressed in them drifts with wrist angle.

### Gesture hysteresis

The thumb–index spread required to count as an open "L" is `0.75 × scale` to
*acquire* and `0.20 × scale` to *keep*. The degenerate-area gate is likewise
`0.005` to acquire and `0.0005` to hold, of canvas area. One threshold for both
gives a frame that flickers off whenever fingers rotate or foreshorten.

### Teleport rejection

A quad that moves more than **30% of screen width in one frame** is beyond real
hand motion. It must persist `JUMP_CONFIRM_FRAMES = 2` before being accepted;
otherwise it is treated as a mis-detection. This kills the single-frame jump to
a bystander's hands.

### Velocity-adaptive smoothing and dropout hold

```js
const alpha = Math.min(0.85, Math.max(0.35, moved / (canvas.width * 0.05)));
corners = corners.map((c, i) => lerpPt(c, targetQuad[i], alpha));
```

Low gain damps pixel jitter when nearly still; gain rises the moment the hands
genuinely move, so it does not feel laggy. A fixed lerp cannot be both.

On detection loss the last quad is **held** for `MAX_LOST_FRAMES = 25` (~0.8 s
at 30 fps) before `presence` fades at 0.05/frame. Fading immediately makes the
frame strobe through ordinary tracking gaps.

## Compositing

Both the camera and the returned AI stream are drawn **mirrored and
screen-aligned** to the same full-frame canvas; only the clip path differs. The
AI stream is a full-frame transform of the same input, so drawing it with
identical geometry keeps it registered as the hands move. Do not try to warp the
AI output into the quad — clip it, do not map it.

`presence` drives `globalAlpha`, so appearance and disappearance are a fade
rather than a pop.

## When you reuse this

- **Tracking only** — drop `connectLucy`/`pushPrompt` and keep `computeQuad` +
  the `loop()` state machine. It is a general "stable quad from two hands"
  component; the payload inside the clip is yours.
- **Realtime AI only** — keep the connect/`set` pair and draw the returned
  stream full-frame. The clip is optional.
- **Both, different gesture** — replace `computeQuad`, keep the smoothing,
  teleport and dropout logic. Those are gesture-independent.

Sibling apps for comparison: `finger-frame-effect` (local Canvas 2D effects, no
latency) and `finger-frame-effect-ai` (Gemini offline video edit, minutes). This
one is the realtime member of that family — pick by the latency you can accept.

## Limits worth stating before a demo

- Needs camera permission, a live network path to Decart, and a valid key.
- Latency is tens of milliseconds of model time **plus** the WebRTC round trip —
  on a bad network the honest answer is "not real time."
- Exactly **two hands**; the quad is `null` for one hand or three.
- Never enter a key into a page you did not verify, and never for someone else.
