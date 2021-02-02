VERSION_TAG=$(shell git rev-parse --short HEAD)

.PHONY: build
build:
	docker build -t registry.webvig.com/sirvig/taylorinventory:$(VERSION_TAG) .


.PHONY: push
push: build
	docker push registry.webvig.com/sirvig/taylorinventory:$(VERSION_TAG)


.PHONY: nomad.job
nomad.job:
	hclfmt -w nomad.job.tpl
	export VERSION_TAG=$(VERSION_TAG) && envsubst < "nomad.job.tpl" > "nomad.job"

.PHONY: clean
clean:
	@rm nomad.job

.PHONY: deploy
deploy: push nomad.job
	nomad run -verbose nomad.job
	make clean

.PHONY: run
run: nomad.job
	nomad run -verbose nomad.job
	make clean

.PHONY: stop
stop:
	nomad stop taylorinventory

.PHONY: status
status:
	nomad status taylorinventory

.PHONY: logs
logs:
	nomad logs -f -job taylorinventory