.PHONY:ps
ps:
	ps jax | head -1 && ps jax | grep spbot.py |  grep -v grep

.PHONY:bot
bot:
	nohup python3.10 -u main.py >> /dev/null 2>&1 &

.PHONY:run
run:
	nohup python3.10 -u spbot.py >> /dev/null 2>&1 &