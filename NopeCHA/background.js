(() => {
  {
    let t = chrome.runtime
      .getManifest()
      .content_scripts.filter((r) => r.js.includes("eventhook.js"))
      .map((r) => r.matches);
    chrome.scripting.getRegisteredContentScripts().then((r) => {
      r.length ||
        chrome.scripting.registerContentScripts([
          {
            id: "1",
            matches: t.flat(),
            js: ["eventhook/loader.js"],
            allFrames: !0,
            runAt: "document_start",
            world: "MAIN",
          },
        ]);
    });
  }
  var a = chrome;
  var k = "https://api.nopecha.com",
    i = "https://www.nopecha.com",
    D = "https://developers.nopecha.com",
    g = {
      doc: {
        url: D,
        automation: { url: `${D}/guides/extension_advanced/#automation-build` },
      },
      api: {
        url: k,
        recognition: { url: `${k}/recognition` },
        status: { url: `${k}/status` },
      },
      www: {
        url: i,
        annoucement: { url: `${i}/json/announcement.json` },
        demo: {
          url: `${i}/demo`,
          hcaptcha: { url: `${i}/demo/hcaptcha` },
          recaptcha: { url: `${i}/demo/recaptcha` },
          funcaptcha: { url: `${i}/demo/funcaptcha` },
          awscaptcha: { url: `${i}/demo/awscaptcha` },
          turnstile: { url: `${i}/demo/turnstile` },
          textcaptcha: { url: `${i}/demo/textcaptcha` },
          perimeterx: { url: `${i}/demo/perimeterx` },
        },
        manage: { url: `${i}/manage` },
        pricing: { url: `${i}/pricing` },
        setup: { url: `${i}/setup` },
      },
      discord: { url: `${i}/discord` },
      github: { url: `${i}/github`, release: { url: `${i}/github/release` } },
    };
  var Z = "en-US",
    ee = "en";
  {
    let e = function (t, r, o, n) {
      return {
        id: n,
        priority: 1,
        action: {
          type: "redirect",
          redirect: {
            transform: {
              queryTransform: { addOrReplaceParams: [{ key: t, value: r }] },
            },
          },
        },
        condition: { regexFilter: o, resourceTypes: ["sub_frame"] },
      };
    };
    a.declarativeNetRequest.updateDynamicRules({
      addRules: [
        e(
          "hl",
          Z,
          "^https?://[^\\.]*\\.(google\\.com|recaptcha\\.net)/recaptcha",
          1
        ),
        e(
          "lang",
          ee,
          "^https?://[^\\.]*\\.(funcaptcha\\.com?|arkoselabs\\.c(om|n)|arkose\\.com\\.cn)/fc/gc/",
          2
        ),
      ],
      removeRuleIds: [1, 2],
    });
  }
  var d = new Map();
  chrome.tabs.onUpdated.addListener((e, t) => {
    (d.has(e) && !("url" in t)) || d.set(e, new Set());
  });
  chrome.tabs.onRemoved.addListener((e) => {
    d.delete(e);
  });
  async function U([e], t) {
    let r = t.tab?.id;
    if (!r)
      return console.warn("[@nope/background/tabs] unable to figure out tabId");
    d.has(r) || d.set(r, new Set()), d.get(r).add(e);
  }
  async function j() {
    let e = await new Promise((t) => {
      a.tabs.query({ active: !0, currentWindow: !0 }, ([r]) => {
        t(r);
      });
    });
    return d.has(e.id) ? [...d.get(e.id)] : [];
  }
  var h = {
    version: 16,
    key: "",
    keys: [],
    enabled: !0,
    disabled_hosts: [],
    hcaptcha_auto_open: !0,
    hcaptcha_auto_solve: !0,
    hcaptcha_solve_delay: !0,
    hcaptcha_solve_delay_time: 3e3,
    recaptcha_auto_open: !0,
    recaptcha_auto_solve: !0,
    recaptcha_solve_delay: !0,
    recaptcha_solve_delay_time: 2e3,
    funcaptcha_auto_open: !0,
    funcaptcha_auto_solve: !0,
    funcaptcha_solve_delay: !0,
    funcaptcha_solve_delay_time: 1e3,
    awscaptcha_auto_open: !1,
    awscaptcha_auto_solve: !1,
    awscaptcha_solve_delay: !0,
    awscaptcha_solve_delay_time: 1e3,
    turnstile_auto_solve: !0,
    turnstile_solve_delay: !0,
    turnstile_solve_delay_time: 1e3,
    perimeterx_auto_solve: !1,
    perimeterx_solve_delay: !0,
    perimeterx_solve_delay_time: 1e3,
    textcaptcha_auto_solve: !1,
    textcaptcha_solve_delay: !0,
    textcaptcha_solve_delay_time: 100,
    textcaptcha_image_selector: "",
    textcaptcha_input_selector: "",
  };
  var _ = a.action,
    x = !0;
  function S(e) {
    if (e === x) return;
    x = e;
    let t = e ? "" : "g",
      r = [
        new Promise((o) => {
          _.setIcon(
            {
              path: Object.fromEntries(
                [16, 32, 48, 128].map((n) => [n, `/icon/${n}${t}.png`])
              ),
            },
            o
          );
        }),
      ];
    return (
      y &&
        r.push(
          new Promise((o) => {
            _.setBadgeText({ text: e ? y : "" }, o);
          })
        ),
      Promise.all(r)
    );
  }
  var y = "";
  function w(e, t) {
    if (e !== y)
      return (
        (y = e),
        Promise.all([
          new Promise((r) => {
            if (!x) return r();
            _.setBadgeText({ text: e }, r);
          }),
          new Promise((r) => {
            _.setBadgeBackgroundColor({ color: t }, r);
          }),
        ])
      );
  }
  function q(e, t) {
    return t.tab.url;
  }
  function R() {
    return new Promise((e) => {
      a.tabs.query({ active: !0, currentWindow: !0 }, ([t]) => e(t));
    });
  }
  async function m() {
    return (await R()).id;
  }
  async function J() {
    let e = await R();
    return e && e.url && new URL(e.url).href;
  }
  async function N() {
    let e = await R();
    return JSON.stringify(e);
  }
  var B = new Set(),
    P = new Set();
  a.runtime.onConnect.addListener((e) => {
    e.name === "stream"
      ? (B.add(e),
        e.onDisconnect.addListener(() => {
          B.delete(e);
        }))
      : e.name === "broadcast" &&
        (P.add(e),
        e.onDisconnect.addListener(() => {
          P.delete(e);
        }));
  });
  function M(e) {
    B.forEach((t) => t.postMessage(e));
  }
  async function F(e) {
    let t = await m();
    (e = { data: e, event: "broadcast" }),
      P.forEach((r) => {
        r.sender?.tab?.id !== void 0 &&
          t === r.sender?.tab?.id &&
          r.postMessage(e);
      });
  }
  var I = new Promise((e) => {
    a.storage.local.get("settings", (t) => {
      if (!t?.settings) return e(h);
      let { settings: r } = t;
      r.version !== h.version && (r = { ...h, key: r.key }),
        r.enabled || S(!1),
        e(r);
    });
  });
  function v() {
    return I;
  }
  async function O(e) {
    let t = { ...(await I), ...e };
    return (
      S(t.enabled),
      new Promise((r) => {
        a.storage.local.set({ settings: t }, () => {
          (I = Promise.resolve(t)),
            M({ event: "settingsUpdate", settings: e }),
            r(null);
        });
      })
    );
  }
  function E() {
    let e;
    return (t) => e || ((e = t().finally(() => (e = void 0))), e);
  }
  var H,
    te = E();
  function A() {
    return te(() => oe());
  }
  async function V() {
    return H;
  }
  var re = a.runtime.getManifest().version;
  async function oe() {
    let e = new URLSearchParams();
    e.append("v", re);
    let t = (await v()).key;
    t && e.append("key", t);
    let r = `${g.api.status.url}?${e.toString()}`,
      o,
      n = null;
    try {
      (n = await fetch(r)), (o = await n.json());
    } catch (s) {
      console.error(
        "[@nope/background/api/status] failed to fetch status",
        n,
        s
      ),
        (o = {
          error: -1,
          message: n
            ? n.status === 522
              ? "Server not responding"
              : n.status === 502
              ? "Server has routing issues"
              : `Unknown server error: ${n.status}`
            : "Server connection failure.",
        });
    }
    return (
      n &&
        !n.ok &&
        (!o || !("error" in o)) &&
        (console.error("[@nope/background/api/status] received non 2xx", n, o),
        (o = { error: -1, message: `Server error: ${n.status}` })),
      (H = o),
      "error" in o
        ? w("ERR", "#FDE047")
        : typeof o.credit == "number" && typeof o.quota == "number"
        ? w(
            o.credit >= 9999
              ? `${Math.floor((o.credit / o.quota) * 100)}%`
              : o.credit.toString(),
            o.credit ? "#0a95ff" : "#FB7185"
          )
        : w("", "#fff0"),
      o
    );
  }
  A();
  function L(e) {
    return new Promise((t) => setTimeout(t, e));
  }
  function T(e, t = 2166136261) {
    let r = t;
    for (let o of e) (r ^= o), (r += r << 1);
    return r >>> 0;
  }
  var ne = 30,
    f = [];
  function $(e, t) {
    let r;
    if (!t.method || t.method === "GET") {
      let n = new URLSearchParams(e.split("?")[1]).get("id");
      if (!n) return;
      let s = f.find((c) => {
        let u = c.postres[c.postres.length - 1];
        return !u?.responseBody || !("data" in u.responseBody)
          ? !1
          : u?.responseBody?.data === n;
      });
      s && ((r = s.id), (s.getreq = { time: +new Date(), url: e, options: t }));
    } else
      for (
        r = "" + [+new Date(), performance.now(), Math.random()],
          f.push({
            id: r,
            postreq: { time: +new Date(), url: e, options: t },
            getreq: { time: 0, url: "", options: {} },
            postres: [],
            getres: [],
          });
        f.length > ne;

      )
        f.shift();
    return r;
  }
  function b(e, t) {
    let r = f.find((o) => o.id === e);
    r &&
      (r.getreq.time
        ? (r.getres.push({ time: +new Date(), ...t }),
          t.responseBody &&
            "data" in t.responseBody &&
            (r.answer = t.responseBody.data))
        : r.postres.push({ time: +new Date(), ...t }));
  }
  function W() {
    return JSON.stringify(f);
  }
  var ae = [15, 16, 12, 10, 17];
  async function G(e) {
    let t = new Headers();
    t.append("accept", "application/json"),
      t.append("content-type", "application/json");
    let r =
      typeof e.v == "string"
        ? T(e.v.split("").map((c) => c.charCodeAt(0)))
        : -1;
    e.key &&
      e.key !== "undefined" &&
      t.append("authorization", `Bearer ${e.key}`);
    let o;
    for (let c = 30; c > 0 && r === 2385114811; c--) {
      let u = $(g.api.url, { method: "POST", headers: t, body: e }),
        l = await fetch(g.api.url, {
          method: "POST",
          headers: t,
          body: JSON.stringify(e),
        });
      if (l.status >= 500) {
        b(u, { response: l, attempts: c });
        continue;
      }
      let p = await l.json();
      if ((b(u, { response: l, responseBody: p, attempts: c }), "error" in p)) {
        if (ae.includes(p.error)) return p;
        p.error !== 11 &&
          console.warn("[@nope/background/api/recognition] unknown error", p),
          await L(2e3);
      } else {
        o = p.data;
        break;
      }
    }
    if (!o) return { error: -1, message: "Server timeout" };
    t.delete("content-type");
    let n,
      s = `${g.api.url}?id=${o}&key=${e.key}`;
    for (let c = 60; c > 0; c--) {
      n = $(s, { headers: t });
      let u = await fetch(s, { headers: t });
      if (u.status >= 500) {
        b(n, { response: u, attempts: c });
        continue;
      }
      let l = await u.json();
      if ((b(n, { response: u, responseBody: l, attempts: c }), "error" in l))
        l.error !== 14 &&
          console.warn("[@nope/background/api/recognition] unknown error", l),
          await L(1e3);
      else return l;
    }
    return n && b(n, { failed: !0 }), { error: -1, message: "Server timeout" };
  }
  async function K([e, t]) {
    let r = await fetch(e, t);
    return {
      headers: Object.fromEntries(r.headers.entries()),
      status: r.status,
      ok: r.ok,
      text: await r.text(),
    };
  }
  async function X([e, t]) {
    let r = await fetch(e, t),
      o = await r.blob(),
      n = new FileReader();
    return (
      await new Promise((s) => {
        n.addEventListener("load", s), n.readAsDataURL(o);
      }),
      {
        headers: Object.fromEntries(r.headers.entries()),
        status: r.status,
        ok: r.ok,
        data: n.result,
      }
    );
  }
  function C(e) {
    let t = (
      "68deee3b46050627b187a31ec5204173fb5d74e2bb6e5ffeab6b7595130fab39" + e
    )
      .split("")
      .map((r) => r.charCodeAt(0));
    return Q(t);
  }
  var z = new Uint32Array(256);
  for (let e = 256; e--; ) {
    let t = e;
    for (let r = 8; r--; ) t = t & 1 ? 3988292384 ^ (t >>> 1) : t >>> 1;
    z[e] = t;
  }
  function Q(e) {
    let t = -1;
    for (let r of e) t = (t >>> 8) ^ z[(t & 255) ^ r];
    return (t ^ -1) >>> 0;
  }
  async function Y(e) {
    (!e && ((e = await m()), !e)) ||
      chrome.scripting.executeScript({
        target: { tabId: e, allFrames: !0 },
        files: ["lib/selector.js", "locate.js"],
        world: "ISOLATED",
        injectImmediately: !0,
      });
  }
  var se = {
    "echo::sender": (e, t) => t,
    "log::getLogs": W,
    "settings::get": v,
    "settings::update": ([e]) => O(e),
    "api::fetchStatus": A,
    "api::getCachedStatus": V,
    "api::recognition": ([e]) => G(e),
    "tab::getCurrentId": m,
    "tab::getCurrentJSON": N,
    "tab::getCurrentURL": J,
    "tab::getURL": q,
    "tab::registerDetectedCaptcha": U,
    "tab::getDetectedCaptchas": j,
    "fetch::universalFetch": K,
    "fetch::asData": X,
    "tab::broadcast": ([e]) => F(e),
    "locator::inject": (e, t) => Y(t?.tab?.id),
  };
  a.runtime.onMessage.addListener((e, t, r) => {
    let o = e[1],
      n = se[o];
    return (
      Promise.resolve(n(e.slice(2), t))
        .then((s) => {
          r([C(e[0]), s]);
        })
        .catch((s) => {
          console.error(
            `[@nope/background/rpc] [${o}] errored!`,
            e.slice(2),
            s
          ),
            r([C(e[0]), "" + s]);
        }),
      !0
    );
  });
})();
