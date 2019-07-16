deploy-prod:
	 ansible-playbook -v -i ansible/production ansible/deploy.yml

deploy-dev:
	 ansible-playbook -v -i ansible/dev ansible/deploy.yml

nix-deploy-prod:
	nixops deploy --include alpha-simon-codes -d plugserv

nix-deploy-dev:
	nixops deploy --include virtualbox -d plugserv

pip-compile:
	pip-compile -r requirements.in && pip-compile -r dev-requirements.in && pip install -r dev-requirements.txt
