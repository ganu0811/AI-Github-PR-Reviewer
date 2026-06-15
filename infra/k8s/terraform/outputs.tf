output "eks_cluster_environment" {
    description = "EKS cluster endpoint"
    value = module.eks.cluster_endpoint
}

output "rds_endpoint" {
    description = "RDS instance endpoint"
    value = aws_db_instance.postgres.endpoint
}

output "redis_environment" {
    description = "ElastiCache Redis endpoint"
    value = "${aws_elastiCache_cluster.redis.cache_nodes[0].address}:${aws_elastiCache_cluster.redis.cache_nodes[0].port}
}

output "ecr_gateway_url" {
    description = "ECR repository URL for gateway"
    value = aws_ecr_repository.gateway.repository_url
}

output  "ecr_webhook_url" {
    description = "ECR repository URL for orchestrator"
    value = aws_ecr_repository.orchestrator.repository_url
}

output "ecr_orchestrator_url" {
    description = "ECR repository URL for orchestrator"
    value = aws_ecr_repository.orchestrator.repository_url
}

output "ecr_reviewer_url" {
    description = "ECR repository URL for reviews"
    value = aws_ecr_repository.reviewer.repository_url
}

output "ecr_learner_url" {
    description = "ECR repository URL for learner"
    value = aws_ecr_repository.learner.repository_url
}


