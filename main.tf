resource "google_project" "project" {
  name       = var.project_name
  project_id = var.project_id
}

resource "google_service_account" "account" {
  account_id   = "admin-synthesis"
  display_name = "Main Synthesis Admin"
  project      = google_project.project.project_id
}

resource "google_project_iam_binding" "binding" {
  project = google_project.project.project_id
  role    = "roles/editor"

  members = [
    "serviceAccount:${google_service_account.account.email}"
  ]
}

resource "google_service_account_key" "account_key" {
  service_account_id = google_service_account.account.name
}

resource "google_project_service" "gmail_api" {
  project = google_project.project.project_id
  service = "gmail.googleapis.com"
}
