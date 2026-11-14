// Peças reutilizáveis das cenas 3D (bancada T6). Regra de ouro: tudo é função do tempo t.
// Mesmo t → mesmo quadro (sem relógio, sem Math.random): é o que permite renderizar quadro a quadro.
import * as THREE from 'three';

export { THREE };

// ---------- tempo e interpolação ----------
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, k) => a + (b - a) * k;
export const easing = {
  linear: k => k,
  inOut: k => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
  out: k => 1 - Math.pow(1 - k, 3),
  in: k => k * k * k,
  outBack: k => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); },
};
/** Progresso 0..1 de t dentro de [ini, fim], com easing. */
export const janela = (t, ini, fim, e = easing.inOut) => e(clamp((t - ini) / (fim - ini)));
/** Sobe em [ini, ini+entra], fica em 1, desce em [fim-sai, fim]. */
export const pulso = (t, ini, fim, entra = 0.25, sai = 0.25) =>
  Math.min(janela(t, ini, ini + entra, easing.out), 1 - janela(t, fim - sai, fim, easing.in));

/** Gerador pseudoaleatório com semente (mulberry32): a cena sai igual em toda renderização. */
export function aleatorio(semente) {
  let a = semente >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------- câmera ----------
/** Caminho contínuo de câmera: Catmull-Rom entre chaves {t, pos:[x,y,z], alvo:[x,y,z], fov?}. */
export function caminhoCamera(chaves, { tremor = 0.012 } = {}) {
  const cr = (p0, p1, p2, p3, s) => {
    const s2 = s * s, s3 = s2 * s;
    return 0.5 * (2 * p1 + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s3);
  };
  const n = chaves.length;
  return (t, camera) => {
    let i = 0;
    while (i < n - 2 && t > chaves[i + 1].t) i++;
    const a = chaves[Math.max(0, i - 1)], b = chaves[i], c = chaves[Math.min(n - 1, i + 1)], d = chaves[Math.min(n - 1, i + 2)];
    let s = clamp((t - b.t) / Math.max(1e-6, c.t - b.t));
    if (i === 0 || i === n - 2) s = i === 0 ? easing.inOut(s) * 0.5 + s * 0.5 : s; // partida suave
    const v = k => [0, 1, 2].map(j => cr(a[k][j], b[k][j], c[k][j], d[k][j], s));
    const [px, py, pz] = v('pos');
    // "câmera na mão": um tremor lento e pequeno dá vida sem chamar atenção
    camera.position.set(px + tremor * Math.sin(t * 1.3), py + tremor * Math.sin(t * 1.7 + 1), pz + tremor * Math.sin(t * 1.1 + 2));
    camera.lookAt(...v('alvo'));
    const fov = lerp(b.fov ?? 50, c.fov ?? 50, easing.inOut(s));
    if (camera.fov !== fov) { camera.fov = fov; camera.updateProjectionMatrix(); }
  };
}

// ---------- geometria ----------
/** Tubo afunilado que se deforma a cada quadro (braços, algas, caudas). */
export class Tubo {
  constructor(nPontos, nRadial, material) {
    this.n = nPontos; this.nr = nRadial;
    const pos = new Float32Array((nPontos * nRadial + 1) * 3);
    const idx = [];
    for (let i = 0; i < nPontos - 1; i++) {
      for (let j = 0; j < nRadial; j++) {
        const a = i * nRadial + j, b = i * nRadial + ((j + 1) % nRadial);
        const c = (i + 1) * nRadial + j, d = (i + 1) * nRadial + ((j + 1) % nRadial);
        idx.push(a, b, c, b, d, c);
      }
    }
    const ponta = nPontos * nRadial, ult = (nPontos - 1) * nRadial;
    for (let j = 0; j < nRadial; j++) idx.push(ult + j, ult + ((j + 1) % nRadial), ponta);
    this.geo = new THREE.BufferGeometry();
    this.geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    this.geo.setIndex(idx);
    this.malha = new THREE.Mesh(this.geo, material);
    this.malha.frustumCulled = false;
    this._T = new THREE.Vector3(); this._N = new THREE.Vector3(); this._B = new THREE.Vector3(); this._tmp = new THREE.Vector3();
    this.tangentes = Array.from({ length: nPontos }, () => new THREE.Vector3());
  }

  /** pontos: Vector3[n]; raios: number[n]; ref: vetor que fixa a "costura" do tubo (evita torção). */
  atualizar(pontos, raios, ref = new THREE.Vector3(0, 1, 0)) {
    const p = this.geo.attributes.position.array, n = this.n, nr = this.nr;
    const T = this._T, N = this._N, B = this._B;
    for (let i = 0; i < n; i++) {
      const a = pontos[Math.max(0, i - 1)], b = pontos[Math.min(n - 1, i + 1)];
      T.subVectors(b, a).normalize();
      this.tangentes[i].copy(T);
      const base = i === 0 ? ref : N;
      N.copy(base).addScaledVector(T, -base.dot(T));
      if (N.lengthSq() < 1e-8) N.set(1, 0, 0).addScaledVector(T, -T.x);
      N.normalize();
      B.crossVectors(T, N);
      for (let j = 0; j < nr; j++) {
        const ang = (j / nr) * Math.PI * 2, c = Math.cos(ang) * raios[i], s = Math.sin(ang) * raios[i];
        const k = (i * nr + j) * 3;
        p[k] = pontos[i].x + c * N.x + s * B.x;
        p[k + 1] = pontos[i].y + c * N.y + s * B.y;
        p[k + 2] = pontos[i].z + c * N.z + s * B.z;
      }
    }
    const k = n * nr * 3, fim = pontos[n - 1];
    this._tmp.copy(this.tangentes[n - 1]).multiplyScalar(raios[n - 1] * 1.2).add(fim);
    p[k] = this._tmp.x; p[k + 1] = this._tmp.y; p[k + 2] = this._tmp.z;
    this.geo.attributes.position.needsUpdate = true;
    this.geo.computeVertexNormals();
  }
}

/** Pedra low-poly: deslocamento por posição (vértices repetidos recebem o mesmo valor, sem rachar a malha). */
export function pedra(raio, cor, semente = 1, detalhe = 1) {
  const geo = new THREE.IcosahedronGeometry(raio, detalhe);
  const p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const f = 1 + 0.18 * Math.sin(x * 3.1 + semente) * Math.cos(z * 2.7 + semente * 1.3) + 0.1 * Math.sin(y * 4.3 + semente * 2.1);
    p.setXYZ(i, x * f, y * f * 0.8, z * f);
  }
  geo.computeVertexNormals();
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: cor, roughness: 0.95, flatShading: true }));
  m.castShadow = true; m.receiveShadow = true;
  return m;
}

