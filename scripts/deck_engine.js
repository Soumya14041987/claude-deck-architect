#!/usr/bin/env node
/**
 * deck_engine.js — renders a Deck Architect content plan (JSON) into a .pptx
 * using pptxgenjs. Invoked by build_deck.py; not meant to be run standalone
 * except for local debugging.
 *
 * Usage: node deck_engine.js <plan.json> <output.pptx> <themes.json>
 */

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const [, , planPath, outPath, themesPath] = process.argv;

if (!planPath || !outPath || !themesPath) {
  console.error("Usage: node deck_engine.js <plan.json> <output.pptx> <themes.json>");
  process.exit(1);
}

// Validate file existence
const requiredFiles = [planPath, themesPath];
for (const file of requiredFiles) {
  if (!fs.existsSync(file)) {
    console.error(`[ERROR] Required file not found: ${file}`);
    process.exit(1);
  }
}

let plan, themes;
try {
  plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
} catch (e) {
  console.error(`[ERROR] Failed to parse plan JSON: ${e.message}`);
  process.exit(1);
}

try {
  themes = JSON.parse(fs.readFileSync(themesPath, "utf8"));
} catch (e) {
  console.error(`[ERROR] Failed to parse themes JSON: ${e.message}`);
  process.exit(1);
}

const themeKey = plan.theme || "cyber-neon";
const mode = plan.mode === "light" ? "light" : "dark";
const theme = themes[themeKey] || themes["cyber-neon"];

const BG = mode === "light" ? theme.bg_light : theme.bg_dark;
const ACCENT = theme.accent_primary;
const ACCENT2 = theme.accent_secondary;
const CARD_BG = mode === "light" ? theme.card_light || "F1F5F9" : theme.card_dark;
const TEXT = mode === "light" ? "1A1A1A" : "E6E6E6";
const TITLE_COLOR = mode === "light" ? (theme.ink || "0F172A") : ACCENT;
const FONT = theme.font || "Arial";
const FONT_FALLBACK = "Arial";

// ---- Presentation setup ----
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3" x 7.5"
pres.author = plan.presenter || "Deck Architect";
pres.title = plan.title || "Untitled Deck";

const SLIDE_W = 13.3;
const SLIDE_H = 7.5;
const MARGIN = 0.6;

function baseSlide(bgColor) {
  const s = pres.addSlide();
  s.background = { color: bgColor || BG };
  return s;
}

function addNotesIfAny(slide, item) {
  if (item.notes) slide.addNotes(item.notes);
}

function titleBlock(slide, titleText, opts = {}) {
  slide.addText(titleText, {
    x: MARGIN,
    y: opts.y ?? 0.45,
    w: SLIDE_W - MARGIN * 2,
    h: opts.h ?? 0.9,
    fontFace: FONT,
    fontSize: opts.fontSize ?? 32,
    bold: true,
    color: opts.color ?? TITLE_COLOR,
    align: opts.align ?? "left",
    margin: 0,
  });
}

function footer(slide, pageNum) {
  slide.addText(plan.event || plan.title || "", {
    x: MARGIN,
    y: SLIDE_H - 0.4,
    w: SLIDE_W - MARGIN * 2 - 0.6,
    h: 0.3,
    fontFace: FONT,
    fontSize: 9,
    color: mode === "light" ? "8A8A8A" : "6B7280",
    align: "left",
    margin: 0,
  });
  slide.addText(String(pageNum), {
    x: SLIDE_W - MARGIN - 0.5,
    y: SLIDE_H - 0.4,
    w: 0.5,
    h: 0.3,
    fontFace: FONT,
    fontSize: 9,
    color: mode === "light" ? "8A8A8A" : "6B7280",
    align: "right",
    margin: 0,
  });
}

// ---- Archetype renderers ----

