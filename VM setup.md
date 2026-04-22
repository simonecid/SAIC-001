# VM setup for Claude

## Create VM

Use vmman.py to create a mini VM:

```
./vmman.py create --disk 5G --mem 4G --cpu 2 --ssh-port 6969 --arch x86_64 smn
```

start it with:

```
./vmman.py start smn
```

Connect with:

```
ssh debian@127.0.0.1 -p 6969
```

Password is `debian`.

## Install basic tooling

```
curl -fsSL https://claude.ai/install.sh | bash
sudo apt update && sudo apt install -f rsync git
```

Log out and in if needed for the environment, then start `claude` and log into your account.

You are set now!

## Sync project to VM

```
rsync -e "ssh -p 6969" -ar . debian@127.0.0.1:checker/
```

## Sync from VM

```
rsync -e "ssh -p 6969" -ar debian@127.0.0.1:checker/ . 
```