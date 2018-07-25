
Docker 的 Hello world 指令

	docker run hello-world

啟動小型作業系統並進入指令列

	docker run -it --rm alpine /bin/ash

run 是一個整合命令，包含建置影像與執行容器

	docker run -it --rm python:3.6 python


Dockerfile
封裝docker指令，用於製作docker image

```
FROM python:3.6
COPY test.py /
ENTRYPOINT python
CMD test.py
```


# 搭配 Dockerfile 

建立影像
  
	docker build . -t sample00

執行

	docker run -it sample00



