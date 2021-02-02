
job "taylorinventory" {
  datacenters = ["webvig"]
  type = "service"

  update {
    max_parallel = 1
    min_healthy_time = "10s"
    healthy_deadline = "3m"
    progress_deadline = "10m"
    auto_revert = true
    canary = 0
  }

  migrate {
    max_parallel = 1
    health_check = "checks"
    min_healthy_time = "10s"
    healthy_deadline = "5m"
  }

  group "taylorinventory" {
    count = 2

    network {
      port "app" {
        to = 30600
      }
    }

    service {
      name = "taylorinventory"
      tags = ["django"]
      port = "app"
    }

    restart {
      attempts = 2
      interval = "30m"
      delay = "15s"
      mode = "fail"
    }

    ephemeral_disk {
      size = 300
    }

    task "taylorinventory" {
      driver = "docker"
      config {
        image = "registry.webvig.com/sirvig/taylorinventory:$VERSION_TAG"
        ports = ["app"]

        auth {
          username = "$REGISTRY_USER"
          password = "$REGISTRY_PASS"
        }
      }

      constraint {
        attribute = "${attr.unique.hostname}"
        value     = "wolowitz.webvig.local"       # stateful jobs get pinned to a machine
      }

      resources {
        cpu    = 250 # 250 MHz
        memory = 128 # 128MB
      }
    }
  }
}
