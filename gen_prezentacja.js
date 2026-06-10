// Generator prezentacji: Optymalizacja portfela CVaR + łańcuchy Markowa
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const {
  FaBullseye, FaWallet, FaPercentage, FaArrowCircleDown, FaBan,
  FaProjectDiagram, FaDice, FaChartLine, FaChartPie, FaBalanceScale,
  FaCheckCircle, FaCalculator, FaCompressArrowsAlt,
} = require("react-icons/fa");

// ---- paleta ----
const NAVY = "1E2761";
const NAVY2 = "2E3A78";
const ICE = "CADCFC";
const ICE_LIGHT = "EAF1FE";
const WHITE = "FFFFFF";
const RED = "C0392B";
const GREEN = "2C7A4B";
const GRAY = "6B7280";
const DARKTXT = "23272F";

const HDR = "Georgia";
const BODY = "Calibri";

// wymiary obrazków w px (do zachowania proporcji)
const IMG = {
  "prez_img/diagram_markowa.png": [1360, 748],
  "prez_img/f_cel.png": [1072, 320],
  "prez_img/f_cena.png": [2015, 103],
  "prez_img/f_cvar.png": [1745, 112],
  "prez_img/f_ogr1.png": [1262, 121],
  "prez_img/f_ogr2.png": [463, 110],
  "prez_img/f_ogr3.png": [955, 251],
  "prez_img/f_ogr4.png": [248, 99],
  "prez_img/f_strata.png": [916, 101],
  "prez_img/histogram_strat.png": [1428, 781],
  "prez_img/trajektorie.png": [1428, 781],
  "granica_efektywna.png": [1350, 900],
  "portfel_kolowy.png": [1350, 900],
};

function imgByH(slide, path, opts) {
  const [pw, ph] = IMG[path];
  const w = opts.h * (pw / ph);
  const x = opts.cx !== undefined ? opts.cx - w / 2 : opts.x;
  slide.addImage({ path, x, y: opts.y, w, h: opts.h });
  return w;
}
function imgByW(slide, path, opts) {
  const [pw, ph] = IMG[path];
  const h = opts.w * (ph / pw);
  slide.addImage({ path, x: opts.x, y: opts.y, w: opts.w, h });
  return h;
}

async function iconPng(Icon, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Icon, { color, size: String(size) })
  );
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

function iconCircle(slide, pres, data, x, y, d, circColor) {
  slide.addShape(pres.shapes.OVAL, {
    x, y, w: d, h: d, fill: { color: circColor }, line: { type: "none" },
  });
  const pad = d * 0.26;
  slide.addImage({ data, x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad });
}

function slideTitle(slide, text) {
  slide.addText(text, {
    x: 0.5, y: 0.22, w: 9.0, h: 0.62, fontFace: HDR, fontSize: 28,
    bold: true, color: NAVY, margin: 0,
  });
}

