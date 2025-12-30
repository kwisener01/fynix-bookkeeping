/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // PWA configuration
  async headers() {
    return [
      {
        source: '/sw.js',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=0, must-revalidate',
          },
          {
            key: 'Service-Worker-Allowed',
            value: '/',
          },
        ],
      },
      {
        source: '/manifest.json',
        headers: [
          {
            key: 'Content-Type',
            value: 'application/manifest+json',
          },
        ],
      },
    ];
  },

  // Optimize images
  images: {
    domains: ['supabase.co'],
    formats: ['image/avif', 'image/webp'],
  },

  // Experimental features
  experimental: {
    // optimizeCss: true,  // Disabled - requires critters package
  },
};

module.exports = nextConfig;
