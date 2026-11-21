import re, os, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:80])
    s = s.replace(a, b)

# ---------- 分开存储 / 同步命名空间 ----------
s = s.replace("'gtrip:", "'ctrip:")
rep("salt: te.encode('gtrip-v1')", "salt: te.encode('ctrip-v1')")
rep("o.app = 'gtrip'", "o.app = 'ctrip'")
assert 'gtrip' not in s, [m.start() for m in re.finditer('gtrip', s)]

# ---------- 文案 ----------
rep('  <p class="meta" style="margin-top:18px">国内玩？用 <a href="cn/">国内版（高德地图）</a></p>\n', '')
rep('<h1>✈ 出国旅行手账</h1>', '<h1>🚄 国内旅行手账</h1>')
rep('<p>免注册，把邀请码发给旅伴就能一起实时编辑。</p>', '<p>免注册，把邀请码发给旅伴就能一起实时编辑。地图用高德。</p>')
rep('<div class="recent" id="lnRecent"></div>', '<div class="recent" id="lnRecent"></div>\n  <p class="meta" style="margin-top:18px">出国玩？用 <a href="../">出国版（Google 地图）</a></p>')
s = s.replace('出国旅行手账', '国内旅行手账')
rep('placeholder="行程名，比如：东京 5 日"', 'placeholder="行程名，比如：成都 4 日"')
rep('placeholder="目的地城市，如 Tokyo"', 'placeholder="目的地城市，如 成都"')
rep('placeholder="这天的主题，如 浅草 + 晴空塔"', 'placeholder="这天的主题，如 宽窄巷子 + 春熙路"')
rep("'地点 / 地址 / Maps 链接'", "'地点 / 地址 / 高德链接'")
rep("b.type === '住宿' ? '酒店名 / 地址' : '航班 / 车次'", "b.type === '住宿' ? '酒店名 / 地址' : '车次 / 航班'")

# ---------- 默认清单 ----------
rep("""  ['证件', '护照! 签证/入境材料! 身份证 信用卡(Visa/Master)! 外币现金 旅行保险单 机票/酒店确认单 证件照片备份'],
  ['电子', '转换插头 充电宝 充电器 数据线 eSIM/流量卡! 耳机 自拍杆'],""",
"""  ['证件', '身份证! 学生证/优惠证件 驾照 少量现金 车票/酒店订单截图'],
  ['电子', '充电宝! 充电器 数据线 耳机 自拍杆 相机'],""")
rep("['其他', '纸巾/湿巾 雨伞 水杯 收纳袋 折叠购物袋 笔(填入境卡)']", "['其他', '纸巾/湿巾 雨伞 水杯 收纳袋 折叠购物袋 颈枕(高铁/飞机)']")
rep("/转换插头|充电宝|雨伞|洗发水|沐浴露|药/", "/充电宝|雨伞|洗发水|沐浴露|药/")

