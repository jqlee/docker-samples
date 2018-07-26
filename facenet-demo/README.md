一、請先clone到本機

二、開啟shell程式

使用 GitHub Desktop 

	Repository > Open In PowerShell/Terminal

切換到範例工作目錄

	cd facenet-demo

三、安裝

	docker-compose -f install.yml up
	
安裝程式會下載 pretrained model 並解壓縮到 data 資料夾。僅需要執行一次。

四、執行

	docker-compose up