/** Fundo em degradê (esfera por dentro), sem neblina. */
export function ceuDegrade(topo, base, raio = 120) {
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { topo: { value: new THREE.Color(topo) }, base: { value: new THREE.Color(base) } },
    vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: 'uniform vec3 topo;\nuniform vec3 base;\nvarying vec3 vP;\nvoid main(){\n  float k = smoothstep(-0.35, 0.75, vP.y);\n  gl_FragColor = vec4(mix(base, topo, k), 1.0);\n  #include <colorspace_fragment>\n}',
  });
  const m = new THREE.Mesh(new THREE.SphereGeometry(raio, 32, 16), mat);
  m.frustumCulled = false;
  return m;
}

// ---------- palco: renderer + composição 2D ----------
export class Palco {
  constructor({ largura, altura }) {
    this.W = largura; this.H = altura;
    this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    this.renderer.setPixelRatio(1);
    this.renderer.setSize(largura, altura, false);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.NeutralToneMapping;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFShadowMap;
    this.cena = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(50, largura / altura, 0.05, 300);
    this.saida = document.createElement('canvas');
    this.saida.width = largura; this.saida.height = altura;
    this.ctx = this.saida.getContext('2d');
    this.hud = new Hud(this.ctx, largura, altura);
  }

  info() {
    const gl = this.renderer.getContext();
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    return { renderer: ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER), three: THREE.REVISION };
  }

  /** Eventos de som com `ancora` ganham pan pela posição do objeto na tela naquele instante. */
  mapearSons(atualizar, eventos) {
    const v = new THREE.Vector3();
    return eventos
      .map(({ ancora, ...e }) => {
        if (ancora) {
          atualizar(e.t);
          this.camera.updateMatrixWorld();
          v.copy(ancora()).project(this.camera);
          e.pan = Math.round(clamp(v.x * 0.8, -0.9, 0.9) * 100) / 100;
        }
        return e;
      })
      .sort((a, b) => a.t - b.t);
  }

  /** Desenha o quadro do instante t e devolve a imagem (data URL). */
  quadro(t, atualizar, duracao, formato = 'jpeg') {
    atualizar(t);
    this.renderer.render(this.cena, this.camera);
    this.ctx.drawImage(this.renderer.domElement, 0, 0);
    this.hud.desenhar(t, this.camera, duracao);
    if (formato === 'nenhum') return null;
    return this.saida.toDataURL(formato === 'png' ? 'image/png' : 'image/jpeg', 0.95);
  }
}