# ---------- 高德链接（替换 Google Maps 那一段） ----------
a = s.index('/* ================= Google Maps ================= */')
b = s.index('function previewBtn(')
s = s[:a] + r"""/* ================= 高德地图（URI API，免 Key） ================= */
function isUrl(s) { return /^https?:\/\//i.test(String(s).trim()); }
function q(where) { where = String(where || '').trim(); var p = (T.place || '').trim(); if (p && where.toLowerCase().indexOf(p.toLowerCase()) < 0) where = p + ' ' + where; return where; }
/* 坐标统一存 GCJ-02（高德底图、高德链接用的都是它）。OSM 系定位结果是 WGS-84，进来时先转换 */
function outChina(lat, lng) { return lng < 72.004 || lng > 137.8347 || lat < 0.8293 || lat > 55.8271; }
function wgs2gcj(lat, lng) {
  if (outChina(lat, lng)) return [lat, lng];
  var A = 6378245.0, EE = 0.00669342162296594323, x = lng - 105.0, y = lat - 35.0;
  var dLat = -100 + 2 * x + 3 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x)) + (20 * Math.sin(6 * x * Math.PI) + 20 * Math.sin(2 * x * Math.PI)) * 2 / 3 + (20 * Math.sin(y * Math.PI) + 40 * Math.sin(y / 3 * Math.PI)) * 2 / 3 + (160 * Math.sin(y / 12 * Math.PI) + 320 * Math.sin(y * Math.PI / 30)) * 2 / 3;
  var dLng = 300 + x + 2 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x)) + (20 * Math.sin(6 * x * Math.PI) + 20 * Math.sin(2 * x * Math.PI)) * 2 / 3 + (20 * Math.sin(x * Math.PI) + 40 * Math.sin(x / 3 * Math.PI)) * 2 / 3 + (150 * Math.sin(x / 12 * Math.PI) + 300 * Math.sin(x / 30 * Math.PI)) * 2 / 3;
  var rad = lat / 180 * Math.PI, m = Math.sin(rad); m = 1 - EE * m * m; var sm = Math.sqrt(m);
  dLat = dLat * 180 / ((A * (1 - EE)) / (m * sm) * Math.PI); dLng = dLng * 180 / (A / sm * Math.cos(rad) * Math.PI);
  return [+(lat + dLat).toFixed(6), +(lng + dLng).toFixed(6)];
}
/* 在地图上手动校准过的地点：高德链接一律用校准后的坐标 */
function pinned(rec, raw) { return !!(rec && rec.llm === 'manual' && Array.isArray(rec.ll) && rec.llq === String(raw || '').trim()); }
function locOf(where, rec) { // 路线用：任何已定位的坐标（自动或校准）
  if (rec && Array.isArray(rec.ll) && rec.llq === String(where || '').trim()) return rec.ll;
  return llFromUrl(where);
}
function aName(where, rec) { var n = rec && (rec.what || rec.name) || String(where || ''); return isUrl(n) ? '地点' : String(n).replace(/[,;|]/g, ' ').trim().slice(0, 40); }
function aMarker(ll, name) { return 'https://uri.amap.com/marker?position=' + ll[1] + ',' + ll[0] + '&name=' + encodeURIComponent(name) + '&coordinate=gaode&callnative=1&src=trip-notebook'; }
function gSearch(where, rec) {
  if (pinned(rec, where)) return aMarker(rec.ll, aName(where, rec));
  var c = llFromUrl(where); if (c) return aMarker(c, aName(where, rec));
  if (isUrl(where)) return String(where).trim(); // 高德分享短链接，直接打开原链接
  var u = 'https://uri.amap.com/search?keyword=' + encodeURIComponent(String(where).trim()) + '&callnative=1&src=trip-notebook';
  if (T.place) u += '&city=' + encodeURIComponent(T.place.trim());
  if (Array.isArray(T.placeLL) && T.placeLLq === T.place) u += '&center=' + T.placeLL[1] + ',' + T.placeLL[0] + '&coordinate=gaode';
  return u;
}
var AMODE = { transit: 'bus', walking: 'walk', driving: 'car', bicycling: 'ride' };
function aNav(a, b) {
  return 'https://uri.amap.com/navigation?from=' + a.ll[1] + ',' + a.ll[0] + ',' + encodeURIComponent(a.name) + '&to=' + b.ll[1] + ',' + b.ll[0] + ',' + encodeURIComponent(b.name) +
    '&mode=' + (AMODE[T.mode] || 'bus') + '&policy=0&coordinate=gaode&callnative=1&src=trip-notebook';
}
/* 高德导航链接只支持 起点→终点，所以当天路线拆成一段一段；没定位的点先跳过 */
function routeHtml(its) {
  var pts = [], skip = 0;
  its.forEach(function (it) {
    if (!String(it.where || '').trim()) return;
    var ll = locOf(it.where, it); if (ll) pts.push({ ll: ll, name: aName(it.where, it) }); else skip++;
  });
  if (pts.length < 2) return skip ? '<span class="meta" title="地图上定位好以后，这里会出现高德导航">🧭 定位中…</span>' : '';
  if (pts.length === 2 && !skip) return '<a class="btn sm" href="' + esc(aNav(pts[0], pts[1])) + '" target="_blank" rel="noopener" title="在高德地图导航">🧭 ' + esc(pts[0].name) + ' → ' + esc(pts[1].name) + '</a>';
  var legs = [];
  for (var i = 0; i + 1 < pts.length; i++) legs.push('<a href="' + esc(aNav(pts[i], pts[i + 1])) + '" target="_blank" rel="noopener">' + (i + 1) + '. ' + esc(pts[i].name) + ' → ' + esc(pts[i + 1].name) + '</a>');
  return '<details class="legs"><summary class="btn sm" title="高德导航只能两点之间，按顺序分段打开">🧭 当天路线 · ' + legs.length + ' 段</summary><div>' + legs.join('') + (skip ? '<span class="meta">还有 ' + skip + ' 个地点没定位，暂时跳过</span>' : '') + '</div></details>';
}
function mapA(where, t, rec) {
  if (!where || !String(where).trim()) return '<span class="map" style="opacity:.2">📍</span>';
  var pin = pinned(rec, where);
  return '<a class="map" href="' + esc(gSearch(where, rec)) + '" target="_blank" rel="noopener" title="' + (pin ? '按你在地图上校准的位置打开高德地图' : (t || '在高德地图搜索')) + '">' + (pin ? '📌' : '📍') + '</a>';
}
""" + s[b:]