function renderTitle(item, idx) {
  const s = baseSlide();
  // Large soft accent shape, not a stripe — a translucent circle bottom-right
  s.addShape(pres.shapes.OVAL, {
    x: SLIDE_W - 4.2,
    y: SLIDE_H - 4.2,
    w: 6,
    h: 6,
    fill: { color: ACCENT, transparency: 85 },
    line: { type: "none" },
  });
  // NOTE: transparency renders correctly in PowerPoint; LibreOffice's PDF
  // export (used for our own QA preview) sometimes shows translucent fills
  // as flatter/darker than PowerPoint will. Verify the true rendering in
  // PowerPoint or Keynote if the QA preview looks off — do not "fix" by
  // removing transparency, which would look wrong in the real target app.
  s.addText(item.title || plan.title, {
    x: MARGIN,
    y: 2.5,
    w: SLIDE_W - MARGIN * 2 - 1,
    h: 1.6,
    fontFace: FONT,
    fontSize: 44,
    bold: true,
    color: TITLE_COLOR,
    align: "left",
    margin: 0,
  });
  if (item.subtitle || plan.subtitle) {
    s.addText(item.subtitle || plan.subtitle, {
      x: MARGIN,
      y: 4.05,
      w: SLIDE_W - MARGIN * 2 - 1,
      h: 0.7,
      fontFace: FONT,
      fontSize: 20,
      color: ACCENT2,
      align: "left",
      margin: 0,
    });
  }
  const presenterLine = [plan.presenter, plan.event].filter(Boolean).join("  |  ");
  if (presenterLine) {
    s.addText(presenterLine, {
      x: MARGIN,
      y: SLIDE_H - 1.1,
      w: SLIDE_W - MARGIN * 2,
      h: 0.5,
      fontFace: FONT,
      fontSize: 14,
      color: TEXT,
      align: "left",
      margin: 0,
    });
  }
  addNotesIfAny(s, item);
}

function renderAgenda(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title || "Agenda");
  const items = item.items || [];
  const twoCol = items.length > 5;
  const colW = twoCol ? (SLIDE_W - MARGIN * 2 - 0.4) / 2 : SLIDE_W - MARGIN * 2;
  const rows = twoCol ? Math.ceil(items.length / 2) : items.length;
  const rowH = Math.min(0.9, (SLIDE_H - 2.2) / rows);

  items.forEach((txt, i) => {
    const col = twoCol ? Math.floor(i / rows) : 0;
    const row = twoCol ? i % rows : i;
    const x = MARGIN + col * (colW + 0.4);
    const y = 1.6 + row * rowH;
    s.addText(String(i + 1).padStart(2, "0"), {
      x, y, w: 0.7, h: rowH - 0.15,
      fontFace: FONT, fontSize: 20, bold: true, color: ACCENT, margin: 0, valign: "middle",
    });
    s.addText(txt, {
      x: x + 0.75, y, w: colW - 0.75, h: rowH - 0.15,
      fontFace: FONT, fontSize: 17, color: TEXT, margin: 0, valign: "middle",
    });
  });
  addNotesIfAny(s, item);
}

function renderProblemFriction(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  const halfW = (SLIDE_W - MARGIN * 2 - 0.4) / 2;
  const cardY = 1.7;
  const cardH = SLIDE_H - cardY - 0.7;

  const left = item.before || item.problem || {};
  const right = item.after || item.solution || {};

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: MARGIN, y: cardY, w: halfW, h: cardH, rectRadius: 0.08,
    fill: { color: CARD_BG }, line: { type: "none" },
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: MARGIN + halfW + 0.4, y: cardY, w: halfW, h: cardH, rectRadius: 0.08,
    fill: { color: CARD_BG }, line: { type: "none" },
  });
  s.addText(left.label || "Before", {
    x: MARGIN + 0.3, y: cardY + 0.25, w: halfW - 0.6, h: 0.5,
    fontFace: FONT, fontSize: 16, bold: true, color: ACCENT2, margin: 0,
  });
  s.addText(left.text || "", {
    x: MARGIN + 0.3, y: cardY + 0.85, w: halfW - 0.6, h: cardH - 1.1,
    fontFace: FONT, fontSize: 15, color: TEXT, margin: 0, valign: "top",
  });
  s.addText(right.label || "After", {
    x: MARGIN + halfW + 0.7, y: cardY + 0.25, w: halfW - 0.6, h: 0.5,
    fontFace: FONT, fontSize: 16, bold: true, color: ACCENT, margin: 0,
  });
  s.addText(right.text || "", {
    x: MARGIN + halfW + 0.7, y: cardY + 0.85, w: halfW - 0.6, h: cardH - 1.1,
    fontFace: FONT, fontSize: 15, color: TEXT, margin: 0, valign: "top",
  });
  addNotesIfAny(s, item);
}

