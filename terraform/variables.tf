variable "region" {
  type    = string
  default = "europe-west3"
}

variable "zone" {
  type    = string
  default = "europe-west3-a"
}

variable "project_name" {
  type    = string
  default = null
}

variable "project_id" {
  type    = string
}

variable "gcp_service_list" {
  description ="The list of apis necessary for the project"
  type = list(string)
  default = [
    "photoslibrary.googleapis.com",
    "gmail.googleapis.com"
  ]
}

variable "user" {
  type = string
}
