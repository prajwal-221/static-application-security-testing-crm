# BlinkIt Clone - Terraform & ECS Workshop Environment

This directory contains the Terraform configuration to deploy the BlinkIt Clone application on AWS ECS using EC2 Capacity Provider (for cost optimization).

## Architecture

- **Compute**: Single EC2 instance (t3.medium) managed by ECS Capacity Provider & Auto Scaling Group.
- **Networking**: VPC (New or Existing), Public Subnets for ALB, Private/Public Subnets for Workloads.
- **Load Balancer**: Application Load Balancer (OSI Layer 7) handling traffic for Frontend (port 80) and Backend (port 8080).
- **Service Discovery**: Route 53 Private Hosted Zone (`blinkit.internal`) for service-to-service communication.
- **Database**: MongoDB running as a container on the ECS instance with data persisted to an EBS volume.
- **Frontend**: React application served via Nginx.
- **Backend**: Node.js/Express application.

## Prerequisites

1.  **AWS CLI** installed and configured (`aws configure`).
2.  **Terraform** installed (v1.5+).
3.  **Docker** installed (for building images).

## Setup Instructions

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Configure Variables

Create a `terraform.tfvars` file from the example:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your settings:
- **Secrets**: Update `access_token_secret` and `refresh_token_secret`.
- **Networking**:
    - Default: Creates a new VPC (easiest for workshop).
    - Optional: Uncomment `vpc_id` and subnet variables to use an existing VPC.

### 3. Deploy Infrastructure

```bash
terraform plan
terraform apply
# Type 'yes' to confirm
```

Wait for the deployment to finish (approx. 5-10 minutes).

### 4. Build and Push Docker Images

Once Terraform completes, it will output the ECR repository URLs and login command.

**Login to ECR:**
```bash
# Run the command output by Terraform, e.g.:
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

**Build and Push Frontend:**
```bash
# From the root of the project (Client directory)
cd ../client
# IMPORTANT: Build with empty API URL so it uses relative paths (ALB handles routing)
docker build -t blinkit-frontend --build-arg VITE_API_URL="" .

# Tag and Push
docker tag blinkit-frontend:latest <ECR_FRONTEND_URL>:latest
docker push <ECR_FRONTEND_URL>:latest
```

**Build and Push Backend:**
```bash
cd ../server
docker build -t blinkit-backend .

# Tag and Push
docker tag blinkit-backend:latest <ECR_BACKEND_URL>:latest
docker push <ECR_BACKEND_URL>:latest
```

### 5. Start/Restart ECS Services

After pushing the images, you might need to force a new deployment if the services are already trying to start with missing images:

```bash
aws ecs update-service --cluster <CLUSTER_NAME> --service backend --force-new-deployment
aws ecs update-service --cluster <CLUSTER_NAME> --service frontend --force-new-deployment
```

### 6. Access the Application

Go to the `alb_url` printed in the Terraform outputs.
Example: `http://blinkit-workshop-alb-123456789.us-east-1.elb.amazonaws.com`

## Cost Estimation (Workshop Mode)

- **EC2 (t3.medium)**: ~$30/month ($0.04/hour)
- **ALB**: ~$16/month (+$0.008/LCU-hour)
- **EBS (30GB)**: ~$3/month
- **Route 53**: ~$0.50/month
- **NAT Gateway (if configured)**: ~$32/month (Standard AWS NAT)
    - *Tip: If you use the existing VPC option with public subnets, you can avoid NAT Gateway costs by putting instances in public subnets (adjust security groups accordingly).*

**Total for a 4-hour workshop:** < $1.00 (excluding one-time resources like NAT Gateway allocation if not destroyed immediately).

## Cleanup

To avoid ongoing charges, destroy the infrastructure when done:

```bash
terraform destroy
```

Note: This will delete the MongoDB data stored on the EC2 instance volume.