rep("""    var route = gRoute(its.map(function (it) { return [it.where, it]; }));
""", "")
rep("""      (route ? '<a class="btn sm" href="' + esc(route) + '" target="_blank" rel="noopener" title="按顺序在 Google 地图规划路线">🧭 当天路线</a>' : '') +""",
    """      routeHtml(its) +""")

# ---------- 坐标解析：高德链接是 经度,纬度 ----------
a = s.index('function llFromUrl(s) {'); b = s.index('function geoKey(p)')
s = s[:a] + r"""function llFromUrl(s) {
  s = String(s);
  var m = s.match(/[?&](?:position|location|p|q|dest|to)=(\d{2,3}\.\d+)(?:,|%2C)(\d{1,2}\.\d+)/i); // 高德：经度,纬度
  if (m) return [parseFloat(m[2]), parseFloat(m[1])];
  m = s.match(/^\s*(\d{1,2}\.\d+)\s*[,，]\s*(\d{2,3}\.\d+)\s*$/); // 直接填 纬度,经度
  if (m) return [parseFloat(m[1]), parseFloat(m[2])];
  m = s.match(/^\s*(\d{2,3}\.\d+)\s*[,，]\s*(\d{1,2}\.\d+)\s*$/); // 高德拾取器复制的 经度,纬度
  return m ? [parseFloat(m[2]), parseFloat(m[1])] : null;
}
""" + s[b:]

# ---------- 底图：高德瓦片 ----------
rep("""    M.map = L.map('lmap', { zoomControl: true, worldCopyJump: true }).setView([25, 110], 3);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' }).addTo(M.map);""",
"""    M.map = L.map('lmap', { zoomControl: true }).setView([35, 105], 4);
    L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', { subdomains: '1234', maxZoom: 18, attribution: '&copy; 高德地图' }).addTo(M.map);""")
s = s.replace('/* ================= 行程地图（Leaflet + OpenStreetMap，免 Key） ================= */', '/* ================= 行程地图（Leaflet + 高德底图，免 Key） ================= */')
rep("在 Google 地图打开</a> · <button data-act=\"pick\"", "在高德地图打开</a> · <button data-act=\"pick\"")
rep("📌 已手动校准，Google 地图和路线都按这个位置 · ", "📌 已手动校准，高德链接和路线都按这个位置 · ")
rep("自动定位，拖动图钉或重新点选后，Google 地图也会改用新位置", "自动定位，位置不准就拖动图钉或重新点选")
rep("图钉可拖动校准 · 地点栏可粘贴含坐标的 Google Maps 链接</span>';", "图钉可拖动校准 · 地点栏也可以直接填坐标（高德坐标拾取器复制的 经度,纬度）' + (amapKey() ? ' · 已用高德 Key 定位' : ' · 定位不准？填一个<button data-act=\"amapkey\">高德 Key</button>会准很多') + '</span>';")
rep('📍 打开 Google 地图 · 👁 在下方地图里看', '📍 在高德地图搜索 · 👁 在下方地图里看')

# ---------- 定位：有高德 Key 用高德，否则 OSM（转 GCJ-02） ----------
rep("/* 地名 → 坐标：Nominatim 为主，Photon 兜底；每秒最多 1 次，结果同步给所有旅伴 */",
    "/* 地名 → 坐标（GCJ-02）：填了高德 Web 服务 Key 就用高德 POI 搜索；否则 Nominatim 为主、Photon 兜底。每秒最多 1 次，结果同步给所有旅伴 */\nfunction amapKey() { return (ls('ctrip:amapkey') || '').trim(); }")
