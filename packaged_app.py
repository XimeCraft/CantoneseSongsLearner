"""Entry point of the distributable .app built by make_dmg.sh. Not used by app.py or make_app.sh.

The code reads and writes data/... relative to the working directory, so point that at a
per-user folder. Bundled songs are copied there only if missing, so an update never overwrites
anything the user already has.
"""
import os
import shutil
import sys

USER_DIR = os.path.expanduser('~/Library/Application Support/Learning Cantonese')
LOG = os.path.expanduser('~/Library/Logs/LearningCantonese.log')


def use_user_data():
    seed = os.path.join(sys._MEIPASS, 'seed')
    for root, _, files in os.walk(seed):
        target = os.path.join(USER_DIR, os.path.relpath(root, seed))
        os.makedirs(target, exist_ok=True)
        for name in files:
            if not os.path.exists(os.path.join(target, name)):
                shutil.copy(os.path.join(root, name), target)
    os.chdir(USER_DIR)


if __name__ == '__main__':
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    sys.stdout = sys.stderr = open(LOG, 'a', buffering=1, encoding='utf-8')
    use_user_data()

    from app import App
    App().mainloop()
