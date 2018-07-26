一、複製範例程式到本機

使用GitHub Desktop 

	File > Clone Repository > URL: https://github.com/jqlee/docker_samples.git

或者在命令模式執行 

	git clone https://github.com/jqlee/docker_samples.git

二、安裝
	
GitHub Desktop

	Repository > Open In PowerShell/Terminal

切換到範例工作目錄

	cd facenet-demo

安裝

	docker-compose -f install.yml up

三、 執行

	docker-compose up
