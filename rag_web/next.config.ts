import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    // NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_API_URL: 'https://mm8yf29n32.us-east-1.awsapprunner.com' || 'http://localhost:8000',
  },
};

export default nextConfig;