function renderKeyConcept(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  const points = item.points || item.items || [];
  const textX = item.image ? MARGIN + 4.2 : MARGIN;
  const textW = item.image ? SLIDE_W - textX - MARGIN : SLIDE_W - MARGIN * 2;

  if (item.image && fs.existsSync(item.image)) {
    s.addImage({ path: item.image, x: MARGIN, y: 1.7, w: 3.6, h: 3.6 });
  } else {
    // Accent numeral block as a visual anchor even without an image
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: MARGIN, y: 1.9, w: 3.6, h: 3.2, rectRadius: 0.1,
      fill: { color: CARD_BG }, line: { type: "none" },
    });
    if (item.image !== false && !item.no_visual) {
      s.addText(String(idx + 1).padStart(2, "0"), {
        x: MARGIN, y: 1.9, w: 3.6, h: 3.2, fontFace: FONT, fontSize: 72, bold: true,
        color: ACCENT, align: "center", valign: "middle", margin: 0,
      });
    }
  }

  let y = 1.75;
  points.forEach((p) => {
    s.addShape(pres.shapes.OVAL, { x: textX, y: y + 0.12, w: 0.12, h: 0.12, fill: { color: ACCENT }, line: { type: "none" } });
    s.addText(p, {
      x: textX + 0.3, y, w: textW - 0.3, h: 0.75,
      fontFace: FONT, fontSize: 16, color: TEXT, margin: 0, valign: "top",
    });
    y += 0.85;
  });
  addNotesIfAny(s, item);
}

function renderTopology(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  const hasCallouts = item.callouts && item.callouts.length;
  const diagW = hasCallouts ? SLIDE_W - MARGIN * 2 - 3.6 : SLIDE_W - MARGIN * 2;

  if (item.diagram_image && fs.existsSync(item.diagram_image)) {
    s.addImage({ path: item.diagram_image, x: MARGIN, y: 1.6, w: diagW, h: SLIDE_H - 2.3, sizing: { type: "contain", w: diagW, h: SLIDE_H - 2.3 } });
  } else {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: MARGIN, y: 1.6, w: diagW, h: SLIDE_H - 2.3, rectRadius: 0.08,
      fill: { color: CARD_BG }, line: { type: "none" },
    });
    s.addText("Diagram unavailable — see speaker notes", {
      x: MARGIN, y: 1.6, w: diagW, h: SLIDE_H - 2.3, fontFace: FONT, fontSize: 14,
      color: TEXT, align: "center", valign: "middle", margin: 0,
    });
  }

  if (hasCallouts) {
    let y = 1.7;
    const calloutX = MARGIN + diagW + 0.4;
    const calloutW = SLIDE_W - MARGIN - calloutX;
    item.callouts.forEach((c, i) => {
      s.addShape(pres.shapes.OVAL, {
        x: calloutX, y, w: 0.35, h: 0.35, fill: { color: ACCENT }, line: { type: "none" },
      });
      s.addText(String(i + 1), {
        x: calloutX, y, w: 0.35, h: 0.35, fontFace: FONT, fontSize: 13, bold: true,
        color: mode === "light" ? "FFFFFF" : "0B132B", align: "center", valign: "middle", margin: 0,
      });
      s.addText(c, {
        x: calloutX + 0.5, y: y - 0.05, w: calloutW - 0.5, h: 0.85,
        fontFace: FONT, fontSize: 12.5, color: TEXT, margin: 0, valign: "top",
      });
      y += 1.0;
    });
  }
  addNotesIfAny(s, item);
}