a = s.index('async function geocode(query, raw) {'); b = s.index('/* ================= 导出 KML')
s = s[:a] + r"""async function geocode(query, raw) {
  var key = amapKey(), city = (T.place || '').trim(), r0 = String(raw || query).trim();
  if (key) {
    try {
      var u = 'https://restapi.amap.com/v3/place/text?offset=1&page=1&extensions=base&key=' + encodeURIComponent(key) + '&keywords=' + encodeURIComponent(r0) + (city && raw ? '&city=' + encodeURIComponent(city) : '');
      var ja = await (await fetch(u)).json();
      var loc = ja && ja.status === '1' && ja.pois && ja.pois[0] && ja.pois[0].location;
      if (!loc && ja && ja.status === '1') { // POI 没找到，再试地址解析
        var jg = await (await fetch('https://restapi.amap.com/v3/geocode/geo?key=' + encodeURIComponent(key) + '&address=' + encodeURIComponent(r0) + (city && raw ? '&city=' + encodeURIComponent(city) : ''))).json();
        loc = jg && jg.status === '1' && jg.geocodes && jg.geocodes[0] && jg.geocodes[0].location;
      }
      if (loc && typeof loc === 'string') { var xy = loc.split(','); return [+(+xy[1]).toFixed(6), +(+xy[0]).toFixed(6)]; }
      if (ja && ja.status === '1') return null;
      // Key 无效 / 超额：退回免费定位
    } catch (e) { }
  }
  var c0 = Array.isArray(T.placeLL) ? T.placeLL : null;
  var vb = c0 ? '&viewbox=' + (c0[1] - 1) + ',' + (c0[0] + 1) + ',' + (c0[1] + 1) + ',' + (c0[0] - 1) : '';
  var tries = [query]; if (raw && raw.trim() !== query) tries.push(raw.trim());
  for (var i = 0; i < tries.length; i++) {
    try {
      var r = await fetch('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&accept-language=zh-CN&countrycodes=cn,hk,mo,tw&q=' + encodeURIComponent(tries[i]) + vb);
      var j = await r.json(); if (j && j[0]) return wgs2gcj(+j[0].lat, +j[0].lon);
    } catch (e) { }
    try {
      var r2 = await fetch('https://photon.komoot.io/api/?limit=1&q=' + encodeURIComponent(tries[i]) + (c0 ? '&lat=' + c0[0] + '&lon=' + c0[1] : ''));
      var j2 = await r2.json(); var f = j2 && j2.features && j2.features[0];
      if (f) return wgs2gcj(f.geometry.coordinates[1], f.geometry.coordinates[0]);
    } catch (e) { }
    if (i + 1 < tries.length) await sleep(1100);
  }
  return null;
}

""" + s[b:]

# ---------- 地图卡片：KML 按钮换成高德 Key ----------
rep("""<button class="btn sm" data-act="kml" title="导出后导入 Google My Maps，手机 Google 地图里就能看到">导出到 Google My Maps</button>""",
    """<button class="btn sm" data-act="amapkey" title="可选：填高德 Web 服务 Key，地点定位更准">🔑 高德 Key</button>""")
rep("""    kml: function () {""", """    amapkey: function () {
      var cur = amapKey();
      var v = prompt('可选：填入高德开放平台的「Web 服务」Key，地点定位会准很多（不填也能用，只是用免费的 OpenStreetMap 定位）。\\n\\n申请：lbs.amap.com → 控制台 → 应用管理 → 创建应用 → 添加 Key，服务平台选「Web 服务」。\\n\\nKey 只保存在这台设备上，不会同步给旅伴；你定位好的坐标会同步。留空 = 不用 Key。', cur);
      if (v === null) return;
      ls('ctrip:amapkey', v.trim() || null);
      if (v.trim()) { // 用新 Key 重新定位所有「自动定位」的点
        mapPoints().forEach(function (p) { if (p.r.llm !== 'manual' && p.r.llq) set('F|' + p.l + '|' + p.r.id + '|llq', ''); });
        set('m|placeLLq', ''); build(); toast('已保存，正在用高德重新定位');
      } else toast('已清除 Key');
      M.fitKey = ''; rerender();
    },
    kml: function () {""")

