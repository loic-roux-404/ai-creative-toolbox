terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.73.1"
    }
  }
}

provider "google" {
  region  = var.region
  zone    = var.zone
}

module "iam" {
  source  = "terraform-google-modules/iam/google"
  version = "7.6.0"
}
