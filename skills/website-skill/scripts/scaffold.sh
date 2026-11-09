#!/usr/bin/env bash
# Makes a new Next.js project and adds the SEO starter files.
# create-next-app rejects paths with spaces or capital letters, so the project
# is made in a temporary folder and then copied to the target.
# Usage: scaffold.sh <target-dir> <static|server>
set -euo pipefail

target="${1:?Usage: scaffold.sh <target-dir> <static|server>}"
mode="${2:?Usage: scaffold.sh <target-dir> <static|server>}"
skill="$(cd "$(dirname "$0")/.." && pwd)"

case "$mode" in
  static|server) ;;
  *) echo "FAIL: mode must be static or server" >&2; exit 1 ;;
esac

if [ -e "$target/package.json" ]; then
  echo "FAIL: $target already has a package.json. This script does not overwrite a project." >&2
  exit 1
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

(cd "$work" && npx --yes create-next-app@latest site --ts --tailwind --eslint --app \
  --src-dir --import-alias "@/*" --use-npm --disable-git --yes)

mkdir -p "$target"
rsync -a "$work/site/" "$target/"
rsync -a "$skill/assets/starter/" "$target/"
cp "$skill/assets/site-plan.template.json" "$target/src/lib/site-plan.json"
rm -f "$target"/public/{file,globe,next,vercel,window}.svg "$target/src/app/favicon.ico"

package_name="$(basename "$(cd "$target" && pwd)" | tr '[:upper:] ' '[:lower:]-')"
if [ "$package_name" = "website" ]; then
  package_name="$(basename "$(cd "$target/.." && pwd)" | tr '[:upper:] ' '[:lower:]-')-website"
fi
(cd "$target" && npm pkg set name="$package_name" >/dev/null)

# Keep the generated config, because its turbopack rule compiles Tailwind.
# cacheComponents rejects the force-static exports in sitemap.ts and robots.ts.
MODE="$mode" python3 - "$target/next.config.ts" <<'PYEOF'
import os, re, sys
path = sys.argv[1]
text = open(path).read()
text = re.sub(r"^\s*(cacheComponents|partialPrefetching): true,\n", "", text, flags=re.M)
text = re.sub(r"^\s*/\* config options here \*/\n", "", text, flags=re.M)
if os.environ["MODE"] == "static":
    marker = "const nextConfig: NextConfig = {\n"
    if marker not in text:
        sys.exit("FAIL: next.config.ts has an unknown format")
    note = (
        "  /* A static site in out/. next/image does not resize here,\n"
        "     so each source image must be the correct size. */\n"
        '  output: "export",\n'
        "  images: { unoptimized: true },\n"
    )
    text = text.replace(marker, marker + note, 1)
open(path, "w").write(text)
PYEOF

echo "OK: $target is ready in $mode mode ($(cd "$target" && node -p "require('next/package.json').version") of Next.js)."
