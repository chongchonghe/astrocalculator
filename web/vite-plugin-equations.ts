import type { Plugin } from 'vite';
import matter from 'gray-matter';
import { readdirSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

const EQUATIONS_DIR = 'equations';
const OUTPUT_FILE = 'src/data/equations.json';

export function equationsPlugin(): Plugin {
  return {
    name: 'vite-plugin-equations',
    buildStart() {
      const equationsDir = join(process.cwd(), EQUATIONS_DIR);

      let files: string[];
      try {
        files = readdirSync(equationsDir).filter((f) => f.endsWith('.md'));
      } catch {
        console.warn('No equations directory found, skipping');
        return;
      }

      const equations = files.map((file: string) => {
        const raw = readFileSync(join(equationsDir, file), 'utf8');
        const { data, content } = matter(raw);
        return {
          slug: file.replace(/\.md$/, ''),
          title: data.title || file,
          category: data.category || 'Uncategorized',
          tags: data.tags || [],
          params: data.params || [],
          expressions: data.expressions || [],
          body: content.trim() || undefined,
        };
      });

      const outDir = join(process.cwd(), 'src/data');
      mkdirSync(outDir, { recursive: true });
      writeFileSync(join(process.cwd(), OUTPUT_FILE), JSON.stringify(equations, null, 2));
      console.log(`Built ${equations.length} equation templates → ${OUTPUT_FILE}`);
    },
  };
}
