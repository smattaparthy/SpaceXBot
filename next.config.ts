import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Dev server only: let phones and other machines on the local network load
  // the page by IP or .local name (otherwise the page never becomes interactive).
  allowedDevOrigins: ["10.*.*.*", "172.*.*.*", "192.168.*.*", "*.local"],

  // The browser calls /api/* on the frontend's own origin and Next.js forwards
  // it to the backend, so the chat works from any device and needs no CORS.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/:path*`,
      },
    ];
  },
};

export default nextConfig;
