腾讯云DNSPod域名使用Let's Encrypt certbot自动更新wildcard证书

1. 更新.env，包含RECORD_ID(使用腾讯云API查询想改的记录的RECORD_ID），key，domain_name（不带wildcard）
2. build image，或者本机能够直接调用certbot和对应python库
3. 运行，如果要更新会自动修改DNS，不需要则会输入1退出

自用docker-compose：
```yaml
version: '3'

services:
  certbot:
    image: zyr17/certbot
    build:
        context: ./certbot/docker
        dockerfile: Dockerfile
    restart: unless-stopped
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
      - ./certbot:/certbot
    # entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    entrypoint: "/bin/sh -c 'cd /certbot; trap exit TERM; while :; do python3 cert.py > /certbot/log.txt; sleep 2d & wait $${!}; done;'"
    # entrypoint: "sleep infinity"


```