function renderDeepDive(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  const layers = item.layers || item.items || [];
  const y0 = 1.7;
  const gap = 0.18;
  const h = Math.min(0.95, (SLIDE_H - y0 - 0.6 - gap * (layers.length - 1)) / layers.length);
  layers.forEach((l, i) => {
    const y = y0 + i * (h + gap);
    const label = typeof l === "string" ? l : l.label;
    const desc = typeof l === "string" ? "" : (l.text || "");
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: MARGIN + i * 0.15, y, w: SLIDE_W - MARGIN * 2 - i * 0.3, h, rectRadius: 0.06,
      fill: { color: CARD_BG }, line: { type: "none" },
      shadow: { type: "outer", color: "000000", opacity: 0.25, blur: 6, offset: 2, angle: 90 },
    });
    s.addText(label, {
      x: MARGIN + i * 0.15 + 0.25, y, w: 3, h, fontFace: FONT, fontSize: 15, bold: true,
      color: ACCENT, valign: "middle", margin: 0,
    });
    if (desc) {
      s.addText(desc, {
        x: MARGIN + i * 0.15 + 3.2, y, w: SLIDE_W - MARGIN * 2 - i * 0.3 - 3.4, h,
        fontFace: FONT, fontSize: 13, color: TEXT, valign: "middle", margin: 0,
      });
    }
  });
  addNotesIfAny(s, item);
}

function renderCodeSpec(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  const code = item.code || "";
  const lines = code.split("\n");
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: MARGIN, y: 1.6, w: SLIDE_W - MARGIN * 2, h: SLIDE_H - 2.3, rectRadius: 0.06,
    fill: { color: "0B0F19" }, line: { type: "none" },
  });
  s.addText(
    lines.map((l, i) => ({
      text: l,
      options: { breakLine: i < lines.length - 1 },
    })),
    {
      x: MARGIN + 0.35, y: 1.85, w: SLIDE_W - MARGIN * 2 - 0.7, h: SLIDE_H - 2.8,
      fontFace: "Consolas", fontSize: 13.5, color: "D4D4D4", valign: "top", margin: 0,
      lineSpacingMultiple: 1.25,
    }
  );
  if (item.language) {
    s.addText(item.language.toUpperCase(), {
      x: SLIDE_W - MARGIN - 1.4, y: 1.65, w: 1.1, h: 0.35, fontFace: FONT, fontSize: 10,
      color: ACCENT, align: "right", margin: 0,
    });
  }
  addNotesIfAny(s, item);
}

function renderComparison(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  const cols = item.columns || [];
  const n = cols.length;
  const colW = (SLIDE_W - MARGIN * 2 - 0.3 * (n - 1)) / n;
  const y0 = 1.6;
  const headerH = 0.6;
  const maxRows = Math.max(...cols.map((c) => c.rows.length));
  const rowH = Math.min(0.55, (SLIDE_H - y0 - headerH - 0.6) / maxRows);
  const chipColors = { AWS: "FF9900", GCP: "4285F4", Azure: "0078D4" };

  cols.forEach((col, ci) => {
    const x = MARGIN + ci * (colW + 0.3);
    const headerColor = chipColors[col.name] || ACCENT;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y: y0, w: colW, h: headerH, rectRadius: 0.05,
      fill: { color: headerColor }, line: { type: "none" },
    });
    s.addText(col.name, {
      x, y: y0, w: colW, h: headerH, fontFace: FONT, fontSize: 15, bold: true,
      color: "FFFFFF", align: "center", valign: "middle", margin: 0,
    });
    col.rows.forEach((r, ri) => {
      const y = y0 + headerH + 0.1 + ri * (rowH + 0.06);
      s.addShape(pres.shapes.RECTANGLE, {
        x, y, w: colW, h: rowH,
        fill: { color: CARD_BG }, line: { type: "none" },
      });
      s.addText(r, {
        x: x + 0.15, y, w: colW - 0.3, h: rowH, fontFace: FONT, fontSize: 12.5,
        color: TEXT, align: "center", valign: "middle", margin: 0,
      });
    });
  });
  addNotesIfAny(s, item);
}

