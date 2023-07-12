# SysReptor CLI "reptor"
## Config
```
$ python3 reptor conf
Server [https://demo.sysre.pt]:
Session ID: fegk1dii32cft9rvi3qkaz0lywos0huf
Project ID: 52822d8c-947a-47bf-bc80-b7aebbc70e84
Store to config file to ~/.sysreptor/config.yaml? [y/n]: y
```

## Upload notes
```
$ echo "Upload this!" | python3 reptor note
Reading from stdin...
Note written to "Uploads".
```

```
$ echo "Upload this!" | python3 reptor note --notename "Test"
Reading from stdin...
Note written to "Test".
```

## Upload files
```
$ python3 reptor file test_data/*
```

```
$ cat img.png | python3 reptor file --filename file.png
```

## Custom modules
### nmap

```
$ cat test_data/nmap_output.txt | python3 reptor nmap
Reading from stdin...
| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
| 127.0.0.1 | 80/tcp | http | n/a |
| 127.0.0.1 | 443/tcp | ssl/http | n/a |
```

```
$ cat test_data/nmap_output.txt | python3 reptor nmap -upload
```

### sslyze
```
$ cat test_data/sslyze.txt | python3 reptor nmap
```

```
$ cat test_data/sslyze.txt | python3 reptor nmap -upload
```

## Unit Tests

```
python -m unittest discover -v -s modules
```