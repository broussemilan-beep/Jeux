/*
 * MOTEUR D'APERÇU du studio VFX (three.js r134).
 *
 * Il joue une RECETTE (voir ../recettes.py) avec la sémantique de Roblox, et
 * rien de plus, pour qu'on ne juge jamais ici un effet que Roblox ne saurait
 * pas faire (fiches/VFX.md §5) :
 *  - particules : Emit / Rate, Lifetime, Speed, SpreadAngle, Acceleration,
 *    Drag (la vitesse est divisée par 2, Drag fois par seconde [DÉDUIT, seule
 *    lecture cohérente avec les recettes d'explosion]),
 *    NumberSequence linéaires avec enveloppe (un tirage par particule),
 *    ColorSequence, Orientation (FacingCamera, FacingCameraWorldUp,
 *    VelocityParallel, VelocityPerpendicular), Rotation / RotSpeed, Squash,
 *    flipbooks (grille, OneShot / Loop), LightEmission (additif), ZOffset,
 *    TimeScale (gel du hitstop) ;
 *  - meshes : MeshPart + texture qui DÉFILE (UV scrolling), échelle,
 *    transparence et rotation dans le temps ;
 *  - traînées (Trail) et faisceaux (Beam) : rubans texturés face caméra,
 *    Beam en Bézier avec défilement de texture ;
 *  - bloom (BloomEffect) animé dans le temps, flash d'écran, secousse
 *    directionnelle à graine fixe ;
 *  - orchestration : apparition, projection, collision -> onde + explosion.
 *
 * Tout est DÉTERMINISTE : chaque particule est calculée analytiquement à
 * partir de son instant de naissance et de sa graine. On peut donc se placer
 * à n'importe quel instant t (captures, critique, marqueurs d'animation).
 */
