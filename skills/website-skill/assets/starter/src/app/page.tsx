import { getPage, pageMetadata } from "@/lib/seo";

export const metadata = pageMetadata("/");

export default function HomePage() {
  const page = getPage("/");
  return <h1>{page.h1}</h1>;
}