function renderTimeline(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  const items = item.items || [];
  const n = items.length;
  const lineY = 4.0;
  const startX = MARGIN + 0.5;
  const endX = SLIDE_W - MARGIN - 0.5;
  s.addShape(pres.shapes.LINE, {
    x: startX, y: lineY, w: endX - startX, h: 0,
    line: { color: ACCENT, width: 2 },
  });
  items.forEach((it, i) => {
    const x = startX + (i / Math.max(n - 1, 1)) * (endX - startX);
    const above = i % 2 === 0;
    s.addShape(pres.shapes.OVAL, {
      x: x - 0.08, y: lineY - 0.08, w: 0.16, h: 0.16, fill: { color: ACCENT }, line: { type: "none" },
    });
    const labelY = above ? lineY - 1.5 : lineY + 0.3;
    s.addText(it.date || "", {
      x: x - 0.9, y: above ? lineY - 0.75 : lineY + 1.1, w: 1.8, h: 0.3,
      fontFace: FONT, fontSize: 11, color: ACCENT2, align: "center", margin: 0,
    });
    s.addText(it.label || "", {
      x: x - 0.9, y: labelY, w: 1.8, h: 0.7,
      fontFace: FONT, fontSize: 12.5, color: TEXT, align: "center", margin: 0, valign: "top",
    });
  });
  addNotesIfAny(s, item);
}

function renderBenchmarkMatrix(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  if (item.chart_type === "table" || !item.series) {
    // simple table fallback
    const rows = item.rows || [];
    const y0 = 1.7;
    const rowH = Math.min(0.5, (SLIDE_H - y0 - 0.6) / (rows.length + 1));
    const headers = item.headers || [];
    const colW = (SLIDE_W - MARGIN * 2) / headers.length;
    headers.forEach((h, ci) => {
      s.addShape(pres.shapes.RECTANGLE, { x: MARGIN + ci * colW, y: y0, w: colW, h: rowH, fill: { color: ACCENT }, line: { type: "none" } });
      s.addText(h, { x: MARGIN + ci * colW, y: y0, w: colW, h: rowH, fontFace: FONT, fontSize: 13, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
    });
    rows.forEach((r, ri) => {
      r.forEach((val, ci) => {
        const y = y0 + (ri + 1) * rowH;
        s.addShape(pres.shapes.RECTANGLE, { x: MARGIN + ci * colW, y, w: colW, h: rowH, fill: { color: CARD_BG }, line: { color: BG, width: 1 } });
        s.addText(String(val), { x: MARGIN + ci * colW, y, w: colW, h: rowH, fontFace: FONT, fontSize: 12, color: TEXT, align: "center", valign: "middle", margin: 0 });
      });
    });
  } else {
    const chartType = item.chart_type === "line" ? pres.ChartType.line : pres.ChartType.bar;
    s.addChart(
      chartType,
      item.series.map((ser) => ({ name: ser.name, labels: item.categories, values: ser.values })),
      {
        x: MARGIN, y: 1.7, w: SLIDE_W - MARGIN * 2, h: SLIDE_H - 2.4,
        showTitle: false,
        showValue: true,
        dataLabelPosition: "outEnd",
        chartColors: [ACCENT, ACCENT2, "8C8C8C"],
        catAxisLabelColor: TEXT,
        valAxisLabelColor: TEXT,
        valGridLine: { color: CARD_BG, size: 1 },
        catGridLine: { style: "none" },
        showLegend: item.series.length > 1,
        legendColor: TEXT,
      }
    );
  }
  addNotesIfAny(s, item);
}

function renderProductionGotchas(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  const items = item.items || [];
  const y0 = 1.7;
  const gap = 0.25;
  const h = Math.min(1.1, (SLIDE_H - y0 - 0.6 - gap * (items.length - 1)) / items.length);
  items.forEach((txt, i) => {
    const y = y0 + i * (h + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: MARGIN, y, w: SLIDE_W - MARGIN * 2, h, rectRadius: 0.06,
      fill: { color: CARD_BG }, line: { type: "none" },
    });
    s.addShape(pres.shapes.OVAL, {
      x: MARGIN + 0.25, y: y + h / 2 - 0.22, w: 0.44, h: 0.44,
      fill: { color: ACCENT }, line: { type: "none" },
    });
    s.addText(String(i + 1), {
      x: MARGIN + 0.25, y: y + h / 2 - 0.22, w: 0.44, h: 0.44, fontFace: FONT, fontSize: 15, bold: true,
      color: mode === "light" ? "FFFFFF" : "0B132B", align: "center", valign: "middle", margin: 0,
    });
    s.addText(txt, {
      x: MARGIN + 0.9, y, w: SLIDE_W - MARGIN * 2 - 1.1, h, fontFace: FONT, fontSize: 14.5,
      color: TEXT, valign: "middle", margin: 0,
    });
  });
  addNotesIfAny(s, item);
}

function renderDemo(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title);
  if (item.image && fs.existsSync(item.image)) {
    s.addImage({ path: item.image, x: MARGIN, y: 1.6, w: SLIDE_W - MARGIN * 2, h: SLIDE_H - 2.3, sizing: { type: "contain", w: SLIDE_W - MARGIN * 2, h: SLIDE_H - 2.3 } });
  } else {
    const steps = item.steps || item.items || [];
    let y = 1.8;
    steps.forEach((st, i) => {
      s.addText(`${i + 1}.`, { x: MARGIN, y, w: 0.5, h: 0.6, fontFace: FONT, fontSize: 16, bold: true, color: ACCENT, margin: 0 });
      s.addText(st, { x: MARGIN + 0.55, y, w: SLIDE_W - MARGIN * 2 - 0.55, h: 0.6, fontFace: FONT, fontSize: 15, color: TEXT, margin: 0, valign: "top" });
      y += 0.7;
    });
  }
  addNotesIfAny(s, item);
}

