// Entry program for the news-image-20261125 bounty (Node 22, standard
// library only). The finished front page is the entry.png file beside this
// program; all this program does is copy it into the output directory the
// grader reads. To try it locally:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from "node:fs";
import { join } from "node:path";

const image = new URL("./entry.png", import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
copyFileSync(image, join(outDir, "entry.png"));
