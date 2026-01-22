# Networking Configuration
# Uses existing VPC if IDs provided, otherwise creates a dedicated VPC

locals {
  create_vpc = var.vpc_id == ""
}

# -------------------------------------------------------------------------------------------------
# DATA SOURCES (Existing Networking)
# -------------------------------------------------------------------------------------------------

data "aws_vpc" "existing" {
  count = var.vpc_id != "" ? 1 : 0
  id    = var.vpc_id
}

data "aws_subnet" "public" {
  count = var.vpc_id != "" ? length(var.public_subnet_ids) : 0
  id    = var.public_subnet_ids[count.index]
}

data "aws_subnet" "private" {
  count = var.vpc_id != "" ? length(var.private_subnet_ids) : 0
  id    = var.private_subnet_ids[count.index]
}

# -------------------------------------------------------------------------------------------------
# NEW NETWORK RESOURCES (Conditional)
# -------------------------------------------------------------------------------------------------

# VPC
resource "aws_vpc" "main" {
  count                = local.create_vpc ? 1 : 0
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.environment}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  count  = local.create_vpc ? 1 : 0
  vpc_id = aws_vpc.main[0].id

  tags = {
    Name = "${var.environment}-igw"
  }
}

# AZ Data Source
data "aws_availability_zones" "available" {
  state = "available"
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = local.create_vpc ? length(var.public_subnets_cidr) : 0
  vpc_id                  = aws_vpc.main[0].id
  cidr_block              = var.public_subnets_cidr[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = local.create_vpc ? length(var.private_subnets_cidr) : 0
  vpc_id            = aws_vpc.main[0].id
  cidr_block        = var.private_subnets_cidr[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.environment}-private-${count.index + 1}"
  }
}

# NAT Gateway (Single NAT for cost optimization)
resource "aws_eip" "nat" {
  count  = local.create_vpc ? 1 : 0
  domain = "vpc"
}

resource "aws_nat_gateway" "main" {
  count         = local.create_vpc ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.environment}-nat"
  }
  depends_on = [aws_internet_gateway.main]
}

# Route Tables - Public
resource "aws_route_table" "public" {
  count  = local.create_vpc ? 1 : 0
  vpc_id = aws_vpc.main[0].id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main[0].id
  }

  tags = {
    Name = "${var.environment}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = local.create_vpc ? length(var.public_subnets_cidr) : 0
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

# Route Tables - Private
resource "aws_route_table" "private" {
  count  = local.create_vpc ? 1 : 0
  vpc_id = aws_vpc.main[0].id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[0].id
  }

  tags = {
    Name = "${var.environment}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = local.create_vpc ? length(var.private_subnets_cidr) : 0
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[0].id
}

# -------------------------------------------------------------------------------------------------
# OUTPUTS (Normalized to handle conditional logic)
# -------------------------------------------------------------------------------------------------

locals {
  vpc_id             = local.create_vpc ? aws_vpc.main[0].id : var.vpc_id
  public_subnet_ids  = local.create_vpc ? aws_subnet.public[*].id : var.public_subnet_ids
  private_subnet_ids = local.create_vpc ? aws_subnet.private[*].id : var.private_subnet_ids
}
