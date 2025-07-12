#!/bin/bash

# This script creates a self-signed certificate and uploads it to AWS Certificate Manager (ACM)

# Set variables
DOMAIN_NAME="app.cloudjerry.xyz"  # Replace with your actual domain
REGION="us-east-2"         # Replace with your AWS region

# Create a directory for certificates
mkdir -p certs
cd certs

# Generate a private key
openssl genrsa -out private.key 2048

# Generate a Certificate Signing Request (CSR)
openssl req -new -key private.key -out csr.pem -subj "/CN=${DOMAIN_NAME}/O=Example Organization/C=US"

# Generate a self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in csr.pem -signkey private.key -out certificate.crt

# Upload the certificate to AWS Certificate Manager
echo "Uploading certificate to ACM..."
CERT_ARN=$(aws acm import-certificate \
  --certificate fileb://certificate.crt \
  --private-key fileb://private.key \
  --region ${REGION} \
  --output text)

echo "Certificate uploaded to ACM with ARN: ${CERT_ARN}"
echo "Update the ingress-nginx service with this ARN in the annotation:"
echo "service.beta.kubernetes.io/aws-load-balancer-ssl-cert: \"${CERT_ARN}\""

# For production, you should use a certificate from a trusted CA
echo ""
echo "NOTE: For production use, consider using AWS Certificate Manager to request a public certificate"
echo "or use Let's Encrypt with cert-manager in your Kubernetes cluster."
