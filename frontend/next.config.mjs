/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'media.api-sports.io',
      },
      {
        protocol: 'https',
        hostname: 'media.apifootball.com',
      },
      {
        protocol: 'https',
        hostname: 'api.sofascore.com',
      },
      {
        protocol: 'https',
        hostname: 'img.sofascore.com',
      },
      {
        protocol: 'https',
        hostname: 'www.sofascore.com',
      },
    ],
  },
}

export default nextConfig
