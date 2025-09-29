#!/bin/bash

# Docker deployment script for PharmaRAG
# This script builds and pushes the Docker image to AWS ECR

# Configuration variables
IMAGE_NAME="pharmarag"
IMAGE_TAG="latest"
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="627877014668"
ECR_REPOSITORY="pharmarag"

# Derived variables
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_FULL_NAME="${ECR_URI}/${ECR_REPOSITORY}:${IMAGE_TAG}"

echo "🚀 Starting Docker deployment for PharmaRAG"
echo "📦 Image: ${FULL_IMAGE_NAME}"
echo "🌍 Region: ${AWS_REGION}"
echo "🏷️  ECR URI: ${ECR_URI}"
echo ""

# Step 1: Build Docker image
echo "🔨 Building Docker image..."
docker build -t ${FULL_IMAGE_NAME} .
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi
echo "✅ Docker image built successfully"

# Step 2: Login to AWS ECR
echo "🔐 Logging into AWS ECR..."
aws ecr get-login-password --region ${AWS_REGION} --profile pafcio136 | docker login --username AWS --password-stdin ${ECR_URI}
if [ $? -ne 0 ]; then
    echo "❌ ECR login failed!"
    exit 1
fi
echo "✅ Successfully logged into ECR"

# Step 3: Tag image for ECR
echo "🏷️  Tagging image for ECR..."
docker tag ${FULL_IMAGE_NAME} ${ECR_FULL_NAME}
if [ $? -ne 0 ]; then
    echo "❌ Image tagging failed!"
    exit 1
fi
echo "✅ Image tagged successfully"

# Step 4: Push image to ECR
echo "📤 Pushing image to ECR..."
docker push ${ECR_FULL_NAME}
if [ $? -ne 0 ]; then
    echo "❌ Image push failed!"
    exit 1
fi
echo "✅ Image pushed successfully to ECR"

echo ""
echo "🎉 Deployment completed successfully!"
echo "📋 Image details:"
echo "   - Local: ${FULL_IMAGE_NAME}"
echo "   - ECR: ${ECR_FULL_NAME}"
echo ""
echo "🚀 Your image is now available in ECR and ready for deployment!"
