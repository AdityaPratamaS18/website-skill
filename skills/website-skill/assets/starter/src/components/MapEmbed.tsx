import { site } from "@/lib/site";

/* A Google Maps frame that needs no API key. It uses the pin in site.geo,
   or the address if the pin is not known. It loads only when it scrolls
   into view, so it does not slow the first view. */
export default function MapEmbed({ height = 360 }: { height?: number }) {
  const { lat, lng } = site.geo;
  const a = site.address;
  const query =
    lat !== null && lng !== null
      ? `${lat},${lng}`
      : [site.name, a.street, a.city, a.country].filter(Boolean).join(", ");
  const src = `https://maps.google.com/maps?q=${encodeURIComponent(query)}&z=16&output=embed`;
  return (
    <iframe
      src={src}
      title={`Map: ${site.name}`}
      width="100%"
      height={height}
      loading="lazy"
      referrerPolicy="no-referrer-when-downgrade"
      style={{ border: 0 }}
      allowFullScreen
    />
  );
}