// ---------- HUD: legenda palavra a palavra, etiquetas presas a objetos, barra de progresso ----------
const FONTE = '"Lilita One"';
const AMARELO = '#ffd600', ESCURO = '#16162a';

export class Hud {
  constructor(ctx, W, H) {
    this.ctx = ctx; this.W = W; this.H = H;
    this.palavras = []; this.etiquetas = [];
    this._v = new THREE.Vector3();
  }

  /** segmentos: [{ini, fim, texto, destaque: ['palavra']}]; o tempo de cada palavra é proporcional ao tamanho. */
  legenda(segmentos) {
    for (const seg of segmentos) {
      const ps = seg.texto.split(/\s+/).filter(Boolean);
      const pesos = ps.map(p => p.replace(/[^\p{L}\p{N}]/gu, '').length + 2);
      const total = pesos.reduce((a, b) => a + b, 0);
      let acc = seg.ini;
      ps.forEach((p, i) => {
        const dur = ((seg.fim - seg.ini) * pesos[i]) / total;
        const limpa = p.replace(/[.,:;!?]+$/u, '');
        const destaque = (seg.destaque || []).some(d => d.toLowerCase() === limpa.toLowerCase());
        this.palavras.push({ texto: limpa, ini: acc, fim: i === ps.length - 1 ? seg.fim + 0.25 : acc + dur, destaque });
        acc += dur;
      });
    }
  }

  /** estilo: 'pilula' (padrão), 'numero' ou 'simbolo'. ancora: () => Vector3 no mundo. */
  etiqueta(e) { this.etiquetas.push({ estilo: 'pilula', desloc: [0.08, -0.07], ...e }); }

  _tela(v, camera) {
    this._v.copy(v).project(camera);
    if (this._v.z > 1) return null;
    return [((this._v.x + 1) / 2) * this.W, ((1 - this._v.y) / 2) * this.H];
  }

  desenhar(t, camera, duracao) {
    const { ctx, W, H } = this;
    for (const e of this.etiquetas) {
      if (t < e.ini || t > e.fim) continue;
      const a = this._tela(e.ancora(), camera);
      if (!a) continue;
      const pop = easing.outBack(clamp((t - e.ini) / 0.35));
      const alfa = 1 - janela(t, e.fim - 0.25, e.fim, easing.in);
      ctx.save();
      ctx.globalAlpha = alfa;
      if (e.estilo === 'pilula') this._pilula(e, a, pop);
      else if (e.estilo === 'numero') this._numero(e, a, pop);
      else this._simbolo(e, a, pop, t);
      ctx.restore();
    }
    this._legenda(t);
    if (duracao) this._progresso(t / duracao);
  }

