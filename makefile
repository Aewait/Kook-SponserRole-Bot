.PHONY:ps
ps:
	ps jax | head -1 && ps jax | grep spbot.py |  grep -v grep

.PHONY:run
run:
	nohup python3.10 -u spbot.py >> ./log/nohup.log 2>&1 &