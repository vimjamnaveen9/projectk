output "infrastructure_dashboard_url" {
  description = "URL to infrastructure CloudWatch dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.infrastructure.dashboard_name}"
}

output "application_dashboard_url" {
  description = "URL to application CloudWatch dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.application.dashboard_name}"
}

output "log_group_names" {
  description = "Names of CloudWatch log groups"
  value = [
    aws_cloudwatch_log_group.app_logs.name,
    aws_cloudwatch_log_group.system_logs.name,
    aws_cloudwatch_log_group.security_logs.name,
    aws_cloudwatch_log_group.alb_access_logs.name
  ]
}

output "dashboard_names" {
  description = "Names of CloudWatch dashboards"
  value = [
    aws_cloudwatch_dashboard.infrastructure.dashboard_name,
    aws_cloudwatch_dashboard.application.dashboard_name
  ]
}

output "alarm_names" {
  description = "Names of CloudWatch alarms"
  value = [
    aws_cloudwatch_metric_alarm.rds_cpu_high.alarm_name,
    aws_cloudwatch_metric_alarm.rds_connections_high.alarm_name,
    aws_cloudwatch_metric_alarm.alb_response_time_high.alarm_name,
    aws_cloudwatch_metric_alarm.alb_5xx_errors.alarm_name
  ]
}