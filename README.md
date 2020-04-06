# ptt_crawler
A simple PTT crawler for articles and pushes from PTT. 
Postgresql is the database utilized in this project, there are two tables inclued: 
**article** and **push**. User are able to choose the board they want to crawl in certain time interval.

## Usage
* First, run ``` pip install -r requirement.txt ``` to install the requirements.
* Edit the database connection details in ```conn_info.py``` .
* Run ```create_table.py``` to create **article** table and **push** table in the database.
* Edit the ```BOARD``` variable in file ```ptt_crawler.py``` to crawl other boards in PTT.
* You can modify the ```start_date``` and ```end_date``` in file ```ptt_crawler.py``` to change get the articles from specific time, the date format is YYYYMMDD, for example, 6, April, 2020 is 20200406.
* Run ```ptt_crawler.py``` the articles and pushes will save into postgresql.