// trzy kółka-stany jako motyw dekoracyjny
function chainMotif(slide, pres, x, y, d) {
  const cols = [GREEN, GRAY, RED];
  const gap = d * 1.7;
  for (let i = 0; i < 3; i++) {
    if (i < 2) {
      slide.addShape(pres.shapes.LINE, {
        x: x + d + i * gap, y: y + d / 2, w: gap - d, h: 0,
        line: { color: ICE, width: 1.5 },
      });
    }
    slide.addShape(pres.shapes.OVAL, {
      x: x + i * gap, y, w: d, h: d, fill: { color: cols[i] },
      line: { type: "none" },
    });
  }
}

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "Optymalizacja portfela akcji miarą ryzyka CVaR";

  const ic = {};
  const defs = {
    bullseye: [FaBullseye, "#FFFFFF"], wallet: [FaWallet, "#FFFFFF"],
    percent: [FaPercentage, "#FFFFFF"], down: [FaArrowCircleDown, "#FFFFFF"],
    ban: [FaBan, "#FFFFFF"], graph: [FaProjectDiagram, "#FFFFFF"],
    dice: [FaDice, "#FFFFFF"], chart: [FaChartLine, "#FFFFFF"],
    pie: [FaChartPie, "#FFFFFF"], scale: [FaBalanceScale, "#FFFFFF"],
    check: [FaCheckCircle, "#7BE3A2"], calc: [FaCalculator, "#FFFFFF"],
    compress: [FaCompressArrowsAlt, "#FFFFFF"],
  };
  for (const [k, [Icon, col]] of Object.entries(defs)) ic[k] = await iconPng(Icon, col);

  // ======================= SLAJD 1: tytuł =======================
  {
    const s = pres.addSlide();
    s.background = { color: NAVY };
    s.addText("Optymalizacja portfela akcji\nmiarą ryzyka CVaR", {
      x: 0.7, y: 1.15, w: 8.6, h: 1.7, fontFace: HDR, fontSize: 40,
      bold: true, color: WHITE, margin: 0,
    });
    s.addText("Scenariusze rynkowe generowane łańcuchami Markowa", {
      x: 0.7, y: 2.95, w: 8.6, h: 0.5, fontFace: BODY, fontSize: 20,
      color: ICE, margin: 0,
    });
    chainMotif(s, pres, 0.72, 3.85, 0.28);
    s.addText("Projekt 12 — Algorytmiczne zastosowania łańcuchów Markowa", {
      x: 0.7, y: 4.62, w: 8.6, h: 0.35, fontFace: BODY, fontSize: 14,
      color: ICE, margin: 0,
    });
    s.addText("czerwiec 2026", {
      x: 0.7, y: 4.97, w: 8.6, h: 0.35, fontFace: BODY, fontSize: 14,
      color: "8FA8D8", margin: 0,
    });
  }

  // ======================= SLAJD 2: cel projektu =======================
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    slideTitle(s, "Cel projektu");

    s.addText([
      { text: "Mamy ", options: {} },
      { text: "10 000 PLN", options: { bold: true, color: NAVY } },
      { text: " i możemy kupić akcje ", options: {} },
      { text: "5 spółek", options: { bold: true, color: NAVY } },
      { text: ". Jak podzielić kapitał, aby:", options: {} },
    ], {
      x: 0.5, y: 1.05, w: 4.2, h: 1.0, fontFace: BODY, fontSize: 16,
      color: DARKTXT, margin: 0,
    });
    s.addText([
      { text: "oczekiwany zysk po T krokach wynosił zadane rₑ,", options: { bullet: true, breakLine: true } },
      { text: "ryzyko dużej straty było jak najmniejsze?", options: { bullet: true } },
    ], {
      x: 0.7, y: 2.0, w: 4.0, h: 1.0, fontFace: BODY, fontSize: 15,
      color: DARKTXT, paraSpaceAfter: 8,
    });
    s.addText([
      { text: "„Ryzyko” mierzymy nowoczesną miarą ", options: {} },
      { text: "CVaR", options: { bold: true, color: RED } },
      { text: " — która wkrótce zastąpi VaR w bankowych systemach pomiaru ryzyka.", options: {} },
    ], {
      x: 0.5, y: 3.3, w: 4.2, h: 1.1, fontFace: BODY, fontSize: 14.5,
      color: GRAY, italic: true, margin: 0,
    });

    const card = (y, label, head, desc, icon, col) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 5.05, y, w: 4.45, h: 1.85, fill: { color: ICE_LIGHT }, line: { type: "none" },
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x: 5.05, y, w: 0.07, h: 1.85, fill: { color: col }, line: { type: "none" },
      });
      iconCircle(s, pres, icon, 5.32, y + 0.62, 0.62, col);
      s.addText(label, {
        x: 6.15, y: y + 0.18, w: 3.2, h: 0.3, fontFace: BODY, fontSize: 11,
        bold: true, color: col, charSpacing: 2, margin: 0,
      });
      s.addText(head, {
        x: 6.15, y: y + 0.46, w: 3.25, h: 0.42, fontFace: BODY, fontSize: 16,
        bold: true, color: DARKTXT, margin: 0,
      });
      s.addText(desc, {
        x: 6.15, y: y + 0.9, w: 3.25, h: 0.85, fontFace: BODY, fontSize: 12.5,
        color: GRAY, margin: 0,
      });
    };
    card(1.05, "CZĘŚĆ 1 — SYMULACJA", "Generator scenariuszy",
      "Łańcuch Markowa modeluje stany rynku; Monte Carlo daje 1000 scenariuszy przyszłych cen.",
      ic.dice, GREEN);
    card(3.15, "CZĘŚĆ 2 — OPTYMALIZACJA", "Minimalny CVaR",
      "Wybór portfela to program liniowy — rozwiązany biblioteką cvxpy dla wielu wartości rₑ.",
      ic.calc, NAVY);
  }

  // ======================= SLAJD 3: słowniczek =======================
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    slideTitle(s, "Cztery pojęcia, które wystarczą");

    const card = (x, y, head, descRuns, icon, col) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x, y, w: 4.4, h: 1.95, fill: { color: ICE_LIGHT }, line: { type: "none" },
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x, y, w: 0.07, h: 1.95, fill: { color: col }, line: { type: "none" },
      });
      iconCircle(s, pres, icon, x + 0.25, y + 0.25, 0.55, col);
      s.addText(head, {
        x: x + 0.98, y: y + 0.3, w: 3.3, h: 0.42, fontFace: BODY, fontSize: 16.5,
        bold: true, color: DARKTXT, margin: 0,
      });
      s.addText(descRuns, {
        x: x + 0.3, y: y + 0.92, w: 3.95, h: 0.95, fontFace: BODY, fontSize: 12.5,
        color: DARKTXT, margin: 0,
      });
    };

    card(0.5, 1.0, "Portfel  x", [
      { text: "Wektor x mówi, ile sztuk każdej akcji kupujemy. Wartość portfela: ", options: {} },
      { text: "Vₜ(x) = Σ xᵢ·Sᵢₜ", options: { bold: true, color: NAVY } },
      { text: " (cena × ilość).", options: {} },
    ], ic.wallet, NAVY);
    card(5.1, 1.0, "Stopa zwrotu  R", [
      { text: "Procentowy zysk lub strata na koniec (chwila T): ", options: {} },
      { text: "R = (Vₜ − V₀) / V₀", options: { bold: true, color: NAVY } },
      { text: ".  Żądamy, by jej wartość oczekiwana wynosiła rₑ.", options: {} },
    ], ic.percent, GREEN);
    card(0.5, 3.2, "Strata  L", [
      { text: "Zysk ze znakiem minus: ", options: {} },
      { text: "L(x) = −(Vₜ − V₀)", options: { bold: true, color: NAVY } },
      { text: ".  Dodatnia strata = portfel stracił na wartości.", options: {} },
    ], ic.down, RED);
    card(5.1, 3.2, "Zakaz krótkiej sprzedaży", [
      { text: "Nie wolno sprzedawać akcji, których nie mamy — wszystkie ilości nieujemne: ", options: {} },
      { text: "x ≥ 0", options: { bold: true, color: NAVY } },
      { text: ".", options: {} },
    ], ic.ban, GRAY);
  }

  // ======================= SLAJD 4: łańcuch Markowa =======================
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    slideTitle(s, "Model rynku: łańcuch Markowa");

    s.addText([
      { text: "Każda akcja w każdej chwili jest w jednym z 3 stanów rynku.", options: { bullet: true, breakLine: true } },
      { text: "Stan zmienia się co krok zgodnie z macierzą przejścia P.", options: { bullet: true, breakLine: true } },
      { text: "Reżimy są trwałe: na diagonali 0.80–0.90.", options: { bullet: true, breakLine: true } },
      { text: "Stan steruje rozkładem stopy zwrotu w danym kroku:", options: { bullet: true } },
    ], {
      x: 0.5, y: 1.0, w: 4.2, h: 1.9, fontFace: BODY, fontSize: 14,
      color: DARKTXT, paraSpaceAfter: 7,
    });

    s.addTable([
      [
        { text: "stan", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
        { text: "śr. zwrot / krok", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
        { text: "zmienność", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
      ],
      [{ text: "hossa", options: { bold: true, color: GREEN } }, "+2.0%", "2.5%"],
      [{ text: "stagnacja", options: { bold: true, color: GRAY } }, "−0.2%", "1.5%"],
      [{ text: "bessa", options: { bold: true, color: RED } }, "−2.2%", "3.5%"],
    ], {
      x: 0.5, y: 3.15, w: 4.2, fontFace: BODY, fontSize: 12, color: DARKTXT,
      border: { pt: 0.5, color: "B9C6E8" }, align: "center", valign: "middle",
      rowH: 0.32,
    });

    imgByH(s, "prez_img/diagram_markowa.png", { x: 4.95, y: 1.05, h: 2.62 });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 4.95, y: 3.95, w: 4.6, h: 1.18, fill: { color: ICE_LIGHT }, line: { type: "none" },
    });
    s.addText("Dynamika ceny (zwrot losowany według stanu):", {
      x: 5.15, y: 4.07, w: 4.1, h: 0.3, fontFace: BODY, fontSize: 12,
      color: GRAY, margin: 0,
    });
    imgByH(s, "prez_img/f_cena.png", { cx: 7.25, y: 4.48, h: 0.22 });
  }

  // ======================= SLAJD 5: Monte Carlo =======================
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    slideTitle(s, "Monte Carlo: 1000 scenariuszy rynku");

    imgByH(s, "prez_img/trajektorie.png", { x: 0.5, y: 1.1, h: 3.25 });
    s.addText("Wynik symulacji: ceny sⱼ w chwili T dla scenariuszy j = 1…1000, każdy z prawdopodobieństwem pⱼ = 1/1000.", {
      x: 0.5, y: 4.55, w: 5.95, h: 0.75, fontFace: BODY, fontSize: 13,
      color: GRAY, italic: true, margin: 0,
    });

    const stat = (y, big, small) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 6.8, y, w: 2.7, h: 1.06, fill: { color: ICE_LIGHT }, line: { type: "none" },
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x: 6.8, y, w: 0.07, h: 1.06, fill: { color: NAVY }, line: { type: "none" },
      });
      s.addText(big, {
        x: 7.0, y: y + 0.1, w: 2.4, h: 0.52, fontFace: HDR, fontSize: 26,
        bold: true, color: NAVY, margin: 0,
      });
      s.addText(small, {
        x: 7.0, y: y + 0.62, w: 2.4, h: 0.36, fontFace: BODY, fontSize: 11.5,
        color: GRAY, margin: 0,
      });
    };
    stat(1.1, "m = 1000", "niezależnych scenariuszy");
    stat(2.32, "T = 30", "kroków czasowych");
    stat(3.54, "−7% … +21%", "oczekiwane zwroty akcji");

    s.addText("Akcja startująca w bessie traci średnio, startująca w hossie zyskuje — stan początkowy ma znaczenie przez dziesiątki kroków.", {
      x: 6.8, y: 4.72, w: 2.7, h: 0.85, fontFace: BODY, fontSize: 10.5,
      color: GRAY, margin: 0,
    });
  }

  // ======================= SLAJD 6: VaR i CVaR =======================
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    slideTitle(s, "Jak mierzymy ryzyko? VaR i CVaR");

    imgByH(s, "prez_img/histogram_strat.png", { x: 0.5, y: 1.05, h: 3.2 });

    const expl = (y, head, txt, col) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 6.55, y, w: 2.95, h: 1.45, fill: { color: ICE_LIGHT }, line: { type: "none" },
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x: 6.55, y, w: 0.07, h: 1.45, fill: { color: col }, line: { type: "none" },
      });
      s.addText(head, {
        x: 6.78, y: y + 0.12, w: 2.6, h: 0.36, fontFace: BODY, fontSize: 15,
        bold: true, color: col, margin: 0,
      });
      s.addText(txt, {
        x: 6.78, y: y + 0.5, w: 2.62, h: 0.9, fontFace: BODY, fontSize: 11.5,
        color: DARKTXT, margin: 0,
      });
    };
    expl(1.05, "VaR₀.₉₅", "Poziom straty przekraczany tylko w 5% najgorszych scenariuszy.", NAVY);
    expl(2.65, "CVaR₀.₉₅", "Średnia strata w tych najgorszych 5% — patrzy w głąb ogona rozkładu.", RED);

    s.addText("CVaR „widzi” katastrofalne scenariusze, które VaR ignoruje.", {
      x: 6.55, y: 4.22, w: 2.95, h: 0.65, fontFace: BODY, fontSize: 11,
      color: GRAY, italic: true, margin: 0,
    });
    imgByH(s, "prez_img/f_cvar.png", { cx: 3.6, y: 4.75, h: 0.3 });
  }

  // ======================= SLAJD 7: program liniowy =======================
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    slideTitle(s, "Wybór portfela = program liniowy");

    const panel = (x, y, w, h, head, col) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x, y, w, h, fill: { color: ICE_LIGHT }, line: { type: "none" },
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x, y, w: 0.07, h, fill: { color: col }, line: { type: "none" },
      });
      s.addText(head, {
        x: x + 0.22, y: y + 0.1, w: w - 0.4, h: 0.32, fontFace: BODY,
        fontSize: 13, bold: true, color: col, margin: 0,
      });
    };

    panel(0.5, 1.0, 4.45, 1.78, "FUNKCJA CELU  (formuła Rockafellara–Uryaseva)", NAVY);
    imgByH(s, "prez_img/f_cel.png", { cx: 2.72, y: 1.5, h: 1.05 });

    panel(5.05, 1.0, 4.45, 1.78, "TRIK: LINEARYZACJA CZĘŚCI DODATNIEJ (·)⁺", RED);
    s.addText("Nieliniowy składnik (Lⱼ − β)⁺ zastępują zmienne pomocnicze zⱼ i dwa ograniczenia liniowe:", {
      x: 5.27, y: 1.46, w: 4.05, h: 0.6, fontFace: BODY, fontSize: 12,
      color: DARKTXT, margin: 0,
    });
    imgByH(s, "prez_img/f_ogr1.png", { cx: 7.27, y: 2.22, h: 0.32 });

    panel(0.5, 3.0, 2.93, 1.62, "BUDŻET", NAVY);
    imgByH(s, "prez_img/f_ogr2.png", { cx: 1.96, y: 3.78, h: 0.32 });

    panel(3.55, 3.0, 2.93, 1.62, "OCZEKIWANY ZWROT = rₑ", NAVY);
    imgByH(s, "prez_img/f_ogr3.png", { cx: 5.01, y: 3.68, h: 0.62 });

    panel(6.57, 3.0, 2.93, 1.62, "BEZ KRÓTKIEJ SPRZEDAŻY", NAVY);
    imgByH(s, "prez_img/f_ogr4.png", { cx: 8.03, y: 3.78, h: 0.3 });

    s.addText([
      { text: "W optimum β* = VaR, a wartość funkcji celu = CVaR.  ", options: { color: DARKTXT } },
      { text: "1006 zmiennych — cvxpy rozwiązuje w ułamku sekundy.", options: { color: GRAY, italic: true } },
    ], {
      x: 0.5, y: 4.85, w: 9.0, h: 0.4, fontFace: BODY, fontSize: 13,
      align: "center", margin: 0,
    });
  }

  // ======================= SLAJD 8: granica efektywna =======================
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    slideTitle(s, "Wyniki: granica efektywna");

    imgByH(s, "granica_efektywna.png", { x: 0.45, y: 1.0, h: 4.35 });

    s.addText([
      { text: "Każdy punkt = optymalny portfel dla innego wymaganego zwrotu rₑ (siatka 2–15%).", options: { bullet: true, breakLine: true } },
      { text: "Minimalne ryzyko: CVaR = 2021 PLN przy rₑ = 11.75%.", options: { bullet: true, breakLine: true } },
      { text: "Szara gałąź — portfele zdominowane: to samo ryzyko, mniejszy zwrot.", options: { bullet: true, breakLine: true } },
      { text: "Żądanie zwrotu poniżej 11.75% nie zmniejsza ryzyka — dywersyfikacja przestaje pomagać.", options: { bullet: true } },
    ], {
      x: 7.05, y: 1.2, w: 2.5, h: 4.0, fontFace: BODY, fontSize: 12.5,
      color: DARKTXT, paraSpaceAfter: 12,
    });
  }

  // ======================= SLAJD 9: optymalny portfel =======================
  {
    const s = pres.addSlide();
    s.background = { color: WHITE };
    slideTitle(s, "Wyniki: optymalny portfel dla rₑ = 12.8%");

    imgByH(s, "portfel_kolowy.png", { x: 0.3, y: 1.1, h: 4.0 });

    const stat = (y, big, small, col) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 6.6, y, w: 2.9, h: 1.12, fill: { color: ICE_LIGHT }, line: { type: "none" },
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x: 6.6, y, w: 0.07, h: 1.12, fill: { color: col }, line: { type: "none" },
      });
      s.addText(big, {
        x: 6.82, y: y + 0.1, w: 2.6, h: 0.55, fontFace: HDR, fontSize: 25,
        bold: true, color: col, margin: 0,
      });
      s.addText(small, {
        x: 6.82, y: y + 0.66, w: 2.6, h: 0.36, fontFace: BODY, fontSize: 11.5,
        color: GRAY, margin: 0,
      });
    };
    stat(1.05, "1486 PLN", "VaR₀.₉₅ = β*  (próg strat)", NAVY);
    stat(2.35, "2033 PLN", "CVaR₀.₉₅  (średnia w ogonie)", RED);

    s.addText([
      { text: "Najwięcej kapitału w spółkach startujących w hossie (59%).", options: { bullet: true, breakLine: true } },
      { text: "Ale 7.5% w spółce z bessy — jej niska zależność od reszty ścina ogon strat.", options: { bullet: true } },
    ], {
      x: 6.6, y: 3.7, w: 2.9, h: 1.6, fontFace: BODY, fontSize: 12,
      color: DARKTXT, paraSpaceAfter: 10,
    });
  }

  // ======================= SLAJD 10: podsumowanie =======================
  {
    const s = pres.addSlide();
    s.background = { color: NAVY };
    s.addText("Co pokazaliśmy", {
      x: 0.7, y: 0.4, w: 8.6, h: 0.7, fontFace: HDR, fontSize: 32,
      bold: true, color: WHITE, margin: 0,
    });

    const row = (y, head, txt) => {
      s.addImage({ data: ic.check, x: 0.75, y: y + 0.05, w: 0.4, h: 0.4 });
      s.addText(head, {
        x: 1.35, y, w: 8.0, h: 0.38, fontFace: BODY, fontSize: 16.5,
        bold: true, color: WHITE, margin: 0,
      });
      s.addText(txt, {
        x: 1.35, y: y + 0.38, w: 8.0, h: 0.42, fontFace: BODY, fontSize: 12.5,
        color: ICE, margin: 0,
      });
    };
    row(1.35, "Łańcuch Markowa jako model rynku",
      "Trwałe reżimy (hossa / stagnacja / bessa) sterują rozkładem zwrotów — 1000 scenariuszy Monte Carlo.");
    row(2.32, "CVaR zamiast wariancji",
      "Miara ryzyka, która uśrednia najgorsze 5% scenariuszy zamiast karać również zyski.");
    row(3.29, "Optymalizacja jako program liniowy",
      "Formuła Rockafellara–Uryaseva + linearyzacja (·)⁺ — przy okazji za darmo dostajemy VaR = β*.");
    row(4.26, "Pełna granica efektywna",
      "Minimalny CVaR 2021 PLN przy zwrocie 11.75%; powyżej — klasyczny kompromis zysk/ryzyko.");

    chainMotif(s, pres, 0.75, 5.12, 0.2);
    s.addText("Python  ·  numpy  ·  cvxpy  ·  matplotlib", {
      x: 5.0, y: 5.05, w: 4.3, h: 0.35, fontFace: BODY, fontSize: 12,
      color: "8FA8D8", align: "right", margin: 0,
    });
  }

  await pres.writeFile({ fileName: "Prezentacja - Mean-Variance-Portfolio.pptx" });
  console.log("OK: Prezentacja - Mean-Variance-Portfolio.pptx");
}

main().catch((e) => { console.error(e); process.exit(1); });
