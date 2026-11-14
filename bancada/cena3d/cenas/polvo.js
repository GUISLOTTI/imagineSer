// T6 — protótipo "Imagine ser um polvo" (~20 s). Texto de TESTE: não é roteiro aprovado nem vai ao ar.
// Fatos usados (8 braços, ventosas, mudança de cor) são básicos, mas ainda sem dossiê/afirmacoes.json.
import { THREE, Palco, Tubo, caminhoCamera, janela, pulso, easing, clamp, lerp, aleatorio, pedra, ceuDegrade } from '../kit.js';

const DURACAO = 20.6;
const Y = new THREE.Vector3(0, 1, 0);

export async function criar({ largura, altura }) {
  const palco = new Palco({ largura, altura });
  const { cena, camera, hud } = palco;
  const rnd = aleatorio(7);

  // ---------------- ambiente ----------------
  const AGUA = new THREE.Color('#1477a8');
  cena.add(ceuDegrade('#7fdcf5', '#06395a'));
  cena.fog = new THREE.Fog(AGUA, 6, 28);

  cena.add(new THREE.HemisphereLight('#c4f4ff', '#d8b27a', 1.7));
  const sol = new THREE.DirectionalLight('#fff3da', 2.3);
  sol.position.set(3, 10, 5);
  sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048);
  Object.assign(sol.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 });
  sol.shadow.bias = -0.0004; sol.shadow.normalBias = 0.02;
  cena.add(sol);

  // chão de areia com dunas suaves (plano perto do polvo)
  const chaoGeo = new THREE.PlaneGeometry(90, 90, 90, 90);
  chaoGeo.rotateX(-Math.PI / 2);
  {
    const p = chaoGeo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), z = p.getZ(i), r = Math.hypot(x, z);
      const onda = 0.22 * Math.sin(x * 0.55 + 1.3) * Math.cos(z * 0.5) + 0.08 * Math.sin(x * 1.9 + z * 1.4);
      p.setY(i, onda * clamp((r - 2.2) / 4));
    }
    chaoGeo.computeVertexNormals();
  }
  const chao = new THREE.Mesh(chaoGeo, new THREE.MeshStandardMaterial({ color: '#e8cf98', roughness: 1, flatShading: true }));
  chao.receiveShadow = true;
  cena.add(chao);

  // pedra grande atrás do polvo (é nela que ele se camufla) + pedras soltas
  const COR_PEDRA = new THREE.Color('#7d8c79');
  const pedraGrande = pedra(1.0, COR_PEDRA, 3);
  pedraGrande.position.set(-0.15, 0.55, -2.7);
  pedraGrande.scale.set(2.9, 2.1, 1.4);
  cena.add(pedraGrande);
  for (let i = 0; i < 14; i++) {
    const ang = rnd() * Math.PI * 2, dist = 3 + rnd() * 9;
    const s = pedra(0.25 + rnd() * 0.5, new THREE.Color().setHSL(0.25 + rnd() * 0.1, 0.08, 0.45 + rnd() * 0.15), i + 10);
    s.position.set(Math.cos(ang) * dist, 0.05, Math.sin(ang) * dist - 2);
    s.rotation.y = rnd() * 6;
    cena.add(s);
  }

  // corais (ramos de cilindro com pontas redondas)
  const coresCoral = ['#ff6f91', '#9b5de5', '#ff9671', '#f15bb5'];
  for (let i = 0; i < 9; i++) {
    const g = new THREE.Group();
    const mat = new THREE.MeshStandardMaterial({ color: coresCoral[i % 4], roughness: 0.8, flatShading: true });
    const ramos = 3 + Math.floor(rnd() * 3);
    for (let k = 0; k < ramos; k++) {
      const h = 0.35 + rnd() * 0.5;
      const ramo = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.07, h, 7), mat);
      const inc = (rnd() - 0.5) * 0.9, giro = rnd() * 6;
      ramo.position.set(Math.sin(giro) * Math.sin(inc) * h * 0.5, h / 2, Math.cos(giro) * Math.sin(inc) * h * 0.5);
      ramo.rotation.set(Math.cos(giro) * inc, 0, -Math.sin(giro) * inc);
      const ponta = new THREE.Mesh(new THREE.SphereGeometry(0.075, 8, 6), mat);
      ponta.position.set(0, h / 2, 0);
      ramo.add(ponta);
      ramo.castShadow = true;
      g.add(ramo);
    }
    const ang = rnd() * Math.PI * 2, dist = 2.6 + rnd() * 5;
    g.position.set(Math.cos(ang) * dist, 0, Math.sin(ang) * dist - 1);
    g.scale.setScalar(0.9 + rnd() * 0.8);
    cena.add(g);
  }

  // algas que balançam
  const algas = [];
  const matAlga = new THREE.MeshStandardMaterial({ color: '#2fb36b', roughness: 0.8 });
  for (let i = 0; i < 12; i++) {
    const tubo = new Tubo(14, 6, matAlga);
    tubo.malha.castShadow = true;
    const ang = rnd() * Math.PI * 2, dist = 2.4 + rnd() * 6;
    algas.push({ tubo, base: new THREE.Vector3(Math.cos(ang) * dist, 0, Math.sin(ang) * dist - 1.5), h: 1.1 + rnd() * 1.6, fase: rnd() * 6 });
    cena.add(tubo.malha);
  }
  const ptsAlga = Array.from({ length: 14 }, () => new THREE.Vector3());
  const raiosAlga = Array.from({ length: 14 }, (_, k) => 0.07 * (1 - k / 16));

  // estrela-do-mar
  {
    const forma = new THREE.Shape();
    for (let k = 0; k < 10; k++) {
      const r = k % 2 ? 0.09 : 0.24, a = (k / 10) * Math.PI * 2;
      k ? forma.lineTo(Math.cos(a) * r, Math.sin(a) * r) : forma.moveTo(r, 0);
    }
    const geo = new THREE.ExtrudeGeometry(forma, { depth: 0.04, bevelEnabled: true, bevelSize: 0.03, bevelThickness: 0.03, bevelSegments: 1 });
    geo.rotateX(-Math.PI / 2);
    const mat = new THREE.MeshStandardMaterial({ color: '#ff9f1c', roughness: 0.7, flatShading: true });
    [[1.9, 0.9], [-2.3, 1.6]].forEach(([x, z], i) => {
      const e = new THREE.Mesh(geo, mat); e.position.set(x, 0.03, z); e.rotation.y = i * 1.2; e.castShadow = true; cena.add(e);
    });
  }

  // feixes de luz vindos da superfície
  const feixes = [];
  const matFeixe = new THREE.MeshBasicMaterial({ color: '#eafcff', transparent: true, opacity: 0.07, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });
  for (let i = 0; i < 6; i++) {
    const f = new THREE.Mesh(new THREE.ConeGeometry(0.9 + rnd() * 0.8, 20, 18, 1, true), matFeixe);
    f.position.set((rnd() - 0.5) * 9, 9, -2 - rnd() * 6);
    f.rotation.z = 0.25 + (rnd() - 0.5) * 0.1;
    feixes.push({ f, fase: rnd() * 6, base: f.rotation.z });
    cena.add(f);
  }

  // bolhas (algumas saem do polvo quando ele acorda)
  const NB = 70;
  const bolhas = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 10, 8), new THREE.MeshStandardMaterial({ color: '#effcff', transparent: true, opacity: 0.55, roughness: 0.05 }), NB);
  bolhas.frustumCulled = false;
  const dadosBolha = Array.from({ length: NB }, (_, i) => ({
    x: (rnd() - 0.5) * 10, z: (rnd() - 0.5) * 8 - 1, y0: rnd() * 10, v: 0.35 + rnd() * 0.6, r: 0.025 + rnd() * 0.05, fase: rnd() * 6,
    doPolvo: i < 14, nasce: 2.15 + rnd() * 0.5,
  }));
  cena.add(bolhas);

  // neve marinha (partículas paradas no ar)
  {
    const n = 400, pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { pos[i * 3] = (rnd() - 0.5) * 16; pos[i * 3 + 1] = rnd() * 8; pos[i * 3 + 2] = (rnd() - 0.5) * 16; }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    var neve = new THREE.Points(geo, new THREE.PointsMaterial({ color: '#ffffff', size: 0.025, transparent: true, opacity: 0.6 }));
    cena.add(neve);
  }

  // ---------------- polvo ----------------
  const COR_POLVO = new THREE.Color('#ff7650');
  const COR_MANCHA = new THREE.Color('#d9532f');
  const COR_MANCHA_PEDRA = new THREE.Color('#5f6d5c');
  const COR_VENTOSA = new THREE.Color('#ffd3c4');
  const matPolvo = new THREE.MeshStandardMaterial({ color: COR_POLVO.clone(), roughness: 0.5 });
  const matMancha = new THREE.MeshStandardMaterial({ color: COR_MANCHA.clone(), roughness: 0.6 });
  const matVentosa = new THREE.MeshStandardMaterial({ color: COR_VENTOSA.clone(), roughness: 0.45 });

  const polvo = new THREE.Group();
  cena.add(polvo);
  const corpo = new THREE.Group();
  polvo.add(corpo);

  const manto = new THREE.Mesh(new THREE.SphereGeometry(0.6, 40, 28), matPolvo);
  manto.scale.set(1, 1.22, 1.0); manto.position.set(0, 1.12, -0.16); manto.rotation.x = -0.32;
  const cabeca = new THREE.Mesh(new THREE.SphereGeometry(0.5, 36, 24), matPolvo);
  cabeca.scale.set(1.06, 0.78, 0.96); cabeca.position.set(0, 0.62, 0.04);
  [manto, cabeca].forEach(m => { m.castShadow = true; m.receiveShadow = true; corpo.add(m); });
  // manchas no manto
  for (let i = 0; i < 9; i++) {
    const a = rnd() * Math.PI * 2, el = 0.2 + rnd() * 0.9;
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.05 + rnd() * 0.05, 10, 8), matMancha);
    m.position.set(Math.cos(a) * Math.cos(el) * 0.6, Math.sin(el) * 0.6, Math.sin(a) * Math.cos(el) * 0.6);
    m.scale.set(1, 1, 0.35); m.lookAt(0, 0, 0);
    manto.add(m);
  }
  // olhos (branco, pupila que segue a câmera, brilho)
  const olhos = [-1, 1].map(lado => {
    const g = new THREE.Group();
    g.position.set(lado * 0.21, 0.74, 0.4);
    const branco = new THREE.Mesh(new THREE.SphereGeometry(0.15, 24, 16), new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 0.3 }));
    const pupila = new THREE.Mesh(new THREE.SphereGeometry(0.085, 20, 14), new THREE.MeshStandardMaterial({ color: '#111522', roughness: 0.2 }));
    const brilho = new THREE.Mesh(new THREE.SphereGeometry(0.024, 10, 8), new THREE.MeshBasicMaterial({ color: '#ffffff' }));
    pupila.position.z = 0.085; brilho.position.set(0.03, 0.04, 0.075); pupila.add(brilho);
    g.add(branco, pupila);
    corpo.add(g);
    return { g, pupila };
  });
  // boquinha
  {
    const boca = new THREE.Mesh(new THREE.TorusGeometry(0.06, 0.016, 8, 16, Math.PI), new THREE.MeshStandardMaterial({ color: '#7a2416' }));
    boca.position.set(0, 0.56, 0.5); boca.rotation.set(0.2, 0, Math.PI);
    corpo.add(boca);
  }

  // braços
  const NBR = 8, NP = 36, NV = 11, L = 2.0;
  const bracos = [];
  const ventosas = new THREE.InstancedMesh(new THREE.CylinderGeometry(1, 0.8, 0.4, 14), matVentosa, NBR * NV);
  ventosas.castShadow = true; ventosas.frustumCulled = false;
  corpo.add(ventosas);
  for (let i = 0; i < NBR; i++) {
    const th = ((i + 0.5) / NBR) * Math.PI * 2;
    const dir = new THREE.Vector3(Math.sin(th), 0, Math.cos(th));
    const lado = new THREE.Vector3().crossVectors(dir, Y);
    const tubo = new Tubo(NP, 12, matPolvo);
    tubo.malha.castShadow = true; tubo.malha.receiveShadow = true;
    corpo.add(tubo.malha);
    bracos.push({
      dir, lado, tubo, fase: i * 1.7,
      base: new THREE.Vector3(0, 0.44, 0.02).addScaledVector(dir, 0.34),
      pontos: Array.from({ length: NP }, () => new THREE.Vector3()), raios: new Array(NP).fill(0.1),
      ordem: (i + 1) % NBR,
    });
  }
  // braço que acena para a câmera (frente-direita)
  const ACENO = 1;

  const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _p = new THREE.Vector3(), _ventral = new THREE.Vector3();

  function formaBraco(b, t, ext, ergue) {
    const Le = L * (0.32 + 0.68 * ext);
    const ds = Le / (NP - 1), dsn = 1 / (NP - 1);
    let phi = -1.15, u = 0, v = 0;
    for (let k = 0; k < NP; k++) {
      const sn = k * dsn;
      const raio = 0.115 * (1 - 0.86 * sn) + 0.012;
      const balanco = 0.22 * Math.pow(sn, 1.5) * Math.sin(1.3 * t + b.fase);
      b.pontos[k].copy(b.base).addScaledVector(b.dir, u).addScaledVector(b.lado, balanco);
      let y = b.base.y + v;
      if (y < raio * 0.9) y = raio * 0.9;
      b.pontos[k].y = y;
      b.raios[k] = raio;
      // curvatura por unidade de comprimento normalizado
      let A = (sn < 0.32 ? 3.6 : 0) + (sn > 0.68 ? 21.9 * (sn - 0.68) / 0.32 : 0);
      A += (1 - ext) * 9;
      A += ergue * (sn > 0.08 && sn < 0.45 ? 4.6 : 0);
      A += 1.3 * sn * Math.sin(2.1 * t - 5 * sn + b.fase);
      phi += A * dsn;
      u += Math.cos(phi) * ds;
      v += Math.sin(phi) * ds;
    }
    b.tubo.atualizar(b.pontos, b.raios, b.lado);
  }

  // ---------------- peixe ----------------
  const peixe = new THREE.Group();
  {
    const matP = new THREE.MeshStandardMaterial({ color: '#ffd23f', roughness: 0.5, flatShading: true });
    const corpoP = new THREE.Mesh(new THREE.SphereGeometry(0.2, 14, 10), matP); corpoP.scale.set(1.45, 0.85, 0.5);
    const listra = new THREE.Mesh(new THREE.SphereGeometry(0.201, 14, 10), new THREE.MeshStandardMaterial({ color: '#3a86ff', roughness: 0.5, flatShading: true }));
    listra.scale.set(0.35, 0.86, 0.51); listra.position.x = 0.05;
    var cauda = new THREE.Group(); cauda.position.x = 0.27;
    const nadadeira = new THREE.Mesh(new THREE.ConeGeometry(0.15, 0.24, 4), matP); nadadeira.rotation.z = Math.PI / 2; nadadeira.position.x = 0.1; nadadeira.scale.set(1, 1, 0.3);
    cauda.add(nadadeira);
    const olhoP = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 6), new THREE.MeshStandardMaterial({ color: '#111' }));
    olhoP.position.set(-0.17, 0.05, 0.08);
    const olhoP2 = olhoP.clone(); olhoP2.position.z = -0.08;
    peixe.add(corpoP, listra, cauda, olhoP, olhoP2);
    peixe.traverse(o => { if (o.isMesh) o.castShadow = true; });
  }
  cena.add(peixe);

  // ---------------- câmera ----------------
  const moverCamera = caminhoCamera([
    { t: 0.0, pos: [0.6, 6.4, 8.6], alvo: [0, 4.3, 0] },
    { t: 2.4, pos: [0.3, 1.9, 4.7], alvo: [0, 0.85, 0] },
    { t: 5.6, pos: [0.9, 7.4, 3.4], alvo: [0, 0.2, 0.75] },
    { t: 8.0, pos: [2.1, 1.4, 2.7], alvo: [0.55, 1.05, 0.35] },
    { t: 9.9, pos: [1.6, 1.5, 3.4], alvo: [0.35, 1.0, 0.3] },
    { t: 12.3, pos: [0.4, 2.0, 6.3], alvo: [-0.2, 0.95, -0.9] },
    { t: 15.5, pos: [0.1, 1.5, 4.6], alvo: [0, 0.8, -0.3] },
    { t: 18.0, pos: [0.75, 1.45, 4.6], alvo: [0.4, 0.95, 0.4] },
    { t: DURACAO, pos: [0.2, 1.7, 5.7], alvo: [0, 0.9, 0] },
  ]);

  // ---------------- texto e etiquetas ----------------
  hud.legenda([
    { ini: 0.3, fim: 2.3, texto: 'Imagine ser um polvo.', destaque: ['polvo'] },
    { ini: 3.0, fim: 5.3, texto: 'Oito braços,', destaque: ['Oito'] },
    { ini: 5.6, fim: 8.6, texto: 'e cada um cheio de ventosas.', destaque: ['ventosas'] },
    { ini: 9.4, fim: 12.2, texto: 'Mas o seu melhor truque é outro:', destaque: ['truque'] },
    { ini: 12.6, fim: 15.2, texto: 'você muda de cor', destaque: ['cor'] },
    { ini: 15.6, fim: 18.4, texto: 'e some na frente de todo mundo.', destaque: ['some'] },
  ]);
  const inicioBraco = b => 3.0 + b.ordem * 0.27;
  bracos.forEach((b, i) => hud.etiqueta({
    estilo: 'numero', texto: String(b.ordem + 1), ini: inicioBraco(b) + 0.75, fim: 5.9,
    ancora: () => _w.copy(b.pontos[NP - 1]).applyMatrix4(corpo.matrixWorld), desloc: [0, -0.03],
  }));
  hud.etiqueta({ texto: '8 BRAÇOS', ini: 5.6, fim: 7.2, ancora: () => _topo.set(0, 1.85, -0.2), desloc: [0, -0.09] });
  hud.etiqueta({ texto: 'VENTOSAS', ini: 7.4, fim: 9.6, ancora: () => _ancoraVentosa, desloc: [-0.13, -0.1] });
  hud.etiqueta({ texto: 'CAMUFLAGEM', ini: 13.3, fim: 15.7, ancora: () => _topo.set(0, 1.85, -0.2), desloc: [0.06, -0.08] });
  hud.etiqueta({ estilo: 'simbolo', texto: '?', ini: 17.9, fim: 19.7, ancora: () => _p2.copy(peixe.position).add(_cima), desloc: [0, -0.03] });
  const _w = new THREE.Vector3(), _ancoraVentosa = new THREE.Vector3(), _topo = new THREE.Vector3(), _p2 = new THREE.Vector3(), _cima = new THREE.Vector3(0, 0.3, 0);
  const _camLocal = new THREE.Vector3();

  // ---------------- animação ----------------
  function atualizar(t) {
    moverCamera(t, camera);

    for (const { f, fase, base } of feixes) f.rotation.z = base + 0.05 * Math.sin(t * 0.4 + fase);
    for (const a of algas) {
      for (let k = 0; k < 14; k++) {
        const s = k / 13;
        ptsAlga[k].copy(a.base);
        ptsAlga[k].y = s * a.h;
        ptsAlga[k].x += 0.25 * s * s * Math.sin(1.2 * t + a.fase - s * 2);
        ptsAlga[k].z += 0.12 * s * s * Math.cos(0.9 * t + a.fase);
      }
      a.tubo.atualizar(ptsAlga, raiosAlga, new THREE.Vector3(1, 0, 0));
    }
    dadosBolha.forEach((b, i) => {
      let x, y, z;
      if (b.doPolvo) {
        const vida = t - b.nasce;
        if (vida < 0) { _s.setScalar(0); _m.compose(_p.set(0, -5, 0), _q.identity(), _s); bolhas.setMatrixAt(i, _m); return; }
        x = (b.x * 0.05) + 0.06 * Math.sin(4 * vida + b.fase); y = 1.4 + vida * (0.9 + b.v); z = b.z * 0.03;
      } else {
        x = b.x + 0.06 * Math.sin(3 * t + b.fase); y = (b.y0 + b.v * t) % 10; z = b.z;
      }
      _m.compose(_p.set(x, y, z), _q.identity(), _s.setScalar(b.r));
      bolhas.setMatrixAt(i, _m);
    });
    bolhas.instanceMatrix.needsUpdate = true;
    neve.position.y = -0.05 * t;

    // polvo acorda (pulinho), respira e se camufla
    const acorda = janela(t, 1.8, 2.5, easing.outBack);
    const camu = janela(t, 12.9, 14.7);
    const achata = lerp(1, 0.86, camu);
    corpo.scale.set(lerp(0.75, 1, acorda), lerp(0.6, 1, acorda) * achata, lerp(0.75, 1, acorda));
    corpo.position.y = 0.25 * Math.sin(Math.PI * clamp((t - 1.8) / 0.7)) + 0.03 * Math.sin(1.4 * t);
    manto.scale.y = 1.22 * (1 + 0.03 * Math.sin(2.2 * t));
    corpo.updateMatrixWorld(true);

    // cor: pisca entre laranja e pedra e então assenta na cor da pedra
    const pisca = camu > 0 && camu < 1 ? 0.35 * Math.sin(24 * (t - 12.9)) * (1 - camu) : 0;
    const kc = clamp(camu + pisca);
    matPolvo.color.copy(COR_POLVO).lerp(COR_PEDRA, kc);
    matMancha.color.copy(COR_MANCHA).lerp(COR_MANCHA_PEDRA, kc);
    matVentosa.color.copy(COR_VENTOSA).lerp(COR_PEDRA, kc * 0.9);

    // olhos: piscam e acompanham a câmera
    const piscando = [2.7, 9.3, 18.75].some(tp => t > tp && t < tp + 0.16);
    _camLocal.copy(camera.position); corpo.worldToLocal(_camLocal);
    for (const o of olhos) {
      o.g.scale.y = piscando ? 0.12 : 1;
      const d = _p.copy(_camLocal).sub(o.g.position).normalize();
      o.pupila.position.set(d.x * 0.045, d.y * 0.04, 0.085);
    }

    // braços: desenrolam um a um, um deles acena mostrando as ventosas, todos se recolhem na camuflagem
    bracos.forEach((b, i) => {
      let ext = janela(t, inicioBraco(b), inicioBraco(b) + 0.85, easing.out);
      ext = lerp(ext, 0.42, camu);
      const ergue = i === ACENO ? pulso(t, 6.0, 10.2, 0.9, 1.0) : 0;
      formaBraco(b, t, ext, ergue);
    });
    // ventosas: aparecem em sequência da base para a ponta
    bracos.forEach((b, i) => {
      for (let j = 0; j < NV; j++) {
        const sn = 0.28 + 0.64 * (j / (NV - 1));
        const kf = sn * (NP - 1), k0 = Math.floor(kf), k1 = Math.min(NP - 1, k0 + 1), f = kf - k0;
        _p.lerpVectors(b.pontos[k0], b.pontos[k1], f);
        const T = b.tubo.tangentes[k0];
        _ventral.crossVectors(T, b.lado).normalize();
        const raio = lerp(b.raios[k0], b.raios[k1], f);
        _p.addScaledVector(_ventral, raio * 0.9);
        const pop = easing.outBack(clamp((t - (6.3 + j * 0.09)) / 0.28));
        _q.setFromUnitVectors(Y, _ventral);
        _s.set(raio * 0.62 * pop, raio * 0.62 * pop, raio * 0.62 * pop);
        _m.compose(_p, _q, _s);
        ventosas.setMatrixAt(i * NV + j, _m);
        if (i === ACENO && j === 6) _ancoraVentosa.copy(_p).applyMatrix4(corpo.matrixWorld);
      }
    });
    ventosas.instanceMatrix.needsUpdate = true;

    // peixe: entra pela direita, para, estranha, vai embora
    {
      const chega = janela(t, 15.8, 17.6, easing.out);
      const sai = janela(t, 19.2, DURACAO, easing.in);
      const x = lerp(lerp(5.5, 0.95, chega), -5.5, sai);
      peixe.position.set(x, 1.0 + 0.04 * Math.sin(t * 2.3) + 0.2 * sai, lerp(1.65, 1.2, sai));
      const parado = chega >= 1 && sai <= 0;
      peixe.rotation.y = parado ? 0.5 * Math.sin((t - 17.6) * 2.2) : 0;
      cauda.rotation.y = Math.sin(t * (parado ? 6 : 16)) * 0.45;
    }
  }

  return {
    duracao: DURACAO,
    canvas: palco.saida,
    info: () => palco.info(),
    quadro: (t, formato = 'jpeg') => palco.quadro(t, atualizar, DURACAO, formato),
  };
}