# ---------- 分段路线下拉样式 ----------
rep(".lmap{height:420px;background:var(--bg);z-index:0}",
    ".lmap{height:420px;background:var(--bg);z-index:0}\n.legs{position:relative}\n.legs summary{list-style:none;cursor:pointer}\n.legs summary::-webkit-details-marker{display:none}\n.legs>div{position:absolute;right:0;top:calc(100% + 4px);z-index:5;background:var(--sf);border:1px solid var(--ln);border-radius:var(--r);box-shadow:0 6px 20px rgba(0,0,0,.12);padding:6px;min-width:220px;display:flex;flex-direction:column;gap:2px}\n.legs>div a{padding:6px 8px;border-radius:6px;font-size:13px;color:var(--t1);text-decoration:none;white-space:nowrap}\n.legs>div a:hover{background:var(--bg)}\n.legs>div .meta{padding:4px 8px}")

assert 'google' not in re.sub(r'kml[\s\S]*?\n', '', '').lower()

# ================= 高德 JS API Key：联想输入 + 精确定位 + 可分享给本行程 =================
def cut(start, end, new):
    global s
    a = s.index(start); b = s.index(end, a)
    s = s[:a] + new + s[b:]

# 1) Key 存取 + 按需加载 JS API
rep("function amapKey() { return (ls('ctrip:amapkey') || '').trim(); }", r"""/* 高德 Web端(JS API) Key：默认只存本机；勾选分享后存进本行程（随行程一起加密） */
function amapCfg() {
  var loc = null; try { loc = JSON.parse(ls('ctrip:amap') || 'null'); } catch (e) { }
  if (loc && loc.k) return { k: loc.k, c: loc.c || '', from: 'local' };
  var t = T && T.amapKey; if (t && t.k) return { k: t.k, c: t.c || '', from: 'trip' };
  return null;
}
function amapKey() { var c = amapCfg(); return c ? c.k : ''; }
var AM = { p: null, k: '', err: '' };
function amapReady() {
  var c = amapCfg(); if (!c) return Promise.resolve(null);
  if (AM.k && AM.k !== c.k) return Promise.resolve(null); // 已加载过别的 Key，要刷新页面
  if (AM.p) return AM.p;
  AM.k = c.k;
  AM.p = new Promise(function (res) {
    window._AMapSecurityConfig = { securityJsCode: c.c };
    var sc = document.createElement('script');
    sc.src = 'https://webapi.amap.com/maps?v=2.0&key=' + encodeURIComponent(c.k) + '&plugin=AMap.AutoComplete,AMap.PlaceSearch';
    sc.onload = function () { res(window.AMap || null); }; sc.onerror = function () { AM.err = 'JS API 加载失败'; res(null); };
    document.head.appendChild(sc);
  });
  return AM.p;
}
function amapCall(fn) { // 包一层超时
  return amapReady().then(function (A) {
    if (!A) return null;
    return new Promise(function (res) { var done = false; setTimeout(function () { if (!done) { done = true; res(null); } }, 8000); fn(A, function (v) { if (!done) { done = true; res(v); } }); });
  });
}
function amapErr(r, st) { AM.err = typeof r === 'string' ? r : (r && r.info) || st; return null; }
function llOf(loc) { return loc && typeof loc.lng === 'number' ? [+loc.lat.toFixed(6), +loc.lng.toFixed(6)] : null; }
/* 地名 → 精确 POI；false = 高德确认没有结果，null = 出错 */
function amapSearch(kw, city) {
  return amapCall(function (A, done) {
    new A.PlaceSearch({ city: city || '全国', pageSize: 1, pageIndex: 1 }).search(kw, function (st, r) {
      if (st === 'complete' && r.poiList && r.poiList.pois.length) { var p = r.poiList.pois[0]; done({ ll: llOf(p.location), name: p.name }); }
      else if (st === 'no_data') done(false); else done(amapErr(r, st));
    });
  });
}
function amapTips(kw, city) {
  return amapCall(function (A, done) {
    new A.AutoComplete({ city: city || '全国' }).search(kw, function (st, r) {
      if (st === 'complete') done((r.tips || []).filter(function (t) { return t.name; }).slice(0, 8));
      else if (st === 'no_data') done([]); else done(amapErr(r, st));
    });
  });
}""")

