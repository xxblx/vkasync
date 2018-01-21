
# Description 

Attention: vkasync is deprecated because of public api for audio is [disabled](https://vk.com/dev/audio_api).  

vkasync is open source command-line tool for creating local mirror of vk.com audios. It allows you to create local copies of users and groups audios.  

# Usage 

1. Create access token

```
./vka_sync.py token -a -l "yours vk.com login"
```

2. Download audios of vk.com users and groups

```
./vka_sync.py get -l "yours vk.com login" -u "username or userid" -p "where to save audios"
./vka_sync.py get -l "yours vk.com login" -g "groupname or groupid" -p "where to save audios"
```

You can add vkasync into /etc/crontab for example for incremental updating local copy of yours vk.com audios. 

# Additional info

See
```
./vka_sync -h
```
for details. 

- 

Oleg Kozlov (xxblx), 2016
