import type { NextConfig } from "next";

const PROD = true;

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: PROD 
      ? 'https://mm8yf29n32.us-east-1.awsapprunner.com'
      : 'http://localhost:8000',
  },
};

export default nextConfig;
