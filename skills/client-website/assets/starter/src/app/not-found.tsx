import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: { absolute: "Page not found" },
  robots: { index: false, follow: false },
};

export default function NotFound() {
  return (
    <section>
      <h1>We could not find that page</h1>
      <p>
        The page may have moved. You can go to the <Link href="/">home page</Link> or{" "}
        <Link href="/contact">contact us</Link>.
      </p>
    </section>
  );
}