function renderQuote(item, idx) {
  const s = baseSlide();
  s.addText(`"${item.text || ""}"`, {
    x: MARGIN + 0.5, y: 2.4, w: SLIDE_W - MARGIN * 2 - 1, h: 2.2,
    fontFace: FONT, fontSize: 26, italic: true, color: TITLE_COLOR, align: "left", margin: 0, valign: "middle",
  });
  if (item.attribution) {
    s.addText(`— ${item.attribution}`, {
      x: MARGIN + 0.5, y: 4.7, w: SLIDE_W - MARGIN * 2 - 1, h: 0.5,
      fontFace: FONT, fontSize: 15, color: ACCENT2, align: "left", margin: 0,
    });
  }
  addNotesIfAny(s, item);
}

function renderResources(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title || "Resources");
  const halfW = (SLIDE_W - MARGIN * 2 - 0.4) / 2;
  const y0 = 1.7;

  function col(x, label, links) {
    s.addText(label, { x, y: y0, w: halfW, h: 0.45, fontFace: FONT, fontSize: 15, bold: true, color: ACCENT, margin: 0 });
    let y = y0 + 0.55;
    (links || []).forEach((l) => {
      s.addText(l.label || l.url, {
        x, y, w: halfW, h: 0.45, fontFace: FONT, fontSize: 13, color: TEXT, margin: 0, valign: "top",
        hyperlink: l.url ? { url: l.url } : undefined,
      });
      y += 0.55;
    });
  }
  col(MARGIN, "Official Docs", item.docs);
  col(MARGIN + halfW + 0.4, "GitHub & Community", item.repos);
  addNotesIfAny(s, item);
}

function renderSpeaker(item, idx) {
  const s = baseSlide();
  titleBlock(s, item.title || "Speaker");
  const photoW = 2.6;
  const hasPhoto = item.photo && fs.existsSync(item.photo);

  if (hasPhoto) {
    s.addImage({ path: item.photo, x: MARGIN, y: 1.7, w: photoW, h: photoW, sizing: { type: "cover", w: photoW, h: photoW } });
  } else {
    s.addShape(pres.shapes.OVAL, {
      x: MARGIN, y: 1.7, w: photoW, h: photoW, fill: { color: CARD_BG }, line: { color: ACCENT, width: 2 },
    });
    const initials = (item.name || "?").split(/\s+/).map((w) => w[0]).slice(0, 2).join("").toUpperCase();
    s.addText(initials, {
      x: MARGIN, y: 1.7, w: photoW, h: photoW, fontFace: FONT, fontSize: 44, bold: true,
      color: ACCENT, align: "center", valign: "middle", margin: 0,
    });
  }

  const textX = MARGIN + photoW + 0.5;
  const textW = SLIDE_W - textX - MARGIN;
  let y = 1.75;

  s.addText(item.name || "", {
    x: textX, y, w: textW, h: 0.55, fontFace: FONT, fontSize: 24, bold: true, color: TITLE_COLOR, margin: 0,
  });
  y += 0.6;
  if (item.role) {
    s.addText(item.role, {
      x: textX, y, w: textW, h: 0.4, fontFace: FONT, fontSize: 15, color: ACCENT2, margin: 0,
    });
    y += 0.5;
  }
  if (item.bio) {
    s.addText(item.bio, {
      x: textX, y, w: textW, h: 1.6, fontFace: FONT, fontSize: 13.5, color: TEXT, margin: 0, valign: "top",
      lineSpacingMultiple: 1.2,
    });
    y += 1.7;
  }
  const contacts = item.contacts || [];
  contacts.forEach((c) => {
    s.addText(c.label ? `${c.label}: ${c.value}` : (c.value || ""), {
      x: textX, y, w: textW, h: 0.35, fontFace: FONT, fontSize: 12.5, color: ACCENT,
      margin: 0, hyperlink: c.url ? { url: c.url } : undefined,
    });
    y += 0.4;
  });
  addNotesIfAny(s, item);
}