  _pilula(e, [ax, ay], pop) {
    const { ctx, H } = this;
    const px = ax + e.desloc[0] * H, py = ay + e.desloc[1] * H;
    const fs = H * 0.03;
    ctx.font = `${fs}px ${FONTE}`;
    const w = ctx.measureText(e.texto).width + fs * 1.3, h = fs * 1.7;
    // linha e ponto de ancoragem
    ctx.strokeStyle = '#ffffff'; ctx.lineWidth = H * 0.0028; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(lerp(ax, px, pop), lerp(ay, py, pop)); ctx.stroke();
    ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(ax, ay, H * 0.0065, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = ESCURO; ctx.beginPath(); ctx.arc(ax, ay, H * 0.0032, 0, Math.PI * 2); ctx.fill();
    ctx.translate(px, py); ctx.scale(pop, pop);
    ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = H * 0.008; ctx.shadowOffsetY = H * 0.003;
    ctx.fillStyle = e.cor || AMARELO;
    ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, h / 2); ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = ESCURO; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(e.texto, 0, fs * 0.06);
  }

  _numero(e, [ax, ay], pop) {
    const { ctx, H } = this;
    const r = H * 0.024;
    ctx.translate(ax + e.desloc[0] * H, ay + e.desloc[1] * H); ctx.scale(pop, pop);
    ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = H * 0.006;
    ctx.fillStyle = AMARELO; ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.lineWidth = H * 0.003; ctx.strokeStyle = ESCURO; ctx.stroke();
    ctx.font = `${r * 1.25}px ${FONTE}`; ctx.fillStyle = ESCURO; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(e.texto, 0, r * 0.08);
  }

  _simbolo(e, [ax, ay], pop, t) {
    const { ctx, H } = this;
    const fs = H * 0.075;
    ctx.translate(ax + e.desloc[0] * H, ay + e.desloc[1] * H + Math.sin(t * 6) * H * 0.003);
    ctx.scale(pop, pop); ctx.rotate(Math.sin(t * 3) * 0.08);
    ctx.font = `${fs}px ${FONTE}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    ctx.lineWidth = fs * 0.16; ctx.strokeStyle = ESCURO; ctx.strokeText(e.texto, 0, 0);
    ctx.fillStyle = e.cor || AMARELO; ctx.fillText(e.texto, 0, 0);
  }

  _legenda(t) {
    const p = this.palavras.find(w => t >= w.ini && t < w.fim);
    if (!p) return;
    const { ctx, W, H } = this;
    let fs = H * 0.052;
    ctx.font = `${fs}px ${FONTE}`;
    const largura = ctx.measureText(p.texto).width;
    if (largura > W * 0.86) fs *= (W * 0.86) / largura;
    const pop = lerp(1.28, 1, easing.out(clamp((t - p.ini) / 0.13)));
    ctx.save();
    ctx.translate(W / 2, H * 0.69); ctx.scale(pop, pop);
    ctx.font = `${fs}px ${FONTE}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = fs * 0.12; ctx.shadowOffsetY = fs * 0.07;
    ctx.lineWidth = fs * 0.2; ctx.strokeStyle = ESCURO; ctx.strokeText(p.texto, 0, 0);
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = p.destaque ? AMARELO : '#ffffff'; ctx.fillText(p.texto, 0, 0);
    ctx.restore();
  }

  _progresso(k) {
    const { ctx, W, H } = this;
    const w = W * 0.5, h = H * 0.0055, x = (W - w) / 2, y = H * 0.045;
    ctx.save();
    ctx.fillStyle = 'rgba(0,0,0,0.28)'; ctx.beginPath(); ctx.roundRect(x, y, w, h, h / 2); ctx.fill();
    ctx.fillStyle = AMARELO; ctx.beginPath(); ctx.roundRect(x, y, Math.max(h, w * clamp(k)), h, h / 2); ctx.fill();
    ctx.restore();
  }
}