(function () {
  "use strict";
  const T = window.THREE;
  const VFX = (window.VFX = {});

  // ---------------------------------------------------------------- hasard
  function mulberry(a) {
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const U = (r, a, b) => a + (b - a) * r();
  const rng2 = (r, v) => (Array.isArray(v) ? U(r, v[0], v[1]) : v);

  // ---------------------------------------------------------- séquences
  // NumberSequence : [[t, v, enveloppe], ...] ; e = tirage par particule dans [-1, 1]
  function seq(s, t, e) {
    if (s == null) return 0;
    if (typeof s === "number") return s;
    if (t <= s[0][0]) return s[0][1] + (s[0][2] || 0) * (e || 0);
    for (let i = 1; i < s.length; i++) {
      if (t <= s[i][0]) {
        const a = s[i - 1], b = s[i], u = (t - a[0]) / Math.max(1e-6, b[0] - a[0]);
        return a[1] + (b[1] - a[1]) * u + ((a[2] || 0) + ((b[2] || 0) - (a[2] || 0)) * u) * (e || 0);
      }
    }
    const l = s[s.length - 1];
    return l[1] + (l[2] || 0) * (e || 0);
  }
  const hex = (h) => new T.Color(h);
  function cseq(s, t) {
    if (!s) return new T.Color(1, 1, 1);
    if (typeof s === "string") return hex(s);
    if (t <= s[0][0]) return hex(s[0][1]);
    for (let i = 1; i < s.length; i++) {
      if (t <= s[i][0]) {
        const a = s[i - 1], b = s[i], u = (t - a[0]) / Math.max(1e-6, b[0] - a[0]);
        return hex(a[1]).lerp(hex(b[1]), u);
      }
    }
    return hex(s[s.length - 1][1]);
  }

  // --------------------------------------------------------- ancres
  // Une ancre donne une position (et un repère) à l'instant t. Formes :
  //  {pos:[x,y,z], dir:[x,y,z]}            point fixe (dir = direction d'émission)
  //  "projectile"                            suit le projectile de la recette
  //  "impact"                                point d'arrivée du projectile
  function makeAnchors(rec) {
    const P = rec.projectile;
    const A = {};
    const v3 = (a) => new T.Vector3(a[0], a[1], a[2]);
    if (P) {
      const a = v3(P.de), b = v3(P.a), h = P.hauteur || 0;
      A.projectilePos = function (t) {
        const u = Math.min(1, Math.max(0, (t - P.t0) / (P.t1 - P.t0)));
        const e = P.acceleration ? u * u : u;               // part lentement, arrive vite
        const p = a.clone().lerp(b, e);
        p.y += h * 4 * e * (1 - e);
        return p;
      };
      A.projectileDir = function (t) {
        return A.projectilePos(Math.min(P.t1, t + 0.01)).sub(A.projectilePos(Math.max(P.t0, t - 0.01))).normalize();
      };
      A.impact = v3(P.a);
      A.impactDir = v3(P.a).sub(v3(P.de)).normalize();
    }
    A.resolve = function (anc, t) {
      if (anc === "projectile") return { pos: A.projectilePos(t), dir: A.projectileDir(t) };
      if (anc === "impact") return { pos: A.impact.clone(), dir: new T.Vector3(0, 1, 0), coup: A.impactDir.clone() };
      const o = anc || {};
      return { pos: v3(o.pos || [0, 0, 0]), dir: v3(o.dir || [0, 1, 0]).normalize(), coup: v3(o.coup || [0, 0, -1]).normalize() };
    };
    return A;
  }
  // repère orthonormé dont l'axe Y = d
  function basis(d) {
    const y = d.clone().normalize();
    const ref = Math.abs(y.y) < 0.95 ? new T.Vector3(0, 1, 0) : new T.Vector3(1, 0, 0);
    const x = new T.Vector3().crossVectors(ref, y).normalize();
    const z = new T.Vector3().crossVectors(x, y).normalize();
    return { x, y, z };
  }

  // ------------------------------------------------------- textures
  const TEX = {};
  VFX.loadTextures = function (map) {       // {nom: dataURI}
    const L = new T.TextureLoader();
    for (const k in map) {
      const t = L.load(map[k]);
      t.wrapS = t.wrapT = T.RepeatWrapping;
      // pas de conversion sRGB : toute la chaîne (bloom compris) travaille
      // sur les valeurs telles que peintes, et l'écran les affiche telles quelles
      TEX[k] = t;
    }
  };
  const MESH = {};
  VFX.loadMeshes = function (data) {
    for (const k in data) {
      const g = new T.BufferGeometry();
      const m = data[k];
      g.setAttribute("position", new T.Float32BufferAttribute(m.positions, 3));
      g.setAttribute("normal", new T.Float32BufferAttribute(m.normales, 3));
      g.setAttribute("uv", new T.Float32BufferAttribute(m.uv, 2));
      g.setIndex(m.indices);
      MESH[k] = g;
    }
  };

  // --------------------------------------------- matériau additif / normal
  function spriteMat(tex, additif) {
    return new T.ShaderMaterial({
      uniforms: { map: { value: tex } },
      vertexShader: "attribute vec4 couleur; varying vec4 vC; varying vec2 vUv; void main(){ vC=couleur; vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}",
      fragmentShader: "uniform sampler2D map; varying vec4 vC; varying vec2 vUv; void main(){ vec4 t=texture2D(map,vUv); gl_FragColor=vec4(t.rgb*vC.rgb, t.a*vC.a); if(gl_FragColor.a<0.004) discard; }",
      transparent: true, depthWrite: false, side: T.DoubleSide,
      blending: additif ? T.AdditiveBlending : T.NormalBlending,
    });
  }

  // =================================================== couche PARTICULES
  function Particules(L, anchors, seed) {
    const tex = TEX[L.texture];
    const n = L.emit != null ? L.emit : Math.ceil((L.rate || 0) * (L.duree_emission || 0.001));
    const born = [];
    const r = mulberry(seed);
    for (let i = 0; i < n; i++) {
      const tb = L.emit != null ? L.t0 : L.t0 + i / L.rate;
      born.push({ tb, r: mulberry((seed * 7919 + i * 104729) | 0) });
    }
    const maxN = Math.max(1, n);
    const geo = new T.BufferGeometry();
    const pos = new Float32Array(maxN * 12), uv = new Float32Array(maxN * 8), col = new Float32Array(maxN * 16);
    const idx = [];
    for (let i = 0; i < maxN; i++) idx.push(i * 4, i * 4 + 1, i * 4 + 2, i * 4, i * 4 + 2, i * 4 + 3);
    geo.setAttribute("position", new T.BufferAttribute(pos, 3));
    geo.setAttribute("uv", new T.BufferAttribute(uv, 2));
    geo.setAttribute("couleur", new T.BufferAttribute(col, 4));
    geo.setIndex(idx);
    const mesh = new T.Mesh(geo, spriteMat(tex, (L.light_emission == null ? 1 : L.light_emission) >= 0.5));
    mesh.frustumCulled = false;
    mesh.renderOrder = 10 + (L.zoffset || 0);
    // tirages figés par particule (déterminisme)
    const P = born.map((b) => {
      const q = b.r;
      const life = rng2(q, L.lifetime || [1, 1]);
      const speed = rng2(q, L.speed || 0);
      const sx = ((L.spread || [0, 0])[0] * Math.PI) / 180, sy = ((L.spread || [0, 0])[1] * Math.PI) / 180;
      const ax = U(q, -sx, sx), ay = U(q, -sy, sy);
      const env = U(q, -1, 1);
      const rot = rng2(q, L.rotation || 0), rotSpeed = rng2(q, L.rotspeed || 0);
      const offs = new T.Vector3();
      if (L.forme && L.forme.sphere) {             // volume sphérique
        const u = q() * 2 - 1, th = q() * Math.PI * 2, rr = L.forme.sphere * Math.cbrt(q());
        offs.set(Math.sqrt(1 - u * u) * Math.cos(th) * rr, u * rr, Math.sqrt(1 - u * u) * Math.sin(th) * rr);
      } else if (L.forme && L.forme.anneau) {      // Disc + ShapePartial = 1 : sur le bord
        const th = q() * Math.PI * 2;
        offs.set(Math.cos(th) * L.forme.anneau, 0, Math.sin(th) * L.forme.anneau);
      }
      const frame0 = Math.floor(q() * 64);
      return { tb: b.tb, life, speed, ax, ay, env, rot, rotSpeed, offs, frame0 };
    });
    const drag = L.drag || 0, k = drag * Math.LN2;
    const acc = new T.Vector3().fromArray(L.accel || [0, 0, 0]);
    const g = (L.flipbook && L.flipbook.grille) || 1, nImg = (L.flipbook && L.flipbook.images) || g * g;
    const cam = new T.Vector3(), tmp = new T.Vector3();

    function state(p, t, anc) {
      const age = (t - p.tb) * (L.timescale || 1);
      if (age < 0 || age > p.life) return null;
      const B = basis(anc.dir);
      // direction : écart (SpreadAngle) autour de l'axe d'émission
      const d = B.y.clone().applyAxisAngle(B.z, p.ax).applyAxisAngle(B.x, p.ay).normalize();
      const v0 = d.multiplyScalar(p.speed);
      let x, v;
      if (k > 1e-6) {
        const e = Math.exp(-k * age);
        x = acc.clone().multiplyScalar(age / k).add(v0.clone().sub(acc.clone().divideScalar(k)).multiplyScalar((1 - e) / k));
        v = acc.clone().divideScalar(k).add(v0.clone().sub(acc.clone().divideScalar(k)).multiplyScalar(e));
      } else {
        x = v0.clone().multiplyScalar(age).add(acc.clone().multiplyScalar(0.5 * age * age));
        v = v0.clone().add(acc.clone().multiplyScalar(age));
      }
      const origin = L.bloque_a_l_ancre ? anc.pos : p.anc0;
      return { pos: origin.clone().add(p.offs).add(x), vel: v, age, f: age / p.life };
    }

    return {
      obj: mesh,
      update(t, camera, gel) {
        camera.getWorldPosition(cam);
        const camRight = new T.Vector3().setFromMatrixColumn(camera.matrixWorld, 0);
        const camUp = new T.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
        let m = 0;
        for (let i = 0; i < P.length; i++) {
          const p = P[i];
          const tt = gel ? gel(t, p.tb) : t;
          if (tt < p.tb || tt > p.tb + p.life / (L.timescale || 1)) continue;
          if (!p.anc0) p.anc0 = anchors.resolve(L.ancre, p.tb).pos;
          const anc = anchors.resolve(L.ancre, tt);
          const s = state(p, tt, anc);
          if (!s) continue;
          const size = Math.max(0, seq(L.size, s.f, p.env));
          const tr = Math.min(1, Math.max(0, seq(L.transparency, s.f, p.env)));
          const sq = seq(L.squash, s.f, 0);
          let w = size, h = size;
          if (sq) { h = size * Math.pow(2, sq); w = size * Math.pow(2, -sq); }   // Squash > 0 : plus haute, plus fine [DÉDUIT]
          const c = cseq(L.color, s.f);
          // repère du quad selon l'orientation
          let rx, ry;
          const toCam = tmp.copy(cam).sub(s.pos).normalize();
          const o = L.orientation || "FacingCamera";
          if (o === "VelocityParallel" && s.vel.lengthSq() > 1e-8) {
            ry = s.vel.clone().normalize(); rx = new T.Vector3().crossVectors(ry, toCam).normalize();
          } else if (o === "VelocityPerpendicular" && s.vel.lengthSq() > 1e-8) {
            const Bv = basis(s.vel); rx = Bv.x; ry = Bv.z;
          } else if (o === "FacingCameraWorldUp") {
            ry = new T.Vector3(0, 1, 0); rx = new T.Vector3().crossVectors(ry, toCam).normalize();
          } else { rx = camRight.clone(); ry = camUp.clone(); }
          const a = ((p.rot + p.rotSpeed * s.age) * Math.PI) / 180;
          const ca = Math.cos(a), sa = Math.sin(a);
          const X = rx.clone().multiplyScalar(ca).add(ry.clone().multiplyScalar(sa)).multiplyScalar(w / 2);
          const Y = ry.clone().multiplyScalar(ca).sub(rx.clone().multiplyScalar(sa)).multiplyScalar(h / 2);
          const ctr = s.pos.clone().add(toCam.clone().multiplyScalar(L.zoffset || 0));
          const corners = [ctr.clone().sub(X).sub(Y), ctr.clone().add(X).sub(Y), ctr.clone().add(X).add(Y), ctr.clone().sub(X).add(Y)];
          // image du flipbook
          let fr = 0;
          if (g > 1) {
            const mode = (L.flipbook && L.flipbook.mode) || "OneShot";
            if (mode === "OneShot") fr = Math.min(nImg - 1, Math.floor(s.f * nImg));
            else fr = (Math.floor(s.age * Math.min(30, L.flipbook.fps || 24)) + (L.flipbook.depart_aleatoire ? p.frame0 : 0)) % nImg;
          }
          const cx = fr % g, cy = Math.floor(fr / g);
          const u0 = cx / g, u1 = (cx + 1) / g, v1 = 1 - cy / g, v0 = 1 - (cy + 1) / g;
          const uvs = [u0, v0, u1, v0, u1, v1, u0, v1];
          for (let j = 0; j < 4; j++) {
            pos.set([corners[j].x, corners[j].y, corners[j].z], m * 12 + j * 3);
            uv.set([uvs[j * 2], uvs[j * 2 + 1]], m * 8 + j * 2);
            col.set([c.r * (L.brightness || 1), c.g * (L.brightness || 1), c.b * (L.brightness || 1), 1 - tr], m * 16 + j * 4);
          }
          m++;
        }
        geo.setDrawRange(0, m * 6);
        geo.attributes.position.needsUpdate = true; geo.attributes.uv.needsUpdate = true; geo.attributes.couleur.needsUpdate = true;
        return m;
      },
    };
  }

  // ======================================================== couche MESH
  function MeshCouche(L, anchors) {
    const mat = new T.ShaderMaterial({
      uniforms: { map: { value: TEX[L.texture] || null }, has: { value: TEX[L.texture] ? 1 : 0 },
        off: { value: new T.Vector2() }, rep: { value: new T.Vector2().fromArray(L.repetition || [1, 1]) },
        col: { value: new T.Color() }, alpha: { value: 1 }, fres: { value: L.bord || 0 } },
      vertexShader: "varying vec2 vUv; varying float vF; uniform float fres; void main(){ vUv=uv; vec4 mv=modelViewMatrix*vec4(position,1.0); vec3 n=normalize(normalMatrix*normal); vF=1.0-abs(dot(n,normalize(-mv.xyz))); gl_Position=projectionMatrix*mv; }",
      fragmentShader: "uniform sampler2D map; uniform float has; uniform vec2 off; uniform vec2 rep; uniform vec3 col; uniform float alpha; uniform float fres; varying vec2 vUv; varying float vF; void main(){ vec4 t = has>0.5 ? texture2D(map, vUv*rep+off) : vec4(1.0); float a=t.a*alpha*mix(1.0, pow(vF,1.5)*1.6, fres); gl_FragColor=vec4(t.rgb*col, a); if(a<0.004) discard; }",
      transparent: true, depthWrite: false, side: T.DoubleSide,
      blending: (L.light_emission == null ? 1 : L.light_emission) >= 0.5 ? T.AdditiveBlending : T.NormalBlending,
    });
    const m = new T.Mesh(MESH[L.mesh], mat);
    m.frustumCulled = false;
    m.renderOrder = 5 + (L.zoffset || 0);
    return {
      obj: m,
      update(t) {
        const a = (t - L.t0) / L.duree;
        if (a < 0 || a > 1) { m.visible = false; return 0; }
        m.visible = true;
        const anc = anchors.resolve(L.ancre, t);
        m.position.copy(anc.pos).add(new T.Vector3().fromArray(L.decalage || [0, 0, 0]));
        // orientation : "sol" (Y monde), "coup" (Y = sens du coup), "direction" (Y = dir de l'ancre)
        const o = L.orientation || "sol";
        const up = o === "coup" ? anc.coup || anc.dir : o === "direction" ? anc.dir : new T.Vector3(0, 1, 0);
        m.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), up.clone().normalize());
        if (L.inclinaison) m.quaternion.multiply(new T.Quaternion().setFromEuler(new T.Euler(...L.inclinaison.map((d) => (d * Math.PI) / 180))));
        m.rotateY(((L.rotation_vitesse || 0) * (t - L.t0) * Math.PI) / 180 + ((L.rotation || 0) * Math.PI) / 180);
        const e = L.echelle;
        if (e && Array.isArray(e[0]) && Array.isArray(e[0][1])) {
          const sx = seq(e.map((k) => [k[0], k[1][0]]), a), sy = seq(e.map((k) => [k[0], k[1][1]]), a), sz = seq(e.map((k) => [k[0], k[1][2]]), a);
          m.scale.set(sx, sy, sz);
        } else { const s = seq(e || 1, a); m.scale.set(s, s, s); }
        mat.uniforms.off.value.set(((L.defilement || [0, 0])[0] * (t - L.t0)) % 1, ((L.defilement || [0, 0])[1] * (t - L.t0)) % 1);
        mat.uniforms.col.value.copy(cseq(L.color, a)).multiplyScalar(L.brightness || 1);
        mat.uniforms.alpha.value = 1 - Math.min(1, Math.max(0, seq(L.transparency, a)));
        return 1;
      },
    };
  }

  // ===================================================== couche RUBAN
  // Trail (suit une ancre en mouvement) et Beam (Bézier entre deux points).
  function Ruban(L, anchors) {
    const N = L.segments || 24;
    const geo = new T.BufferGeometry();
    const pos = new Float32Array((N + 1) * 2 * 3), uv = new Float32Array((N + 1) * 2 * 2), col = new Float32Array((N + 1) * 2 * 4);
    const idx = [];
    for (let i = 0; i < N; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    geo.setAttribute("position", new T.BufferAttribute(pos, 3));
    geo.setAttribute("uv", new T.BufferAttribute(uv, 2));
    geo.setAttribute("couleur", new T.BufferAttribute(col, 4));
    geo.setIndex(idx);
    const m = new T.Mesh(geo, spriteMat(TEX[L.texture], (L.light_emission == null ? 1 : L.light_emission) >= 0.5));
    m.frustumCulled = false; m.renderOrder = 8;
    const cam = new T.Vector3();
    function pointsTrail(t) {
      const out = [];
      const life = L.lifetime || 0.3;
      for (let i = 0; i <= N; i++) {
        const tt = Math.max(L.t0, t - (life * i) / N);
        out.push({ p: anchors.resolve(L.ancre, Math.min(tt, L.t1_ancre || 1e9)).pos, f: i / N, tt });
      }
      return out;
    }
    function pointsBeam() {
      const a = new T.Vector3().fromArray(L.de), b = new T.Vector3().fromArray(L.a);
      const c0 = a.clone().add(new T.Vector3().fromArray(L.courbe0 || [0, 0, 0]));
      const c1 = b.clone().add(new T.Vector3().fromArray(L.courbe1 || [0, 0, 0]));
      const out = [];
      for (let i = 0; i <= N; i++) {
        const u = i / N, v = 1 - u;
        const p = a.clone().multiplyScalar(v * v * v).add(c0.clone().multiplyScalar(3 * v * v * u)).add(c1.clone().multiplyScalar(3 * v * u * u)).add(b.clone().multiplyScalar(u * u * u));
        out.push({ p, f: u });
      }
      return out;
    }
    return {
      obj: m,
      update(t, camera) {
        const fin = L.type === "trail" ? L.t1 + (L.lifetime || 0.3) : L.t0 + L.duree;
        if (t < L.t0 || t > fin) { m.visible = false; return 0; }
        m.visible = true;
        camera.getWorldPosition(cam);
        const pts = L.type === "trail" ? pointsTrail(t) : pointsBeam();
        const a = L.type === "trail" ? 0 : (t - L.t0) / L.duree;
        const glob = 1 - Math.min(1, Math.max(0, seq(L.transparency_temps || 0, a)));
        const scroll = (L.vitesse_texture || 0) * (t - L.t0);
        for (let i = 0; i <= N; i++) {
          const p = pts[i].p;
          const nxt = pts[Math.min(N, i + 1)].p, prv = pts[Math.max(0, i - 1)].p;
          const tan = nxt.clone().sub(prv);
          if (tan.lengthSq() < 1e-10) tan.set(0, 0, 1);
          const side = new T.Vector3().crossVectors(tan.normalize(), cam.clone().sub(p).normalize()).normalize();
          const f = pts[i].f;
          const w = seq(L.largeur || 1, f) / 2 * (L.type === "trail" && t > L.t1 ? 1 : 1);
          let fade = 1 - Math.min(1, Math.max(0, seq(L.transparency, f)));
          if (L.type === "trail" && pts[i].tt <= L.t0 + 1e-6 && i > 0) fade = 0;
          const c = cseq(L.color, f);
          const A = p.clone().add(side.clone().multiplyScalar(w)), B = p.clone().sub(side.clone().multiplyScalar(w));
          pos.set([A.x, A.y, A.z, B.x, B.y, B.z], i * 6);
          const uu = (L.type === "trail" ? f : f * (L.repetition || 1)) - scroll;
          uv.set([uu, 1, uu, 0], i * 4);
          const br = L.brightness || 1;
          col.set([c.r * br, c.g * br, c.b * br, fade * glob, c.r * br, c.g * br, c.b * br, fade * glob], i * 8);
        }
        geo.attributes.position.needsUpdate = true; geo.attributes.uv.needsUpdate = true; geo.attributes.couleur.needsUpdate = true;
        return 1;
      },
    };
  }

  // ================================================== couche PROJECTILE
  // l'objet qui voyage : un mesh (sphère d'énergie...) entre t0 et t1, qui
  // DISPARAÎT à la collision
  function Projectile(P, anchors) {
    const L = Object.assign({ t0: P.t0, duree: P.t1 - P.t0, ancre: "projectile", orientation: "direction" }, P.visuel || {});
    const c = MeshCouche(L, anchors);
    return { obj: c.obj, update(t) { return t >= P.t1 ? ((c.obj.visible = false), 0) : c.update(t); } };
  }

  // ============================================================ BLOOM
  // BloomEffect Roblox : Intensity, Size, Threshold. Passe maison (le module
  // three.js n'est pas disponible ici) : seuil -> flou gaussien à 2 échelles
  // -> ajout.
  function Bloom(renderer, w, h) {
    // cibles 8 bits : les cibles en demi-flottant donnaient des carrés noirs
    // (valeurs invalides) sous le rendu logiciel. En 8 bits, c'est portable
    // et déterministe ; les valeurs > 1 saturent, le seuil fait le reste.
    const rt = (s) => new T.WebGLRenderTarget(Math.max(1, (w / s) | 0), Math.max(1, (h / s) | 0));
    const scene = rt(1), a2 = rt(2), b2 = rt(2), a4 = rt(4), b4 = rt(4);
    const cam = new T.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const quad = new T.Mesh(new T.PlaneGeometry(2, 2));
    const sc = new T.Scene(); sc.add(quad);
    const vs = "varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.0,1.0); }";
    const seuil = new T.ShaderMaterial({ uniforms: { t: { value: null }, thr: { value: 0.8 } }, vertexShader: vs,
      fragmentShader: "uniform sampler2D t; uniform float thr; varying vec2 vUv; void main(){ vec3 c=texture2D(t,vUv).rgb; float l=max(c.r,max(c.g,c.b)); gl_FragColor=vec4(c*max(0.0,l-thr)/max(l,1e-4),1.0); }" });
    const flou = new T.ShaderMaterial({ uniforms: { t: { value: null }, d: { value: new T.Vector2() } }, vertexShader: vs,
      fragmentShader: "uniform sampler2D t; uniform vec2 d; varying vec2 vUv; void main(){ vec3 c=texture2D(t,vUv).rgb*0.227; c+=texture2D(t,vUv+d*1.385).rgb*0.316; c+=texture2D(t,vUv-d*1.385).rgb*0.316; c+=texture2D(t,vUv+d*3.231).rgb*0.070; c+=texture2D(t,vUv-d*3.231).rgb*0.070; gl_FragColor=vec4(c,1.0); }" });
    const mix = new T.ShaderMaterial({ uniforms: { s: { value: null }, b1: { value: null }, b2: { value: null }, k: { value: 0 }, flash: { value: new T.Vector4(1, 1, 1, 0) } }, vertexShader: vs,
      fragmentShader: "uniform sampler2D s; uniform sampler2D b1; uniform sampler2D b2; uniform float k; uniform vec4 flash; varying vec2 vUv; void main(){ vec3 c=texture2D(s,vUv).rgb + k*(texture2D(b1,vUv).rgb*0.6+texture2D(b2,vUv).rgb*0.9); c=mix(c, flash.rgb, flash.a); gl_FragColor=vec4(c,1.0); }" });
    function pass(mat, target) { quad.material = mat; renderer.setRenderTarget(target); renderer.render(sc, cam); }
    return {
      render(scene3, camera, p) {           // p = {intensite, seuil, taille, flash:[r,g,b,a]}
        renderer.setRenderTarget(scene); renderer.render(scene3, camera);
        seuil.uniforms.t.value = scene.texture; seuil.uniforms.thr.value = p.seuil; pass(seuil, a2);
        const sz = p.taille || 1;
        for (const [A, B, W, H] of [[a2, b2, a2.width, a2.height]]) {
          flou.uniforms.t.value = A.texture; flou.uniforms.d.value.set(sz / W, 0); pass(flou, B);
          flou.uniforms.t.value = B.texture; flou.uniforms.d.value.set(0, sz / H); pass(flou, A);
        }
        flou.uniforms.t.value = a2.texture; flou.uniforms.d.value.set((sz * 2) / a4.width, 0); pass(flou, b4);
        flou.uniforms.t.value = b4.texture; flou.uniforms.d.value.set(0, (sz * 2) / a4.height); pass(flou, a4);
        mix.uniforms.s.value = scene.texture; mix.uniforms.b1.value = a2.texture; mix.uniforms.b2.value = a4.texture;
        mix.uniforms.k.value = p.intensite; mix.uniforms.flash.value.fromArray(p.flash || [1, 1, 1, 0]);
        pass(mix, null);
      },
    };
  }

  // ======================================================= la RECETTE
  VFX.Effet = function (rec, scene) {
    const anchors = makeAnchors(rec);
    const couches = [];
    let seed = rec.graine || 1;
    const gels = rec.gels || [];              // [[debut, duree]] : TimeScale 0 (hitstop)
    // temps « effet » vu par une particule née à tb : le gel suspend son âge
    function gel(t, tb) {
      if (t < tb) return t;                   // pas encore née : on ne touche à rien
      let tt = t;
      for (const [g0, d] of gels) {
        if (tb < g0 + d && t > g0) tt -= Math.min(t, g0 + d) - Math.max(g0, tb);
      }
      return Math.max(tb, tt);
    }
    if (rec.projectile) couches.push(Projectile(rec.projectile, anchors));
    for (const L of rec.couches) {
      seed = (seed * 16807) % 2147483647;
      let c = null;
      if (L.type === "particules") c = Particules(L, anchors, seed);
      else if (L.type === "mesh") c = MeshCouche(L, anchors);
      else if (L.type === "trail" || L.type === "beam") c = Ruban(L, anchors);
      if (c) { c.L = L; scene.add(c.obj); couches.push(c); }
    }
    return {
      duree: rec.duree,
      couches,
      update(t, camera) {
        let n = 0;
        for (const c of couches) n += c.update(t, camera, c.L && c.L.type === "particules" && c.L.gel !== false ? gel : null) || 0;
        return n;
      },
      post(t) {                               // bloom, flash d'écran, secousse
        const b = rec.bloom || {};
        const out = { intensite: seq(b.intensite || 0.6, t / rec.duree), seuil: b.seuil == null ? 0.8 : b.seuil, taille: b.taille || 2, flash: [1, 1, 1, 0] };
        for (const f of rec.flashs || []) {
          const a = (t - f.t0) / f.duree;
          if (a >= 0 && a <= 1) { const c = hex(f.couleur || "#ffffff"); out.flash = [c.r, c.g, c.b, 1 - seq(f.transparency || [[0, 0], [1, 1]], a)]; }
        }
        let sh = new T.Vector3();
        for (const s of rec.secousses || []) {
          const a = t - s.t0;
          if (a >= 0 && a <= s.duree) {
            const r = mulberry(((s.graine || 9) * 1000 + Math.floor(a * 60)) | 0);
            const amp = s.amplitude * Math.pow(1 - a / s.duree, 2);   // trauma²
            const d = new T.Vector3().fromArray(s.direction || [0, -1, 0]).normalize();
            sh.add(d.multiplyScalar(amp * (r() * 2 - 1) * 0.6 + amp * 0.4 * Math.cos(a * 70)));
          }
        }
        out.secousse = sh;
        return out;
      },
    };
  };
  VFX.Bloom = Bloom;
  VFX.seq = seq;
})();
