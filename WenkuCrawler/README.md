# WenkuCrawler

* 此爬蟲適用於 `www.wenku8.net`，在極短時間內下載一整套書。
* **此爬蟲僅適用於學術用途。**

## 備註

* 此程式不適用於已經被宣告因版權問題而停止更新的小說。（如果需要下載此類型的小說，可以去原repo看一下）
* 下載內容不包括插圖。（如果需要下載插圖，可以去原repo看一下）
* 下載的檔案格式為 `.txt`。
* 預設下載路徑為 `D:\`，如果需要更改請自行更改程式碼。

## 使用方式

1. 先確認本機是否已經安裝 `python3`

2. 執行指令 `pip install scrapy`, `pip install opencc`

3. 用 `cd` 指令把位置改到 `WenkuCrawler` 的根目錄中

4. 執行指令 `scrapy crawl wenku`

5. 前往小說的主頁面，複製連結。
    > 以 [`圖書迷宮`](https://www.wenku8.net/modules/article/reader.php?aid=2511) 這本書來舉例的話，就是超連結點進去那個頁面的連結。

6. 將連結貼上至程式中

7. 等待運行

8. 完成！
