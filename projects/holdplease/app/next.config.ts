import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Allow images from Google (for user avatars)
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
      },
    ],
  },
  // External packages that need Node.js (not bundled for Edge)
  serverExternalPackages: ['better-sqlite3'],
  // Tell Turbopack this app is the root
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;
