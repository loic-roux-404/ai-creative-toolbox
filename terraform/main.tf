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

# Need an organization to create a brand
# resource "google_project_service" "project_service" {
#   project = google_project.project.project_id
#   service = "iap.googleapis.com"
# }

# resource "google_iap_brand" "project_brand" {
#   support_email     = "69loloro10@gmail.com"
#   application_title = "Cloud IAP protected Application"
#   project           = google_project_service.project_service.project
# }

# resource "google_iap_client" "project_client" {
#   display_name = "Letter Synthesis App"
#   brand        =  google_iap_brand.project_brand.name
# }
