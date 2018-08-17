# dfg

Dockerfile from git

It's create docker image form git like [docker build git](https://docs.docker.com/engine/reference/commandline/build/#git-repositories) by cron

And pushed new image to registry (build with build-args)

```bash
docker run -it \
--name dfg \
--restart=always \
-d -p 8080:8080 
-e DFG_URL_CLONE='https://oauth2:GITLAB_TOKEN@gitlab.com/my/project.git#master:docker/nginx' \ For docker build from git
-e DFG_PATH_DOCKERFILE='Dockerfile' \ # Dockerfile in directory docker/nginx
-e DFG_IMAGE_TAG='registry.com/my/project:master' \
-e DFG_AUTH_BASE64='dXNlcjpwYXNz' \ # If you need auth for registry convert user:pass -> dXNlcjpwYXNz by base64 encode 
-e DFG_BUILD_ON_START \ If you need to start in first boot
-e DFG_CRON='0 * * * *' \ Default crontab
negash/dfg
```