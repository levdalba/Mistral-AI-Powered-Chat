/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode for better development experience
  reactStrictMode: true,
  
  // Enable SWC minification for better performance
  swcMinify: true,
  
  // Experimental features
  experimental: {
    // Enable App Router (stable in Next.js 13.4+)
    appDir: true,
    
    // Enable optimized images
    optimizeCss: true,
    
    // Enable edge runtime for better performance
    runtime: 'edge',
  },
  
  // Image optimization
  images: {
    domains: [],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Headers for security and performance
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
  
  // Redirects for better UX
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ];
  },
  
  // Webpack configuration for better optimization
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Optimize bundle analyzer
    if (process.env.ANALYZE) {
      const withBundleAnalyzer = require('@next/bundle-analyzer')({
        enabled: true,
      });
      return withBundleAnalyzer(config);
    }
    
    // Custom webpack configuration
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
    };
    
    return config;
  },
  
  // TypeScript configuration
  typescript: {
    // Allow production builds to successfully complete even if there are type errors
    ignoreBuildErrors: false,
  },
  
  // ESLint configuration
  eslint: {
    // Allow production builds to successfully complete even if there are lint errors
    ignoreDuringBuilds: false,
  },
  
  // Output configuration for static export (if needed)
  output: process.env.BUILD_STANDALONE === 'true' ? 'standalone' : undefined,
  
  // Trailing slash configuration
  trailingSlash: false,
  
  // PoweredByHeader
  poweredByHeader: false,
  
  // Compression
  compress: true,
};

module.exports = nextConfig;
