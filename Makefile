image:
	docker build -t tool-s3-sync:v1.0.0 .

show-buckets:
	docker run -it -v ${PWD}/settings:/root/.aws --rm tool-s3-sync:v1.0.0 show-buckets.sh
