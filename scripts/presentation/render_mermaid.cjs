const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

async function render(inputFile, outputFile) {
  const source = fs.readFileSync(inputFile, "utf8");
  const html = `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body {
      margin: 0;
      background: #0b1220;
      color: #e2e8f0;
      font-family: Arial, sans-serif;
    }
    #wrap {
      width: 1600px;
      min-height: 900px;
      padding: 24px;
      box-sizing: border-box;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .mermaid {
      background: transparent;
    }
  </style>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({
      startOnLoad: true,
      theme: 'dark',
      securityLevel: 'loose',
      flowchart: { curve: 'basis' },
      sequence: { actorMargin: 50, messageMargin: 40 }
    });
  </script>
</head>
<body>
    <div id="wrap">
      <pre class="mermaid">${source.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>
    </div>
</body>
</html>`;

  const htmlPath = path.resolve(path.dirname(outputFile), path.basename(outputFile, path.extname(outputFile)) + ".html");
  fs.writeFileSync(htmlPath, html, "utf8");

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 2200, height: 1240 }, deviceScaleFactor: 2 });
  await page.goto(`file://${htmlPath}`, { waitUntil: "networkidle" });
  await page.locator("#wrap").screenshot({ path: outputFile });
  await browser.close();
}

const [inputFile, outputFile] = process.argv.slice(2);
render(inputFile, outputFile).catch(err => {
  console.error(err);
  process.exit(1);
});
