# Using an archive sourced from git avoids unintended files in the image.
# git archive doesn't easily support reproducible builds (which are helpful for the docker cache) so it's built manually.
build-cluster:
	git ls-files plugserv/ scripts/ manage.py | tar cTf - app-archive.tar --owner=0 --group=0 --mtime=0 --sort=name && \
	docker build -t plugserv:k8s -t $$DOCKER_REPO/plugserv:k8s .

deploy-cluster: build-cluster
	docker push $$DOCKER_REPO/plugserv:k8s && \
	envsubst < kube/secrets.env.yaml | kubectl apply -f - && \
	envsubst < kube/deployment.env.yaml | kubectl apply -f - && \
	kubectl rollout restart deployment plugserv

pip-compile:
	pip-compile -r requirements.in && pip-compile -r dev-requirements.in && pip-sync dev-requirements.txt

serve:
	python manage.py runserver 0.0.0.0:8000