# 2) 定位：有 Key 用 JS API 的 PlaceSearch
cut("  if (key) {\n    try {\n      var u = 'https://restapi.amap.com", "  var c0 = Array.isArray(T.placeLL)", r"""  if (key) {
    var hit = await amapSearch(r0, city && raw ? city : '');
    if (hit && hit.ll) return hit.ll;
    if (hit === false) return null;
    // Key 无效 / 超额：退回免费定位
  }
""")

# 3) 联想选中的 POI 和手动校准一样算「精确」：高德链接按坐标 + 名称打开
rep("function pinned(rec, raw) { return !!(rec && rec.llm === 'manual' &&", "function pinned(rec, raw) { return !!(rec && (rec.llm === 'manual' || rec.llm === 'poi') &&")
rep("  if (l === 'wish' && how === 'manual') T.items.forEach(", "  if (l === 'wish' && (how === 'manual' || how === 'poi')) T.items.forEach(")
rep("📌 已手动校准，高德链接和路线都按这个位置 · ", "' + (p.r.llm === 'poi' ? '📌 高德精确位置' : '📌 已手动校准，高德链接和路线都按这个位置') + ' · ")
rep("p.r.llm !== 'manual' && p.r.llq", "p.r.llm !== 'manual' && p.r.llm !== 'poi' && p.r.llq")

# 4) Key 设置弹窗
rep('<div class="modal" id="shareM" hidden>', """<div class="modal" id="amapM" hidden><div class="card">
  <div class="hd"><b>高德地图 Key</b><span class="meta" id="amapState"></span><button class="x" data-close>×</button></div>
  <div class="bd">
    <p class="meta" style="margin-top:0">配上后，「想去」「日程」「住宿」里输地点名会自动联想，选中就记下高德的精确位置，地图定位也更准。不配也能用。</p>
    <ol class="steps">
      <li>登录 <a href="https://console.amap.com/dev/key/app" target="_blank" rel="noopener">高德开放平台</a> → 应用管理 → 我的应用 → 创建新应用</li>
      <li>在应用里点「添加 Key」，服务平台选 <b>Web端(JS API)</b></li>
      <li>域名白名单填 <code id="amapHost"></code> <button class="btn sm" id="amapCopyHost">复制</button></li>
      <li>提交后把 <b>Key</b> 和 <b>安全密钥</b> 粘到下面，点保存</li>
    </ol>
    <div class="row"><input class="kin" id="amapK" placeholder="Key" autocomplete="off" spellcheck="false"><input class="kin" id="amapC" placeholder="安全密钥" autocomplete="off" spellcheck="false"></div>
    <label class="row" style="cursor:pointer"><input type="checkbox" id="amapShare"> <b>分享给本行程</b> <span class="meta">同行程的人都能用，消耗你的额度</span></label>
    <div class="row"><button class="btn p" id="amapSave">保存</button><button class="btn" id="amapClear">清除</button><span class="meta" id="amapMsg"></span></div>
    <p class="meta">🔒 默认只存在这台设备上；勾选分享后加密存进本行程，只有拿到邀请码/链接的人能用。</p>
  </div>
</div></div>
<div id="sugg" hidden></div>
<div class="modal" id="shareM" hidden>""")
rep(".lmap{height:420px;background:var(--bg);z-index:0}", """.lmap{height:420px;background:var(--bg);z-index:0}
.kin{flex:1;min-width:12em;border:1px solid var(--ln);background:var(--bg);border-radius:6px;padding:7px 9px;outline:none;font:13px ui-monospace,Menlo,monospace}
#amapM code{background:var(--bg);padding:1px 6px;border-radius:4px}
#sugg{position:fixed;z-index:20;background:var(--sf);border:1px solid var(--ln);border-radius:var(--r);box-shadow:0 8px 24px rgba(0,0,0,.14);padding:4px;max-height:300px;overflow:auto;min-width:240px}
#sugg .si{padding:7px 10px;border-radius:6px;cursor:pointer;font-size:13px;line-height:1.35}
#sugg .si small{display:block;color:var(--t3);font-size:11px}
#sugg .si.on,#sugg .si:hover{background:var(--al)}
#sugg .sf{padding:3px 10px;font-size:10px;color:var(--t3);text-align:right}""")