function renderCallToAction(item, idx) {
  const s = baseSlide(ACCENT);
  const onAccentText = "FFFFFF";
  s.addText(item.title || "Thank You", {
    x: MARGIN, y: 1.8, w: SLIDE_W - MARGIN * 2, h: 1, fontFace: FONT, fontSize: 34, bold: true,
    color: onAccentText, align: "center", margin: 0,
  });
  const items = item.items || [];
  let y = 3.0;
  items.forEach((txt) => {
    s.addText(`• ${txt}`, {
      x: MARGIN + 1, y, w: SLIDE_W - MARGIN * 2 - 2, h: 0.5, fontFace: FONT, fontSize: 16,
      color: onAccentText, align: "center", margin: 0,
    });
    y += 0.55;
  });
  if (item.handles && item.handles.length) {
    s.addText(item.handles.join("   |   "), {
      x: MARGIN, y: SLIDE_H - 1.1, w: SLIDE_W - MARGIN * 2, h: 0.5, fontFace: FONT, fontSize: 14,
      color: onAccentText, align: "center", margin: 0,
    });
  }
  addNotesIfAny(s, item);
}

const RENDERERS = {
  Title: renderTitle,
  Agenda: renderAgenda,
  ProblemFriction: renderProblemFriction,
  KeyConcept: renderKeyConcept,
  Topology: renderTopology,
  DeepDive: renderDeepDive,
  CodeSpec: renderCodeSpec,
  Comparison: renderComparison,
  Timeline: renderTimeline,
  BenchmarkMatrix: renderBenchmarkMatrix,
  ProductionGotchas: renderProductionGotchas,
  Demo: renderDemo,
  Quote: renderQuote,
  Resources: renderResources,
  Speaker: renderSpeaker,
  CallToAction: renderCallToAction,
};

(plan.slides || []).forEach((item, idx) => {
  const renderer = RENDERERS[item.archetype];
  if (!renderer) {
    console.error(`[WARNING] Slide ${idx + 1}: Unknown archetype "${item.archetype}" — skipping. Valid archetypes: ${Object.keys(RENDERERS).join(", ")}`);
    return;
  }
  try {
    renderer(item, idx);
  } catch (e) {
    console.error(`[ERROR] Slide ${idx + 1} (${item.archetype}): ${e.message}`);
    // Continue rendering other slides instead of crashing
  }
});

const outDir = path.dirname(outPath);
if (!fs.existsSync(outDir)) {
  try {
    fs.mkdirSync(outDir, { recursive: true });
  } catch (e) {
    console.error(`[ERROR] Failed to create output directory: ${e.message}`);
    process.exit(1);
  }
}

console.log(`[INFO] Writing PPTX to: ${outPath}`);
pres
  .writeFile({ fileName: outPath })
  .then(() => {
    const sizeKB = Math.round(fs.statSync(outPath).size / 1024);
    console.log(`[INFO] Successfully wrote ${outPath} (${sizeKB} KB)`);
  })
  .catch((err) => {
    console.error(`[ERROR] Failed to write PPTX: ${err.message}`);
    if (fs.existsSync(outPath)) {
      try {
        fs.unlinkSync(outPath);
      } catch (e) {
        // Ignore cleanup errors
      }
    }
    process.exit(1);
  });
