.PHONY: clean

install: 
	pip install -r requirements.txt

clean:
	docker rmi -f $$(docker images -a -q)

up:
	docker compose up

build: clean up

curl:
	curl -X 'GET' 'http://localhost:8001/items/1?q=test' -H 'accept: ap2lication/json'
	echo " "