cut("    amapkey: function () {", "    kml: function () {", r"""    amapkey: function () { openAmap(); },
""")

rep("function refreshConv() {", r"""function openAmap() {
  var c = amapCfg(), loc = c && c.from === 'local', tk = T.amapKey && T.amapKey.k;
  $('#amapHost').textContent = location.hostname || 'deiuhen.github.io';
  $('#amapK').value = c ? c.k : ''; $('#amapC').value = c ? c.c : '';
  $('#amapShare').checked = !!(tk && c && tk === c.k);
  $('#amapState').textContent = !c ? '' : loc ? (tk === c.k ? '已分享给本行程' : '只在这台设备上') : '正在用旅伴分享的 Key';
  $('#amapMsg').textContent = AM.k && c && AM.k !== c.k ? '换了 Key，刷新页面后生效' : '';
  $('#amapM').hidden = false;
}
function amapRelocate() { // 用 Key 重新定位所有「自动定位」的点
  mapPoints().forEach(function (p) { if (p.r.llm !== 'manual' && p.r.llm !== 'poi' && p.r.llq) set('F|' + p.l + '|' + p.r.id + '|llq', ''); });
  set('m|placeLLq', ''); build(); M.fitKey = ''; rerender();
}
$('#amapCopyHost').onclick = function () { copy($('#amapHost').textContent); };
$('#amapSave').onclick = async function () {
  var k = $('#amapK').value.trim(), c = $('#amapC').value.trim(), sh = $('#amapShare').checked, msg = $('#amapMsg');
  if (!/^[0-9a-f]{32}$/i.test(k)) { msg.textContent = 'Key 应该是 32 位字母数字'; return; }
  if (!c) { msg.textContent = '还要填安全密钥（和 Key 在同一行）'; return; }
  ls('ctrip:amap', JSON.stringify({ k: k, c: c }));
  if (sh) setM('amapKey', { k: k, c: c }); else if (T.amapKey && T.amapKey.k === k) setM('amapKey', null);
  if (AM.k && AM.k !== k) { msg.innerHTML = '已保存，<a href="#" onclick="location.reload();return false">刷新页面</a>后生效'; return; }
  msg.textContent = '检测中…'; AM.err = '';
  var t = await amapTips('天安门', '北京');
  if (t && t.length) {
    msg.textContent = '✅ Key 可用' + (sh ? '，已分享给本行程' : '');
    $('#amapState').textContent = sh ? '已分享给本行程' : '只在这台设备上';
    amapRelocate();
  } else {
    var e = String(AM.err || ''), why = /DOMAIN/i.test(e) ? '域名白名单里要有 ' + (location.hostname || '') : /SCODE|SECURITY/i.test(e) ? '安全密钥不对' : /PLAT_NOMATCH/i.test(e) ? '服务平台要选「Web端(JS API)」，不是 Web 服务' : /INVALID_USER_KEY/i.test(e) ? 'Key 不对' : /OVER|LIMIT/i.test(e) ? '今天的额度用完了' : e || '连不上高德';
    msg.textContent = '❌ ' + why + (e && why !== e ? '（' + e + '）' : '');
  }
};
$('#amapClear').onclick = function () {
  var c = amapCfg(); ls('ctrip:amap', null);
  if (c && T.amapKey && T.amapKey.k === c.k && confirm('这个 Key 也分享在本行程里，要一起取消分享吗？')) setM('amapKey', null);
  $('#amapK').value = ''; $('#amapC').value = ''; $('#amapShare').checked = false;
  $('#amapMsg').textContent = '已清除' + (AM.k ? '，刷新页面后完全停用' : ''); $('#amapState').textContent = amapCfg() ? '正在用旅伴分享的 Key' : '';
  rerender();
};

/* 输入地点名 → 高德联想；选中就记下精确位置 */
var SG = { el: null, tips: [], i: -1, t: 0, seq: 0 };
function suggOk(el) {
  if (!el || el.tagName !== 'INPUT' || !el.dataset.l) return false;
  var l = el.dataset.l, f = el.dataset.f;
  return (l === 'wish' && (f === 'name' || f === 'where')) || (l === 'items' && f === 'where') || (l === 'book' && f === 'detail' && (find('book', el.dataset.id) || {}).type === '住宿');
}
function hideSugg() { SG.el = null; SG.tips = []; SG.i = -1; $('#sugg').hidden = true; }
function placeSugg() {
  var el = SG.el, box = $('#sugg'); if (!el || !document.body.contains(el)) { hideSugg(); return; }
  var r = el.getBoundingClientRect(); box.style.left = Math.max(8, Math.min(r.left, innerWidth - box.offsetWidth - 8)) + 'px';
  box.style.top = (r.bottom + box.offsetHeight + 8 > innerHeight && r.top > box.offsetHeight ? r.top - box.offsetHeight - 4 : r.bottom + 4) + 'px';
  box.style.minWidth = Math.max(240, r.width) + 'px';
}
function showSugg(el, tips) {
  if (!tips || !tips.length) { hideSugg(); return; }
  SG.el = el; SG.tips = tips; SG.i = -1;
  $('#sugg').innerHTML = tips.map(function (t, i) { var sub = [Array.isArray(t.district) ? '' : t.district, Array.isArray(t.address) ? '' : t.address].filter(Boolean).join(' '); return '<div class="si" data-i="' + i + '">' + esc(t.name) + (llOf(t.location) ? '' : ' <span class="meta">（无坐标）</span>') + (sub ? '<small>' + esc(sub) + '</small>' : '') + '</div>'; }).join('') + '<div class="sf">高德地图 · ↑↓ 选择 · 回车确定</div>';
  $('#sugg').hidden = false; placeSugg();
}
function pickSugg(i) {
  var t = SG.tips[i], el = SG.el; hideSugg(); if (!t || !el) return;
  var l = el.dataset.l, id = el.dataset.id, f = el.dataset.f, r = find(l, id), ll = llOf(t.location); if (!r) return;
  var key = t.name;
  if (l === 'wish') {
    var old = { name: r.name, key: String(r.where || r.name || '').trim() };
    if (f === 'name') { setF('wish', id, 'name', t.name); key = String(r.where || '').trim() ? null : t.name; }
    else { setF('wish', id, 'where', t.name); if (!String(r.name || '').trim()) setF('wish', id, 'name', t.name); }
    syncWish(find('wish', id), old);
  } else setF(l, id, f, t.name);
  if (ll && key) { setGeo(l, id, ll, 'poi', key); toast('📌 已记下高德精确位置'); } else rerender();
}
document.addEventListener('input', function (e) {
  var el = e.target; if (!T || !suggOk(el)) return;
  clearTimeout(SG.t);
  var v = el.value.trim(); if (!amapKey() || v.length < 2 || isUrl(v) || llFromUrl(v)) { hideSugg(); return; }
  SG.t = setTimeout(function () {
    var my = ++SG.seq, sig = sigOf(el);
    amapTips(v, (T.place || '').trim()).then(function (tips) {
      var a = document.activeElement; if (my !== SG.seq || !a || sigOf(a) !== sig) return;
      showSugg(a, tips);
    });
  }, 250);
});
document.addEventListener('keydown', function (e) {
  if ($('#sugg').hidden || e.target !== SG.el) return;
  var n = SG.tips.length;
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); SG.i = e.key === 'ArrowDown' ? (SG.i + 1) % n : (SG.i <= 0 ? n - 1 : SG.i - 1); $('#sugg').querySelectorAll('.si').forEach(function (x, i) { x.classList.toggle('on', i === SG.i); }); }
  else if (e.key === 'Enter' && SG.i >= 0) { e.preventDefault(); pickSugg(SG.i); }
  else if (e.key === 'Escape') hideSugg();
}, true);
$('#sugg').addEventListener('mousedown', function (e) { e.preventDefault(); var x = e.target.closest('.si'); if (x) pickSugg(+x.dataset.i); });
document.addEventListener('focusout', function (e) { if (e.target === SG.el) setTimeout(function () { if (document.activeElement !== SG.el) hideSugg(); }, 120); });
addEventListener('scroll', function () { if (SG.el) placeSugg(); }, true);
addEventListener('resize', function () { if (SG.el) placeSugg(); });
function refreshConv() {""")

os.makedirs(os.path.dirname(dst), exist_ok=True)
open(dst, 'w', encoding='utf-8').write(s)
left = [l for l in s.split('\n') if 'Google' in l or 'google.com' in l]
print('lines still mentioning Google:', len(left))
for l in left: print('  ', l.strip()[:120])
