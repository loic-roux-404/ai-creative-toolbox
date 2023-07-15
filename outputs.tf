output "project_id" {
  value = google_project.project.project_id
}

output "service_account_email" {
  value = google_service_account.account.email
}

output "service_account_key" {
  value       = google_service_account_key.account_key.private_key
  description = "Service Account Key in JSON format"
  sensitive = true
}